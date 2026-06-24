# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Headless Keycloak authentication helper for the ONDEWO S2T client (D18).

This module implements the D18 *offline-token* flow for headless SDKs against a
**public** Keycloak client (no ``client_secret`` - Q1):

1. A one-time Resource Owner Password Credentials (ROPC) login
   (``grant_type=password``) requesting ``scope=offline_access`` yields a short-lived
   ``access_token`` and a long-lived offline ``refresh_token``.
2. The access token is refreshed automatically (``grant_type=refresh_token``) before it
   expires and attached as an ``Authorization: Bearer`` gRPC metadata header.
3. The refresh loop stops once ``token_expiration_in_s`` has elapsed since login (if set),
   after which calls fail until the caller logs in again.

No 2FA is involved - the account is a 2FA-exempt technical user (D14) and ROPC bypasses
the browser flow. There is **no** legacy ``cai-token`` / ``Authorization: Basic`` header
(dropped by D5).

The HTTP transport is the standard library (``urllib.request``) so the helper has no
extra runtime dependency and is trivially mockable in hermetic unit tests: pass a custom
``transport`` callable to ``KeycloakTokenManager`` / ``AsyncKeycloakTokenManager``.
"""

import asyncio
import json
import threading
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from urllib import (
    parse,
    request,
)
from urllib.error import HTTPError

if TYPE_CHECKING:
    from ondewo.s2t.client.client_config import ClientConfig

# A single gRPC metadata header tuple, e.g. ('authorization', 'Bearer <jwt>').
Metadata = Tuple[str, str]

# The transport contract used to talk to the Keycloak token endpoint. It receives the
# token URL and the already-url-encoded form body and must return the parsed JSON
# response as a dict. Injecting a fake implementation keeps unit tests offline.
Transport = Callable[[str, Dict[str, str]], Dict[str, Any]]

# Refresh this many seconds before the access token's own ``expires_in`` to avoid using a
# token that expires mid-call.
_REFRESH_LEEWAY_S: int = 30


class KeycloakAuthenticationError(Exception):
    """Raised when a Keycloak token request (login or refresh) fails."""


def _default_transport(token_url: str, form: Dict[str, str]) -> Dict[str, Any]:
    """POST a url-encoded form to the Keycloak token endpoint via ``urllib``.

    Args:
        token_url (str):
            Fully-qualified OpenID Connect token endpoint URL.
        form (Dict[str, str]):
            Token-request form fields (e.g. ``grant_type``, ``client_id``, ``scope``).

    Returns:
        Dict[str, Any]:
            The decoded JSON token response.

    Raises:
        KeycloakAuthenticationError:
            If the endpoint returns a non-2xx status or a non-JSON body.
    """
    data: bytes = parse.urlencode(form).encode('utf-8')
    http_request: request.Request = request.Request(
        url=token_url,
        data=data,
        method='POST',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        },
    )
    try:
        with request.urlopen(http_request) as response:  # noqa: S310 - fixed https token URL
            body: bytes = response.read()
    except HTTPError as error:
        detail: str = error.read().decode('utf-8', errors='replace')
        raise KeycloakAuthenticationError(
            f'Keycloak token request failed with HTTP {error.code}: {detail}'
        ) from error
    except OSError as error:
        raise KeycloakAuthenticationError(
            f'Keycloak token request to {token_url} failed: {error}'
        ) from error

    try:
        parsed: Dict[str, Any] = json.loads(body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError) as error:
        raise KeycloakAuthenticationError(
            f'Keycloak token endpoint returned a non-JSON response: {body!r}'
        ) from error
    return parsed


def build_token_url(keycloak_url: str, realm: str) -> str:
    """Build the OpenID Connect token endpoint URL for a realm.

    Args:
        keycloak_url (str):
            Base URL of the Keycloak server (with or without a trailing slash).
        realm (str):
            Realm name.

    Returns:
        str:
            ``<keycloak_url>/realms/<realm>/protocol/openid-connect/token``.
    """
    base: str = keycloak_url.rstrip('/')
    return f'{base}/realms/{realm}/protocol/openid-connect/token'


def bearer_metadata(access_token: str) -> Metadata:
    """Wrap an access token into the standard ``Authorization: Bearer`` metadata tuple.

    Args:
        access_token (str):
            The Keycloak access token (JWT).

    Returns:
        Metadata:
            ``('authorization', 'Bearer <access_token>')`` - the gRPC metadata key is the
            lowercase ``authorization`` header (D5).
    """
    return ('authorization', f'Bearer {access_token}')


class KeycloakTokenManager:
    """Synchronous ROPC offline-token manager with bounded auto-refresh (D18).

    Performs the one-time ``grant_type=password`` + ``scope=offline_access`` login, then
    exchanges the offline ``refresh_token`` for fresh access tokens on demand. The token
    is refreshed lazily on each ``get_metadata()`` call once it is within
    ``_REFRESH_LEEWAY_S`` of expiry, and the refresh stops permanently once
    ``token_expiration_in_s`` has elapsed since login.
    """

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
        transport: Optional[Transport] = None,
        time_source: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialise the token manager.

        Args:
            keycloak_url (str):
                Base URL of the Keycloak server.
            realm (str):
                Keycloak realm.
            client_id (str):
                Public client id (no secret, D18/Q1).
            username (str):
                Technical-user username/email.
            password (str):
                Technical-user password.
            token_expiration_in_s (Optional[int]):
                Seconds after login at which auto-refresh stops; ``None`` runs until the
                offline session expires.
            transport (Optional[Transport]):
                Token-endpoint transport; defaults to a ``urllib``-based implementation.
                Inject a fake to keep tests offline.
            time_source (Callable[[], float]):
                Monotonic clock used for expiry/deadline math; injectable for tests.
        """
        self._token_url: str = build_token_url(keycloak_url, realm)
        self._client_id: str = client_id
        self._username: str = username
        self._password: str = password
        self._token_expiration_in_s: Optional[int] = token_expiration_in_s
        self._transport: Transport = transport or _default_transport
        self._time_source: Callable[[], float] = time_source

        self._lock: threading.Lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._access_expires_at: float = 0.0
        self._refresh_deadline: Optional[float] = None

    def login(self) -> None:
        """Perform the one-time ROPC login with ``scope=offline_access``.

        Stores the access token, the offline refresh token, and (if
        ``token_expiration_in_s`` is set) the wall-clock deadline at which auto-refresh
        will stop.

        Raises:
            KeycloakAuthenticationError:
                If the token endpoint rejects the credentials or omits a token.
        """
        form: Dict[str, str] = {
            'grant_type': 'password',
            'client_id': self._client_id,
            'username': self._username,
            'password': self._password,
            'scope': 'offline_access',
        }
        with self._lock:
            now: float = self._time_source()
            self._apply_token_response(self._transport(self._token_url, form), now=now)
            if self._token_expiration_in_s is not None:
                self._refresh_deadline = now + self._token_expiration_in_s

    def _refresh(self) -> None:
        """Exchange the offline refresh token for a fresh access token.

        Must be called with ``self._lock`` held.

        Raises:
            KeycloakAuthenticationError:
                If no refresh token is available or the refresh request fails.
        """
        if not self._refresh_token:
            raise KeycloakAuthenticationError('No refresh token available; call login() first.')
        form: Dict[str, str] = {
            'grant_type': 'refresh_token',
            'client_id': self._client_id,
            'refresh_token': self._refresh_token,
        }
        self._apply_token_response(self._transport(self._token_url, form), now=self._time_source())

    def _apply_token_response(self, response: Dict[str, Any], now: float) -> None:
        """Store the access/refresh tokens from a token response.

        Must be called with ``self._lock`` held.

        Args:
            response (Dict[str, Any]):
                The decoded token response.
            now (float):
                The monotonic timestamp of the request, used as the expiry base.

        Raises:
            KeycloakAuthenticationError:
                If the response carries no ``access_token``.
        """
        access_token: Optional[str] = response.get('access_token')
        if not access_token:
            raise KeycloakAuthenticationError(f'Keycloak response contained no access_token: {response}')
        self._access_token = access_token
        # Keycloak rotates the refresh token on each grant; keep the newest one and fall
        # back to the existing offline token if a refresh response omits it.
        self._refresh_token = response.get('refresh_token') or self._refresh_token
        expires_in: int = int(response.get('expires_in', 0))
        self._access_expires_at = now + expires_in

    def _needs_refresh(self, now: float) -> bool:
        """Whether the cached access token is missing or within the refresh leeway.

        Args:
            now (float):
                Current monotonic timestamp.

        Returns:
            bool:
                ``True`` if a refresh should be attempted.
        """
        if self._access_token is None:
            return True
        return now >= (self._access_expires_at - _REFRESH_LEEWAY_S)

    def get_access_token(self) -> str:
        """Return a valid access token, refreshing it if needed and still allowed.

        Returns:
            str:
                A non-expired access token.

        Raises:
            KeycloakAuthenticationError:
                If no token has been obtained yet, the refresh deadline
                (``token_expiration_in_s``) has passed, or a refresh fails.
        """
        with self._lock:
            now: float = self._time_source()
            if self._refresh_deadline is not None and now >= self._refresh_deadline:
                raise KeycloakAuthenticationError(
                    'token_expiration_in_s elapsed; auto-refresh stopped - re-login required.'
                )
            if self._needs_refresh(now):
                self._refresh()
            # Unreachable defensive guard: _needs_refresh() returns True whenever the token is None, so a
            # refresh is always attempted, and a successful _refresh()/_apply_token_response() sets a truthy
            # access_token (otherwise it raises first); kept as a belt-and-braces invariant check.
            if self._access_token is None:  # pragma: no cover
                raise KeycloakAuthenticationError('No access token available; call login() first.')
            return self._access_token

    def get_metadata(self) -> List[Metadata]:
        """Return the gRPC call metadata carrying the current bearer token.

        Returns:
            List[Metadata]:
                ``[('authorization', 'Bearer <jwt>')]``.

        Raises:
            KeycloakAuthenticationError:
                Propagated from :meth:`get_access_token`.
        """
        return [bearer_metadata(self.get_access_token())]


class AsyncKeycloakTokenManager:
    """Asynchronous counterpart of :class:`KeycloakTokenManager`.

    Mirrors the sync manager's behaviour but guards state with an ``asyncio.Lock`` and
    runs the (potentially blocking) transport off the event loop via ``asyncio.to_thread``.
    The ``asyncio.Lock`` is created lazily on first use so the manager can be constructed
    outside a running loop without binding the lock to the wrong loop.
    """

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
        transport: Optional[Transport] = None,
        time_source: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialise the async token manager.

        Args:
            keycloak_url (str):
                Base URL of the Keycloak server.
            realm (str):
                Keycloak realm.
            client_id (str):
                Public client id (no secret, D18/Q1).
            username (str):
                Technical-user username/email.
            password (str):
                Technical-user password.
            token_expiration_in_s (Optional[int]):
                Seconds after login at which auto-refresh stops; ``None`` runs until the
                offline session expires.
            transport (Optional[Transport]):
                Token-endpoint transport; defaults to a ``urllib``-based implementation.
            time_source (Callable[[], float]):
                Monotonic clock used for expiry/deadline math; injectable for tests.
        """
        self._token_url: str = build_token_url(keycloak_url, realm)
        self._client_id: str = client_id
        self._username: str = username
        self._password: str = password
        self._token_expiration_in_s: Optional[int] = token_expiration_in_s
        self._transport: Transport = transport or _default_transport
        self._time_source: Callable[[], float] = time_source

        self._lock: Optional[asyncio.Lock] = None
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._access_expires_at: float = 0.0
        self._refresh_deadline: Optional[float] = None

    def _get_lock(self) -> asyncio.Lock:
        """Return the lazily-created ``asyncio.Lock`` bound to the running loop.

        Returns:
            asyncio.Lock:
                The lock guarding token state.
        """
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def _call_transport(self, form: Dict[str, str]) -> Dict[str, Any]:
        """Run the (blocking) transport off the event loop.

        Args:
            form (Dict[str, str]):
                The token-request form.

        Returns:
            Dict[str, Any]:
                The decoded token response.
        """
        return await asyncio.to_thread(self._transport, self._token_url, form)

    async def login(self) -> None:
        """Perform the one-time ROPC login with ``scope=offline_access``.

        Raises:
            KeycloakAuthenticationError:
                If the token endpoint rejects the credentials or omits a token.
        """
        form: Dict[str, str] = {
            'grant_type': 'password',
            'client_id': self._client_id,
            'username': self._username,
            'password': self._password,
            'scope': 'offline_access',
        }
        async with self._get_lock():
            now: float = self._time_source()
            response: Dict[str, Any] = await self._call_transport(form)
            self._apply_token_response(response, now=now)
            if self._token_expiration_in_s is not None:
                self._refresh_deadline = now + self._token_expiration_in_s

    async def _refresh(self) -> None:
        """Exchange the offline refresh token for a fresh access token.

        Must be called with the lock held.

        Raises:
            KeycloakAuthenticationError:
                If no refresh token is available or the refresh request fails.
        """
        if not self._refresh_token:
            raise KeycloakAuthenticationError('No refresh token available; call login() first.')
        form: Dict[str, str] = {
            'grant_type': 'refresh_token',
            'client_id': self._client_id,
            'refresh_token': self._refresh_token,
        }
        response: Dict[str, Any] = await self._call_transport(form)
        self._apply_token_response(response, now=self._time_source())

    def _apply_token_response(self, response: Dict[str, Any], now: float) -> None:
        """Store the access/refresh tokens from a token response.

        Must be called with the lock held.

        Args:
            response (Dict[str, Any]):
                The decoded token response.
            now (float):
                The monotonic timestamp of the request, used as the expiry base.

        Raises:
            KeycloakAuthenticationError:
                If the response carries no ``access_token``.
        """
        access_token: Optional[str] = response.get('access_token')
        if not access_token:
            raise KeycloakAuthenticationError(f'Keycloak response contained no access_token: {response}')
        self._access_token = access_token
        self._refresh_token = response.get('refresh_token') or self._refresh_token
        expires_in: int = int(response.get('expires_in', 0))
        self._access_expires_at = now + expires_in

    def _needs_refresh(self, now: float) -> bool:
        """Whether the cached access token is missing or within the refresh leeway.

        Args:
            now (float):
                Current monotonic timestamp.

        Returns:
            bool:
                ``True`` if a refresh should be attempted.
        """
        if self._access_token is None:
            return True
        return now >= (self._access_expires_at - _REFRESH_LEEWAY_S)

    async def get_access_token(self) -> str:
        """Return a valid access token, refreshing it if needed and still allowed.

        Returns:
            str:
                A non-expired access token.

        Raises:
            KeycloakAuthenticationError:
                If no token has been obtained yet, the refresh deadline
                (``token_expiration_in_s``) has passed, or a refresh fails.
        """
        async with self._get_lock():
            now: float = self._time_source()
            if self._refresh_deadline is not None and now >= self._refresh_deadline:
                raise KeycloakAuthenticationError(
                    'token_expiration_in_s elapsed; auto-refresh stopped - re-login required.'
                )
            if self._needs_refresh(now):
                await self._refresh()
            # Unreachable defensive guard: _needs_refresh() returns True whenever the token is None, so a
            # refresh is always attempted, and a successful _refresh()/_apply_token_response() sets a truthy
            # access_token (otherwise it raises first); kept as a belt-and-braces invariant check.
            if self._access_token is None:  # pragma: no cover
                raise KeycloakAuthenticationError('No access token available; call login() first.')
            return self._access_token

    async def get_metadata(self) -> List[Metadata]:
        """Return the gRPC call metadata carrying the current bearer token.

        Returns:
            List[Metadata]:
                ``[('authorization', 'Bearer <jwt>')]``.

        Raises:
            KeycloakAuthenticationError:
                Propagated from :meth:`get_access_token`.
        """
        return [bearer_metadata(await self.get_access_token())]


def token_manager_from_config(
    config: 'ClientConfig',
    transport: Optional[Transport] = None,
) -> KeycloakTokenManager:
    """Build a synchronous token manager from a Keycloak-configured ``ClientConfig``.

    Args:
        config (ClientConfig):
            A config whose ``uses_keycloak_auth`` is ``True`` (fully populated ROPC set).
        transport (Optional[Transport]):
            Optional token-endpoint transport override (used by tests).

    Returns:
        KeycloakTokenManager:
            A token manager wired to the config's credentials.

    Raises:
        ValueError:
            If the config does not opt into Keycloak authentication.
    """
    if not config.uses_keycloak_auth:
        raise ValueError('ClientConfig does not enable Keycloak authentication.')
    return KeycloakTokenManager(
        keycloak_url=config.keycloak_url,
        realm=config.realm,
        client_id=config.client_id,
        username=config.resolved_username,
        password=config.password,
        token_expiration_in_s=config.token_expiration_in_s,
        transport=transport,
    )


def async_token_manager_from_config(
    config: 'ClientConfig',
    transport: Optional[Transport] = None,
) -> AsyncKeycloakTokenManager:
    """Build an asynchronous token manager from a Keycloak-configured ``ClientConfig``.

    Args:
        config (ClientConfig):
            A config whose ``uses_keycloak_auth`` is ``True`` (fully populated ROPC set).
        transport (Optional[Transport]):
            Optional token-endpoint transport override (used by tests).

    Returns:
        AsyncKeycloakTokenManager:
            An async token manager wired to the config's credentials.

    Raises:
        ValueError:
            If the config does not opt into Keycloak authentication.
    """
    if not config.uses_keycloak_auth:
        raise ValueError('ClientConfig does not enable Keycloak authentication.')
    return AsyncKeycloakTokenManager(
        keycloak_url=config.keycloak_url,
        realm=config.realm,
        client_id=config.client_id,
        username=config.resolved_username,
        password=config.password,
        token_expiration_in_s=config.token_expiration_in_s,
        transport=transport,
    )

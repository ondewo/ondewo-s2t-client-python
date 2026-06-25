# Copyright 2021-2026 ONDEWO GmbH
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

"""Hermetic unit tests for the D18 headless Keycloak auth helper.

No network is used: a :class:`FakeTransport` stands in for the Keycloak token endpoint
and records every form it receives, so the tests can assert on the exact ROPC parameters
(``grant_type``, ``scope=offline_access``, ``client_id``, no ``client_secret``) and on the
auto-refresh and ``token_expiration_in_s`` behaviour. A controllable ``FakeClock`` drives
all expiry/deadline math deterministically.

``asyncio_mode = auto`` is set in ``pytest.ini`` so async test functions need no decorator.
"""

import io
from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

import pytest

from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.utils import keycloak as keycloak_module
from ondewo.s2t.client.utils.keycloak import (
    AsyncKeycloakTokenManager,
    KeycloakAuthenticationError,
    KeycloakTokenManager,
    _default_transport,
    async_token_manager_from_config,
    bearer_metadata,
    build_token_url,
    token_manager_from_config,
)

# ---------------------------------------------------------------------------
# Module-level constants (single source of truth for inputs AND expectations)
# ---------------------------------------------------------------------------

KEYCLOAK_URL: str = "https://keycloak.example.com/auth"
REALM: str = "ondewo-ccai-platform"
CLIENT_ID: str = "ondewo-nlu-cai-sdk-public"
USERNAME: str = "tech-user@ondewo.com"
PASSWORD: str = "s3cret-pw"
EXPECTED_TOKEN_URL: str = (
    "https://keycloak.example.com/auth/realms/ondewo-ccai-platform/protocol/openid-connect/token"
)
DEFAULT_EXPIRES_IN: int = 300


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class FakeClock:
    """A controllable monotonic clock for deterministic expiry/deadline math."""

    def __init__(self, start: float = 1000.0) -> None:
        """Initialise the clock.

        Args:
            start: Initial monotonic value.
        """
        self.now: float = start

    def __call__(self) -> float:
        """Return the current fake monotonic time.

        Returns:
            float: The current value.
        """
        return self.now

    def advance(self, seconds: float) -> None:
        """Advance the clock.

        Args:
            seconds: Seconds to add to the current time.
        """
        self.now += seconds


class FakeTransport:
    """Records token-endpoint requests and replays scripted JSON responses.

    Each call pops the next scripted response; once exhausted it raises so a test never
    silently makes more requests than it scripted for.
    """

    def __init__(self, responses: List[Dict[str, Any]]) -> None:
        """Initialise with a list of responses to return in order.

        Args:
            responses: Scripted JSON token responses, returned FIFO.
        """
        self._responses: List[Dict[str, Any]] = list(responses)
        self.calls: List[Tuple[str, Dict[str, str]]] = []

    def __call__(self, token_url: str, form: Dict[str, str]) -> Dict[str, Any]:
        """Record the request and return the next scripted response.

        Args:
            token_url: The token endpoint URL.
            form: The url-encoded-style form fields.

        Returns:
            Dict[str, Any]: The next scripted response.

        Raises:
            AssertionError: If called more times than scripted.
        """
        self.calls.append((token_url, dict(form)))
        assert self._responses, "FakeTransport received an unexpected extra request"
        return self._responses.pop(0)


def _token_response(access_token: str, refresh_token: str, expires_in: int = DEFAULT_EXPIRES_IN) -> Dict[str, Any]:
    """Build a Keycloak-shaped token response.

    Args:
        access_token: The access token value.
        refresh_token: The (offline) refresh token value.
        expires_in: Access-token lifetime in seconds.

    Returns:
        Dict[str, Any]: A token response dict.
    """
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


class TestPureHelpers:
    """Tests for the stateless module helpers."""

    def test_build_token_url(self) -> None:
        """``build_token_url`` must produce the OIDC token endpoint path."""
        assert build_token_url(KEYCLOAK_URL, REALM) == EXPECTED_TOKEN_URL

    def test_build_token_url_strips_trailing_slash(self) -> None:
        """A trailing slash on the base URL must not double the separator."""
        assert build_token_url(KEYCLOAK_URL + "/", REALM) == EXPECTED_TOKEN_URL

    def test_bearer_metadata_shape(self) -> None:
        """``bearer_metadata`` must produce the lowercase ``authorization`` tuple."""
        assert bearer_metadata("abc.def.ghi") == ("authorization", "Bearer abc.def.ghi")


# ---------------------------------------------------------------------------
# ClientConfig validation
# ---------------------------------------------------------------------------


class TestClientConfigValidation:
    """Tests for the relaxed, dual-mode ``ClientConfig.__post_init__``."""

    def test_bare_host_port_is_valid(self) -> None:
        """An unauthenticated ``ClientConfig(host, port)`` must remain valid (no http_token)."""
        config: ClientConfig = ClientConfig(host="localhost", port="50051")
        assert config.uses_keycloak_auth is False

    def test_no_http_token_field(self) -> None:
        """The legacy ``http_token`` field must be gone (D5)."""
        assert not hasattr(ClientConfig(host="localhost", port="50051"), "http_token")

    def test_full_keycloak_config_is_valid(self) -> None:
        """A complete Keycloak ROPC field set must validate and enable auth."""
        config: ClientConfig = ClientConfig(
            host="localhost",
            port="50051",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
        )
        assert config.uses_keycloak_auth is True
        assert config.resolved_username == USERNAME

    def test_user_name_alias_resolves(self) -> None:
        """The legacy ``user_name`` alias must satisfy the username requirement."""
        config: ClientConfig = ClientConfig(
            host="localhost",
            port="50051",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            user_name=USERNAME,
            password=PASSWORD,
        )
        assert config.resolved_username == USERNAME

    def test_no_client_secret_field(self) -> None:
        """The public-client design (Q1) must not introduce a ``client_secret`` field."""
        config: ClientConfig = ClientConfig(
            host="localhost",
            port="50051",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
        )
        assert not hasattr(config, "client_secret")

    @pytest.mark.parametrize(
        "missing_field",
        ["keycloak_url", "realm", "client_id", "username", "password"],
    )
    def test_partial_keycloak_config_raises(self, missing_field: str) -> None:
        """Omitting any single required field from an otherwise-complete set must raise."""
        kwargs: Dict[str, Any] = {
            "host": "localhost",
            "port": "50051",
            "keycloak_url": KEYCLOAK_URL,
            "realm": REALM,
            "client_id": CLIENT_ID,
            "username": USERNAME,
            "password": PASSWORD,
        }
        kwargs[missing_field] = ""
        with pytest.raises(ValueError):
            ClientConfig(**kwargs)

    def test_token_expiration_in_s_defaults_none(self) -> None:
        """``token_expiration_in_s`` must default to ``None`` (refresh until session end)."""
        config: ClientConfig = ClientConfig(host="localhost", port="50051")
        assert config.token_expiration_in_s is None


# ---------------------------------------------------------------------------
# Synchronous token manager
# ---------------------------------------------------------------------------


class TestSyncTokenManager:
    """Tests for :class:`KeycloakTokenManager`."""

    def _manager(
        self,
        transport: FakeTransport,
        clock: FakeClock,
        token_expiration_in_s: Any = None,
    ) -> KeycloakTokenManager:
        """Build a manager wired to the fakes.

        Args:
            transport: Scripted transport double.
            clock: Controllable clock.
            token_expiration_in_s: Optional refresh-loop bound.

        Returns:
            KeycloakTokenManager: The configured manager.
        """
        return KeycloakTokenManager(
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            token_expiration_in_s=token_expiration_in_s,
            transport=transport,
            time_source=clock,
        )

    def test_login_sends_ropc_offline_access(self) -> None:
        """Login must POST grant_type=password + scope=offline_access + the public client id."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        clock: FakeClock = FakeClock()
        manager: KeycloakTokenManager = self._manager(transport, clock)

        manager.login()

        assert len(transport.calls) == 1
        url, form = transport.calls[0]
        assert url == EXPECTED_TOKEN_URL
        assert form["grant_type"] == "password"
        assert form["scope"] == "offline_access"
        assert form["client_id"] == CLIENT_ID
        assert form["username"] == USERNAME
        assert form["password"] == PASSWORD
        assert "client_secret" not in form

    def test_metadata_carries_bearer_access_token(self) -> None:
        """``get_metadata`` must return the Authorization: Bearer tuple with the access token."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        manager: KeycloakTokenManager = self._manager(transport, FakeClock())

        manager.login()

        assert manager.get_metadata() == [("authorization", "Bearer access-1")]

    def test_no_refresh_while_token_fresh(self) -> None:
        """A still-fresh access token must be reused without a second token request."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        clock: FakeClock = FakeClock()
        manager: KeycloakTokenManager = self._manager(transport, clock)

        manager.login()
        clock.advance(10)
        token: str = manager.get_access_token()

        assert token == "access-1"
        assert len(transport.calls) == 1

    def test_auto_refresh_uses_offline_refresh_token(self) -> None:
        """Near expiry, the manager must exchange the offline refresh token for a new access token."""
        transport: FakeTransport = FakeTransport(
            [
                _token_response("access-1", "offline-1"),
                _token_response("access-2", "offline-2"),
            ]
        )
        clock: FakeClock = FakeClock()
        manager: KeycloakTokenManager = self._manager(transport, clock)

        manager.login()
        clock.advance(DEFAULT_EXPIRES_IN)  # past expiry - leeway -> refresh
        token: str = manager.get_access_token()

        assert token == "access-2"
        assert len(transport.calls) == 2
        refresh_form: Dict[str, str] = transport.calls[1][1]
        assert refresh_form["grant_type"] == "refresh_token"
        assert refresh_form["refresh_token"] == "offline-1"
        assert refresh_form["client_id"] == CLIENT_ID
        assert "client_secret" not in refresh_form

    def test_token_expiration_in_s_stops_refresh_loop(self) -> None:
        """Once ``token_expiration_in_s`` elapses, the manager must refuse to refresh."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        clock: FakeClock = FakeClock()
        manager: KeycloakTokenManager = self._manager(transport, clock, token_expiration_in_s=600)

        manager.login()
        clock.advance(601)
        with pytest.raises(KeycloakAuthenticationError):
            manager.get_access_token()
        # The deadline check must short-circuit before any refresh request is attempted.
        assert len(transport.calls) == 1

    def test_get_token_before_login_raises(self) -> None:
        """Asking for a token before login must raise rather than make a refresh call."""
        transport: FakeTransport = FakeTransport([])
        manager: KeycloakTokenManager = self._manager(transport, FakeClock())
        with pytest.raises(KeycloakAuthenticationError):
            manager.get_access_token()

    def test_login_without_access_token_raises(self) -> None:
        """A token response missing ``access_token`` must raise."""
        transport: FakeTransport = FakeTransport([{"refresh_token": "offline-1", "expires_in": 300}])
        manager: KeycloakTokenManager = self._manager(transport, FakeClock())
        with pytest.raises(KeycloakAuthenticationError):
            manager.login()

    def test_factory_from_config(self) -> None:
        """``token_manager_from_config`` must wire the config credentials into a working manager."""
        config: ClientConfig = ClientConfig(
            host="localhost",
            port="50051",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
        )
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        manager: KeycloakTokenManager = token_manager_from_config(config, transport=transport)

        manager.login()

        assert transport.calls[0][1]["scope"] == "offline_access"
        assert manager.get_metadata() == [("authorization", "Bearer access-1")]

    def test_factory_from_config_without_auth_raises(self) -> None:
        """The factory must reject a config that does not enable Keycloak auth."""
        config: ClientConfig = ClientConfig(host="localhost", port="50051")
        with pytest.raises(ValueError):
            token_manager_from_config(config)

    def test_needs_refresh_true_when_token_missing(self) -> None:
        """``_needs_refresh`` must return True whenever no access token is cached.

        This is the invariant that makes the post-refresh ``self._access_token is None`` guard in
        ``get_access_token`` unreachable (a missing token always forces a refresh first); the test
        locks it in so the ``# pragma: no cover`` on that defensive branch stays justified.
        """
        transport: FakeTransport = FakeTransport([])
        clock: FakeClock = FakeClock()
        manager: KeycloakTokenManager = self._manager(transport, clock)
        assert manager._needs_refresh(clock.now) is True


# ---------------------------------------------------------------------------
# Asynchronous token manager (mirrors the sync suite)
# ---------------------------------------------------------------------------


class TestAsyncTokenManager:
    """Tests for :class:`AsyncKeycloakTokenManager`."""

    def _manager(
        self,
        transport: FakeTransport,
        clock: FakeClock,
        token_expiration_in_s: Any = None,
    ) -> AsyncKeycloakTokenManager:
        """Build an async manager wired to the fakes.

        Args:
            transport: Scripted transport double.
            clock: Controllable clock.
            token_expiration_in_s: Optional refresh-loop bound.

        Returns:
            AsyncKeycloakTokenManager: The configured manager.
        """
        return AsyncKeycloakTokenManager(
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            token_expiration_in_s=token_expiration_in_s,
            transport=transport,
            time_source=clock,
        )

    async def test_login_sends_ropc_offline_access(self) -> None:
        """Async login must POST grant_type=password + scope=offline_access (public client)."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        manager: AsyncKeycloakTokenManager = self._manager(transport, FakeClock())

        await manager.login()

        url, form = transport.calls[0]
        assert url == EXPECTED_TOKEN_URL
        assert form["grant_type"] == "password"
        assert form["scope"] == "offline_access"
        assert form["client_id"] == CLIENT_ID
        assert "client_secret" not in form

    async def test_metadata_carries_bearer_access_token(self) -> None:
        """Async ``get_metadata`` must return the Bearer tuple with the access token."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        manager: AsyncKeycloakTokenManager = self._manager(transport, FakeClock())

        await manager.login()
        metadata: List[Tuple[str, str]] = await manager.get_metadata()

        assert metadata == [("authorization", "Bearer access-1")]

    async def test_auto_refresh_uses_offline_refresh_token(self) -> None:
        """Async manager must refresh from the offline token near expiry."""
        transport: FakeTransport = FakeTransport(
            [
                _token_response("access-1", "offline-1"),
                _token_response("access-2", "offline-2"),
            ]
        )
        clock: FakeClock = FakeClock()
        manager: AsyncKeycloakTokenManager = self._manager(transport, clock)

        await manager.login()
        clock.advance(DEFAULT_EXPIRES_IN)
        token: str = await manager.get_access_token()

        assert token == "access-2"
        assert transport.calls[1][1]["grant_type"] == "refresh_token"
        assert transport.calls[1][1]["refresh_token"] == "offline-1"

    async def test_token_expiration_in_s_stops_refresh_loop(self) -> None:
        """Async manager must stop refreshing once ``token_expiration_in_s`` elapses."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        clock: FakeClock = FakeClock()
        manager: AsyncKeycloakTokenManager = self._manager(transport, clock, token_expiration_in_s=600)

        await manager.login()
        clock.advance(601)
        with pytest.raises(KeycloakAuthenticationError):
            await manager.get_access_token()
        assert len(transport.calls) == 1

    async def test_factory_from_config(self) -> None:
        """``async_token_manager_from_config`` must produce a working async manager."""
        config: ClientConfig = ClientConfig(
            host="localhost",
            port="50051",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
        )
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        manager: AsyncKeycloakTokenManager = async_token_manager_from_config(config, transport=transport)

        await manager.login()
        metadata: List[Tuple[str, str]] = await manager.get_metadata()

        assert metadata == [("authorization", "Bearer access-1")]

    async def test_no_refresh_while_token_fresh(self) -> None:
        """A still-fresh access token must be reused without a second token request."""
        transport: FakeTransport = FakeTransport([_token_response("access-1", "offline-1")])
        clock: FakeClock = FakeClock()
        manager: AsyncKeycloakTokenManager = self._manager(transport, clock)

        await manager.login()
        clock.advance(10)
        token: str = await manager.get_access_token()

        assert token == "access-1"
        assert len(transport.calls) == 1

    async def test_get_token_before_login_raises(self) -> None:
        """Asking for a token before login must raise rather than make a refresh call."""
        transport: FakeTransport = FakeTransport([])
        manager: AsyncKeycloakTokenManager = self._manager(transport, FakeClock())
        with pytest.raises(KeycloakAuthenticationError):
            await manager.get_access_token()

    async def test_login_without_access_token_raises(self) -> None:
        """A token response missing ``access_token`` must raise."""
        transport: FakeTransport = FakeTransport([{"refresh_token": "offline-1", "expires_in": 300}])
        manager: AsyncKeycloakTokenManager = self._manager(transport, FakeClock())
        with pytest.raises(KeycloakAuthenticationError):
            await manager.login()

    async def test_refresh_keeps_previous_offline_token_when_omitted(self) -> None:
        """A refresh response that omits ``refresh_token`` must keep reusing the offline token."""
        transport: FakeTransport = FakeTransport(
            [
                _token_response("access-1", "offline-1"),
                # Refresh #1 rotates the access token but omits a new refresh token.
                {"access_token": "access-2", "expires_in": DEFAULT_EXPIRES_IN, "token_type": "Bearer"},
                _token_response("access-3", "offline-3"),
            ]
        )
        clock: FakeClock = FakeClock()
        manager: AsyncKeycloakTokenManager = self._manager(transport, clock)

        await manager.login()
        clock.advance(DEFAULT_EXPIRES_IN)
        await manager.get_access_token()  # refresh #1 -> access-2, no new offline token
        clock.advance(DEFAULT_EXPIRES_IN)
        await manager.get_access_token()  # refresh #2 -> must still present offline-1

        assert transport.calls[2][1]["refresh_token"] == "offline-1"

    async def test_factory_from_config_without_auth_raises(self) -> None:
        """The async factory must reject a config that does not enable Keycloak auth."""
        config: ClientConfig = ClientConfig(host="localhost", port="50051")
        with pytest.raises(ValueError):
            async_token_manager_from_config(config)

    async def test_needs_refresh_true_when_token_missing(self) -> None:
        """``_needs_refresh`` must return True whenever no access token is cached.

        Mirrors the sync invariant: a missing token always forces a refresh first, which is why the
        post-refresh ``self._access_token is None`` guard in ``get_access_token`` is unreachable and
        carries a ``# pragma: no cover``.
        """
        transport: FakeTransport = FakeTransport([])
        clock: FakeClock = FakeClock()
        manager: AsyncKeycloakTokenManager = self._manager(transport, clock)
        assert manager._needs_refresh(clock.now) is True


# ---------------------------------------------------------------------------
# Refresh-token-rotation edge case (sync)
# ---------------------------------------------------------------------------


class TestRefreshTokenRotation:
    """Tests for the refresh-token fall-back when a refresh response omits a new one."""

    def test_refresh_keeps_previous_offline_token_when_omitted(self) -> None:
        """A refresh response that omits ``refresh_token`` must keep reusing the offline token."""
        transport: FakeTransport = FakeTransport(
            [
                _token_response("access-1", "offline-1"),
                # Refresh #1 rotates the access token but omits a new refresh token.
                {"access_token": "access-2", "expires_in": DEFAULT_EXPIRES_IN, "token_type": "Bearer"},
                _token_response("access-3", "offline-3"),
            ]
        )
        clock: FakeClock = FakeClock()
        manager: KeycloakTokenManager = KeycloakTokenManager(
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            transport=transport,
            time_source=clock,
        )

        manager.login()
        clock.advance(DEFAULT_EXPIRES_IN)
        manager.get_access_token()  # refresh #1 -> access-2, no new offline token
        clock.advance(DEFAULT_EXPIRES_IN)
        manager.get_access_token()  # refresh #2 -> must still present offline-1

        assert transport.calls[2][1]["refresh_token"] == "offline-1"


# ---------------------------------------------------------------------------
# Default urllib transport (hermetic: urlopen is monkeypatched, no network)
# ---------------------------------------------------------------------------


class FakeHTTPResponse:
    """Context-manager stand-in for the object returned by ``urllib.request.urlopen``."""

    def __init__(self, body: bytes) -> None:
        """Initialise with the raw response body.

        Args:
            body: The bytes ``read()`` should return.
        """
        self._body: bytes = body

    def __enter__(self) -> "FakeHTTPResponse":
        """Enter the ``with`` block.

        Returns:
            FakeHTTPResponse: self.
        """
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Exit the ``with`` block (no cleanup needed)."""
        return None

    def read(self) -> bytes:
        """Return the scripted response body.

        Returns:
            bytes: The body.
        """
        return self._body


class TestDefaultTransport:
    """Tests for :func:`_default_transport`, the production ``urllib`` token transport.

    ``urllib.request.urlopen`` is monkeypatched so no socket is ever opened; the tests
    assert the request is built correctly (POST, url-encoded form, JSON accept header) and
    that every failure mode maps onto :class:`KeycloakAuthenticationError`.
    """

    def test_posts_urlencoded_form_and_parses_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A 2xx JSON body must be decoded and the request built as a url-encoded POST."""
        captured: Dict[str, Any] = {}

        def fake_urlopen(req: Any) -> FakeHTTPResponse:
            """Capture the outgoing request and return a scripted JSON body.

            Args:
                req: The ``urllib.request.Request`` built by ``_default_transport``.

            Returns:
                FakeHTTPResponse: A context-manager response with a 2xx JSON token body.
            """
            captured["url"] = req.full_url
            captured["method"] = req.get_method()
            captured["data"] = req.data
            captured["content_type"] = req.headers.get("Content-type")
            return FakeHTTPResponse(b'{"access_token": "acc", "expires_in": 300}')

        monkeypatch.setattr(keycloak_module.request, "urlopen", fake_urlopen)

        result: Dict[str, Any] = _default_transport(
            EXPECTED_TOKEN_URL,
            {"grant_type": "password", "client_id": CLIENT_ID},
        )

        assert result == {"access_token": "acc", "expires_in": 300}
        assert captured["url"] == EXPECTED_TOKEN_URL
        assert captured["method"] == "POST"
        assert captured["content_type"] == "application/x-www-form-urlencoded"
        # The form must be url-encoded into the request body, not the query string.
        assert b"grant_type=password" in captured["data"]
        assert f"client_id={CLIENT_ID}".encode("utf-8") in captured["data"]

    def test_http_error_maps_to_auth_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A non-2xx HTTP status must raise :class:`KeycloakAuthenticationError` with the code."""
        from urllib.error import HTTPError

        def fake_urlopen(req: Any) -> FakeHTTPResponse:
            """Simulate a 401 token-endpoint response.

            Args:
                req: The request built by ``_default_transport`` (unused).

            Raises:
                HTTPError: Always, with status 401 and an ``invalid_grant`` body.
            """
            raise HTTPError(
                url=EXPECTED_TOKEN_URL,
                code=401,
                msg="Unauthorized",
                hdrs=None,  # type: ignore[arg-type]
                fp=io.BytesIO(b'{"error": "invalid_grant"}'),
            )

        monkeypatch.setattr(keycloak_module.request, "urlopen", fake_urlopen)

        with pytest.raises(KeycloakAuthenticationError) as exc_info:
            _default_transport(EXPECTED_TOKEN_URL, {"grant_type": "password"})
        assert "401" in str(exc_info.value)

    def test_network_error_maps_to_auth_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An ``OSError`` (e.g. connection refused) must raise :class:`KeycloakAuthenticationError`."""

        def fake_urlopen(req: Any) -> FakeHTTPResponse:
            """Simulate a transport-level network failure.

            Args:
                req: The request built by ``_default_transport`` (unused).

            Raises:
                OSError: Always, mimicking a refused connection.
            """
            raise OSError("connection refused")

        monkeypatch.setattr(keycloak_module.request, "urlopen", fake_urlopen)

        with pytest.raises(KeycloakAuthenticationError):
            _default_transport(EXPECTED_TOKEN_URL, {"grant_type": "password"})

    def test_non_json_body_maps_to_auth_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A 2xx body that is not valid JSON must raise :class:`KeycloakAuthenticationError`."""

        def fake_urlopen(req: Any) -> FakeHTTPResponse:
            """Return a 2xx response whose body is not valid JSON.

            Args:
                req: The request built by ``_default_transport`` (unused).

            Returns:
                FakeHTTPResponse: A response wrapping a non-JSON HTML body.
            """
            return FakeHTTPResponse(b"<html>not json</html>")

        monkeypatch.setattr(keycloak_module.request, "urlopen", fake_urlopen)

        with pytest.raises(KeycloakAuthenticationError):
            _default_transport(EXPECTED_TOKEN_URL, {"grant_type": "password"})

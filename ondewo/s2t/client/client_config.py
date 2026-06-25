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

"""Client configuration for the ONDEWO S2T SDK.

Defines :class:`ClientConfig`, a frozen ``dataclass_json`` extension of
``BaseClientConfig`` that carries the connection target (``host``/``port``/``grpc_cert``)
plus the headless Keycloak authentication parameters used by the D18 offline-token flow
(see :mod:`ondewo.s2t.client.utils.keycloak`).

Authentication is optional: a bare ``ClientConfig(host=..., port=...)`` stays valid for
unauthenticated or ingress-injected-auth usage, while supplying any Keycloak field switches
on a completeness check that requires the full Resource Owner Password Credentials parameter
set (``keycloak_url``, ``realm``, ``client_id``, a username, and ``password``).
"""

from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
from ondewo.utils.base_client_config import BaseClientConfig


@dataclass_json
@dataclass(frozen=True)
class ClientConfig(BaseClientConfig):
    """ Config for ONDEWO S2T client.

    Extends ``BaseClientConfig`` (``host``/``port``/``grpc_cert``) with the headless
    Keycloak authentication parameters used by the D18 offline-token flow.

    The SDK authenticates against a **public** Keycloak client (no ``client_secret`` -
    Q1/D18) using the Resource Owner Password Credentials grant with
    ``scope=offline_access``, then auto-refreshes the short-lived access token and
    attaches it as an ``Authorization: Bearer`` gRPC metadata header. There is no
    legacy ``http_token`` / ``Authorization: Basic`` field (dropped by D5).

    Backward compatibility: every authentication field defaults to empty/``None`` so an
    unauthenticated ``ClientConfig(host=..., port=...)`` (e.g. against a plaintext
    server or an Envoy ingress that injects auth) remains valid. When any Keycloak
    field is set, the full ROPC set (``keycloak_url``, ``realm``, ``client_id``,
    a username, and ``password``) is required.

    Attributes:
        keycloak_url (str):
            Base URL of the Keycloak server, e.g. ``https://keycloak.example.com/auth``.
        realm (str):
            Keycloak realm that owns the SDK client and the technical user.
        client_id (str):
            Public Keycloak client id used for the ROPC grant (no secret, D18/Q1),
            e.g. ``ondewo-nlu-cai-sdk-public``.
        username (str):
            Username/email of the (2FA-exempt) technical user authenticating via ROPC.
        user_name (str):
            Backward-compatible alias for ``username``; if ``username`` is empty this
            value is used instead.
        password (str):
            Password of the technical user.
        token_expiration_in_s (Optional[int]):
            Upper bound, in seconds since login, on how long the background auto-refresh
            runs. Once elapsed the refresh loop stops and calls fail until re-login.
            ``None`` (default) means refresh until the offline session itself expires.
    """
    keycloak_url: str = ''
    realm: str = ''
    client_id: str = ''
    username: str = ''
    user_name: str = ''
    password: str = ''
    token_expiration_in_s: Optional[int] = None

    def __post_init__(self) -> None:
        """ Validate the Keycloak authentication field set.

        Calls ``BaseClientConfig.__post_init__`` (which encodes ``grpc_cert``), then -
        only if the config opts into Keycloak auth (any Keycloak/credential field set) -
        requires the complete ROPC parameter set. A bare ``host``/``port`` config stays
        valid so unauthenticated usage keeps working.

        Raises:
            ValueError:
                If Keycloak authentication is partially configured (some but not all of
                ``keycloak_url``, ``realm``, ``client_id``, a username and ``password``).
        """
        super(ClientConfig, self).__post_init__()

        if not self.uses_keycloak_auth:
            return

        missing: list[str] = []
        if not self.keycloak_url:
            missing.append('keycloak_url')
        if not self.realm:
            missing.append('realm')
        if not self.client_id:
            missing.append('client_id')
        if not self.resolved_username:
            missing.append('username')
        if not self.password:
            missing.append('password')
        if missing:
            raise ValueError(
                'Incomplete Keycloak authentication config in '
                f'{self.__class__.__name__}: missing {missing}. '
                'Provide keycloak_url, realm, client_id, username and password together, '
                'or none of them for an unauthenticated client.'
            )

    @property
    def resolved_username(self) -> str:
        """ Return the effective username, preferring ``username`` over ``user_name``.

        Returns:
            str:
                ``username`` if set, otherwise the ``user_name`` alias, otherwise ``''``.
        """
        return self.username or self.user_name

    @property
    def uses_keycloak_auth(self) -> bool:
        """ Whether this config opts into the Keycloak ROPC offline-token flow.

        Returns:
            bool:
                ``True`` if any Keycloak/credential field is non-empty, which switches
                on the ``__post_init__`` completeness check and the token manager.
        """
        return bool(
            self.keycloak_url
            or self.realm
            or self.client_id
            or self.resolved_username
            or self.password
        )

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
"""Services base that injects the Keycloak bearer token into every S2T gRPC call.

The generated service wrappers (``ondewo/s2t/client/services/*.py``) subclass
:class:`ServicesInterface` and forward :attr:`ServicesInterface.metadata` to every stub
call. When the :class:`~ondewo.s2t.client.client_config.ClientConfig` opts into the D18
headless offline-token flow, that metadata carries a freshly auto-refreshed
``Authorization: Bearer`` header; otherwise it is empty and calls travel unauthenticated
(e.g. against a plaintext server or an Envoy ingress that injects auth).
"""

from abc import ABC
from typing import (
    Any,
    List,
    Optional,
    Set,
    Tuple,
)

from ondewo.utils.base_services_interface import BaseServicesInterface

from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.utils.keycloak import (
    KeycloakTokenProvider,
    get_keycloak_token_provider,
)


class ServicesInterface(BaseServicesInterface, ABC):
    """gRPC services base that attaches the Keycloak bearer token to every call.

    Extends ``BaseServicesInterface`` (which builds the gRPC channel) with a
    :class:`~ondewo.s2t.client.utils.keycloak.KeycloakTokenProvider` that is shared per
    :class:`ClientConfig`, so the one-time ROPC offline-token login runs once for all of a
    client's service stubs. The provider is created only when the config opts into Keycloak
    headless auth (D18).
    """

    def __init__(
        self,
        config: ClientConfig,
        use_secure_channel: bool,
        options: Optional[Set[Tuple[str, Any]]] = None,
    ) -> None:
        """Build the gRPC channel and, if configured, the shared Keycloak token provider.

        Args:
            config (ClientConfig):
                Connection target plus the optional Keycloak headless-auth fields.
            use_secure_channel (bool):
                Whether to use a secure (TLS) gRPC channel.
            options (Optional[Set[Tuple[str, Any]]]):
                Additional gRPC channel options.
        """
        super(ServicesInterface, self).__init__(
            config=config,
            use_secure_channel=use_secure_channel,
            options=options,
        )
        # When Keycloak headless auth (D18) is configured, every call carries a freshly
        # auto-refreshed `Authorization: Bearer` token; the provider is shared per config so
        # the offline-token ROPC login happens once for all services on the client.
        self._keycloak_provider: Optional[KeycloakTokenProvider] = (
            get_keycloak_token_provider(config) if config.uses_keycloak_auth else None
        )

    @property
    def metadata(self) -> List[Tuple[str, str]]:
        """The gRPC metadata attached to every outgoing call.

        With Keycloak auth this rebuilds (and auto-refreshes) the ``Authorization: Bearer``
        token on each access; otherwise it returns an empty list so the call travels
        unauthenticated.

        Returns:
            List[Tuple[str, str]]:
                The metadata tuples for the next gRPC call, or ``[]`` when Keycloak auth is
                not configured.
        """
        if self._keycloak_provider is not None:
            return self._keycloak_provider.bearer_metadata()
        return []

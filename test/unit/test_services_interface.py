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
"""Unit tests for the S2T services-interface Keycloak-bearer injection seam.

No network is touched: ``get_keycloak_token_provider`` is patched so the real ROPC
offline-token login never runs, and the gRPC channel factories are patched so no real
channel is opened. The tests exercise both branches of the ``metadata`` property on the
sync :class:`ServicesInterface` and the async :class:`AsyncServicesInterface`:

* provider set (Keycloak auth configured) -> the auto-refreshed ``Authorization: Bearer``
  metadata from :meth:`KeycloakTokenProvider.bearer_metadata`;
* no provider (no Keycloak auth) -> an empty list.
"""
from typing import (
    Any,
    List,
    Tuple,
)
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from ondewo.s2t.client.async_services_interface import AsyncServicesInterface
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services_interface import ServicesInterface

# Bound exactly once so a refactor that changes only an input or only an expectation cannot
# silently make a test tautological.
KEYCLOAK_URL: str = 'https://kc.example.com/auth'
REALM: str = 'ondewo-ccai-platform'
CLIENT_ID: str = 'ondewo-nlu-cai-sdk-public'
USERNAME: str = 'tech-user@example.com'
PASSWORD: str = 's3cr3t'

# The canonical `Authorization: Bearer` metadata the provider would return.
EXPECTED_BEARER_METADATA: List[Tuple[str, str]] = [('authorization', 'Bearer test-access-token')]

# Patch targets for the shared-provider factory, resolved in each interface module's namespace.
_SYNC_FACTORY: str = 'ondewo.s2t.client.services_interface.get_keycloak_token_provider'
_ASYNC_FACTORY: str = 'ondewo.s2t.client.async_services_interface.get_keycloak_token_provider'

# Patch targets for the gRPC channel factories so construction opens no real channel.
_GRPC_INSECURE: str = 'grpc.insecure_channel'
_GRPC_AIO_INSECURE: str = 'grpc.aio.insecure_channel'


class _ConcreteSyncInterface(ServicesInterface):
    """Concrete :class:`ServicesInterface` implementing the abstract ``stub`` property."""

    @property
    def stub(self) -> Any:
        """Return a throwaway stub; never exercised by the metadata tests."""
        return MagicMock()


class _ConcreteAsyncInterface(AsyncServicesInterface):
    """Concrete :class:`AsyncServicesInterface` implementing the abstract ``stub`` property."""

    @property
    def stub(self) -> Any:
        """Return a throwaway stub; never exercised by the metadata tests."""
        return MagicMock()


@pytest.fixture
def config_without_keycloak() -> ClientConfig:
    """A bare, unauthenticated config (no Keycloak fields set).

    Returns:
        ClientConfig: A config pointing to ``localhost:50051`` with no auth.
    """
    return ClientConfig(host='localhost', port='50051')


@pytest.fixture
def config_with_keycloak() -> ClientConfig:
    """A config carrying the complete Keycloak ROPC field set.

    Returns:
        ClientConfig: A config that opts into the D18 headless offline-token flow.
    """
    return ClientConfig(
        host='localhost',
        port='50051',
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
    )


def test_sync_metadata_is_empty_without_keycloak(config_without_keycloak: ClientConfig) -> None:
    """Sync ``metadata`` is an empty list when Keycloak auth is not configured."""
    with patch(_GRPC_INSECURE):
        interface: _ConcreteSyncInterface = _ConcreteSyncInterface(
            config=config_without_keycloak,
            use_secure_channel=False,
        )
    assert interface.metadata == []


def test_sync_metadata_is_bearer_with_keycloak(config_with_keycloak: ClientConfig) -> None:
    """Sync ``metadata`` returns the provider's bearer metadata when Keycloak auth is set."""
    provider: MagicMock = MagicMock()
    provider.bearer_metadata.return_value = EXPECTED_BEARER_METADATA
    with patch(_GRPC_INSECURE), patch(_SYNC_FACTORY, return_value=provider) as factory:
        interface: _ConcreteSyncInterface = _ConcreteSyncInterface(
            config=config_with_keycloak,
            use_secure_channel=False,
        )
    factory.assert_called_once_with(config_with_keycloak)
    assert interface.metadata == EXPECTED_BEARER_METADATA
    provider.bearer_metadata.assert_called_once_with()


def test_async_metadata_is_empty_without_keycloak(config_without_keycloak: ClientConfig) -> None:
    """Async ``metadata`` is an empty list when Keycloak auth is not configured."""
    with patch(_GRPC_AIO_INSECURE):
        interface: _ConcreteAsyncInterface = _ConcreteAsyncInterface(
            config=config_without_keycloak,
            use_secure_channel=False,
        )
    assert interface.metadata == []


def test_async_metadata_is_bearer_with_keycloak(config_with_keycloak: ClientConfig) -> None:
    """Async ``metadata`` returns the provider's bearer metadata when Keycloak auth is set."""
    provider: MagicMock = MagicMock()
    provider.bearer_metadata.return_value = EXPECTED_BEARER_METADATA
    with patch(_GRPC_AIO_INSECURE), patch(_ASYNC_FACTORY, return_value=provider) as factory:
        interface: _ConcreteAsyncInterface = _ConcreteAsyncInterface(
            config=config_with_keycloak,
            use_secure_channel=False,
        )
    factory.assert_called_once_with(config_with_keycloak)
    assert interface.metadata == EXPECTED_BEARER_METADATA
    provider.bearer_metadata.assert_called_once_with()

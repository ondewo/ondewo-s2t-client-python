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
from typing import (
    Any,
    Optional,
    Set,
    Tuple,
)

from ondewo.utils.async_base_client import AsyncBaseClient

from ondewo.s2t.client.async_services_container import AsyncServicesContainer
from ondewo.s2t.client.client_config import BaseClientConfig
from ondewo.s2t.client.services.async_speech_to_text import Speech2Text


class AsyncClient(AsyncBaseClient):
    """
    The core asynchronous Python client for interacting with ONDEWO s2t services.
    """

    def _initialize_services(
        self,
        config: BaseClientConfig,
        use_secure_channel: bool,
        options: Optional[Set[Tuple[str, Any]]] = None,
    ) -> None:
        """
        Initialize the asynchronous service clients, login with the current config,
        and set up the services in self.services.

        Args:
            config (ClientConfig): Configuration for the client.
            use_secure_channel (bool): Whether to use a secure gRPC channel.
            options (Optional[Set[Tuple[str, Any]]]): Additional options for the gRPC channel.
        """
        self.services: AsyncServicesContainer = AsyncServicesContainer(
            speech_to_text=Speech2Text(config=config, use_secure_channel=use_secure_channel, options=options)
        )

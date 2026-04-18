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

"""Unit tests for the asynchronous :class:`~ondewo.s2t.client.async_client.AsyncClient`
and async :class:`~ondewo.s2t.client.services.async_speech_to_text.Speech2Text` service.

All gRPC backend calls are mocked; no real server connection is required.
Test scenarios mirror those in ``test_sync_client.py`` but use ``async``/``await``
patterns throughout.  ``asyncio_mode = auto`` is set in ``pytest.ini`` so no
``@pytest.mark.asyncio`` decorator is needed on individual tests.

Patching strategy
-----------------
* ``grpc.aio.insecure_channel`` is patched to prevent any real network activity.
* ``Speech2TextStub`` is patched at the async service-module level.  Because the
  ``stub`` property is non-cached, the patch must remain active for the full test
  body, which the ``patch_grpc_and_stub`` autouse fixture guarantees.
* Every RPC attribute on the stub mock is an :class:`~unittest.mock.AsyncMock`
  so that ``await self.stub.MethodName(...)`` succeeds.
"""

from typing import (
    Any,
    AsyncIterator,
    Iterator,
    List,
    Set,
    Tuple,
)
from unittest.mock import AsyncMock, MagicMock, patch

import grpc
import pytest
from google.protobuf.empty_pb2 import Empty

from ondewo.s2t.client.async_client import AsyncClient
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.async_speech_to_text import Speech2Text as AsyncSpeech2Text
from ondewo.s2t.speech_to_text_pb2 import (
    AddDataToUserLanguageModelRequest,
    CreateUserLanguageModelRequest,
    Decoding,
    DeleteUserLanguageModelRequest,
    ListS2tDomainsRequest,
    ListS2tDomainsResponse,
    ListS2tLanguageModelsRequest,
    ListS2tLanguageModelsResponse,
    ListS2tLanguagesRequest,
    ListS2tLanguagesResponse,
    ListS2tNormalizationPipelinesRequest,
    ListS2tNormalizationPipelinesResponse,
    ListS2tPipelinesRequest,
    ListS2tPipelinesResponse,
    S2tGetServiceInfoResponse,
    S2tPipelineId,
    Speech2TextConfig,
    TrainUserLanguageModelRequest,
    TranscribeFileRequest,
    TranscribeFileResponse,
    TranscribeRequestConfig,
    TranscribeStreamRequest,
    TranscribeStreamResponse,
)

# ---------------------------------------------------------------------------
# Module-level patch targets
# ---------------------------------------------------------------------------

_STUB_PATH: str = "ondewo.s2t.client.services.async_speech_to_text.Speech2TextStub"
"""Fully-qualified import path of the stub class inside the async service module."""

_GRPC_AIO_INSECURE: str = "grpc.aio.insecure_channel"
"""Patch target for the async gRPC insecure channel factory."""

_CLIENT_SPEECH2TEXT: str = "ondewo.s2t.client.async_client.Speech2Text"
"""Patch target for the async Speech2Text class as imported by the AsyncClient module."""


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _make_async_stub() -> MagicMock:
    """Build a :class:`~unittest.mock.MagicMock` where every RPC method is an :class:`~unittest.mock.AsyncMock`.

    The async ``Speech2Text`` service calls ``await self.stub.MethodName(...)`` for each
    RPC.  Plain ``MagicMock`` attributes are not awaitable, so each attribute is
    explicitly replaced with an ``AsyncMock``.

    Returns:
        MagicMock: Stub mock with all sixteen RPC methods set to ``AsyncMock()``.
    """
    stub: MagicMock = MagicMock()
    for method_name in (
        "TranscribeFile",
        "TranscribeStream",
        "GetS2tPipeline",
        "CreateS2tPipeline",
        "DeleteS2tPipeline",
        "UpdateS2tPipeline",
        "ListS2tPipelines",
        "ListS2tLanguages",
        "ListS2tDomains",
        "GetServiceInfo",
        "ListS2tLanguageModels",
        "CreateUserLanguageModel",
        "DeleteUserLanguageModel",
        "AddDataToUserLanguageModel",
        "TrainUserLanguageModel",
        "ListS2tNormalizationPipelines",
    ):
        setattr(stub, method_name, AsyncMock())
    return stub


async def _async_gen(*items: TranscribeStreamRequest) -> AsyncIterator[TranscribeStreamRequest]:
    """Yield each item in *items* as an async generator for use in streaming tests.

    Args:
        *items: One or more :class:`~ondewo.s2t.speech_to_text_pb2.TranscribeStreamRequest`
            instances to yield.

    Yields:
        TranscribeStreamRequest: Each item in order.
    """
    for item in items:
        yield item


# ---------------------------------------------------------------------------
# AsyncClient initialisation
# ---------------------------------------------------------------------------


class TestAsyncClientInitialization:
    """Tests that :class:`~ondewo.s2t.client.async_client.AsyncClient` wires up its container."""

    @pytest.fixture
    def mock_async_speech2text(self) -> MagicMock:
        """Provide a :class:`~unittest.mock.MagicMock` spec'd to :class:`AsyncSpeech2Text`.

        Returns:
            MagicMock: Mock instance with the same interface as the real async service.
        """
        return MagicMock(spec=AsyncSpeech2Text)

    @pytest.fixture
    def async_client(
        self,
        client_config: ClientConfig,
        mock_async_speech2text: MagicMock,
    ) -> AsyncClient:
        """Construct an :class:`~ondewo.s2t.client.async_client.AsyncClient` with gRPC patched out.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
            mock_async_speech2text: Pre-built mock injected in place of the real async service.

        Returns:
            AsyncClient: Fully initialised async client whose
                ``services.speech_to_text`` is the mock.
        """
        with patch(_CLIENT_SPEECH2TEXT, return_value=mock_async_speech2text):
            with patch(_GRPC_AIO_INSECURE):
                return AsyncClient(config=client_config, use_secure_channel=False)

    def test_services_container_is_created(self, async_client: AsyncClient) -> None:
        """Services container must be present after construction.

        Args:
            async_client: Patched async client under test.
        """
        assert async_client.services is not None

    def test_speech2text_service_is_present(self, async_client: AsyncClient) -> None:
        """``services.speech_to_text`` attribute must be set.

        Args:
            async_client: Patched async client under test.
        """
        assert async_client.services.speech_to_text is not None

    def test_speech2text_service_is_the_injected_mock(
        self,
        async_client: AsyncClient,
        mock_async_speech2text: MagicMock,
    ) -> None:
        """The service stored on the container must be exactly the injected mock.

        Args:
            async_client: Patched async client under test.
            mock_async_speech2text: The mock injected during construction.
        """
        assert async_client.services.speech_to_text is mock_async_speech2text

    def test_invalid_config_raises(self) -> None:
        """Passing a non-``BaseClientConfig`` value must raise ``ValueError`` or ``TypeError``."""
        with patch(_GRPC_AIO_INSECURE):
            with pytest.raises((ValueError, TypeError)):
                AsyncClient(config="not-a-config", use_secure_channel=False)  # type: ignore[arg-type]


class TestAsyncClientWithGrpcOptions:
    """Tests that :class:`~ondewo.s2t.client.async_client.AsyncClient` accepts gRPC channel options."""

    def test_async_client_accepts_custom_grpc_options(self, client_config: ClientConfig) -> None:
        """AsyncClient must be constructable with a non-empty ``options`` set.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
        """
        options: Set[Tuple[str, Any]] = {
            ("grpc.max_send_message_length", 1024 * 1024),
            ("grpc.max_receive_message_length", 1024 * 1024),
            ("grpc.enable_retries", 1),
        }
        with patch(_CLIENT_SPEECH2TEXT):
            with patch(_GRPC_AIO_INSECURE):
                client: AsyncClient = AsyncClient(
                    config=client_config,
                    use_secure_channel=False,
                    options=options,
                )
        assert client.services is not None

    def test_speech2text_accessible_via_services(self, client_config: ClientConfig) -> None:
        """``async_client.services.speech_to_text`` must be non-None after default construction.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
        """
        with patch(_CLIENT_SPEECH2TEXT):
            with patch(_GRPC_AIO_INSECURE):
                client: AsyncClient = AsyncClient(config=client_config, use_secure_channel=False)
        assert client.services.speech_to_text is not None


# ---------------------------------------------------------------------------
# Async Speech2Text service — stub delegation tests
# ---------------------------------------------------------------------------


class TestAsyncSpeech2TextServiceDelegation:
    """Verifies that every async :class:`AsyncSpeech2Text` method delegates to the correct stub RPC."""

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide an async-compatible stub mock via :func:`_make_async_stub`.

        Returns:
            MagicMock: Stub mock with all RPC methods set to ``AsyncMock()``.
        """
        return _make_async_stub()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC aio channel and stub patched for each delegation test.

        Args:
            mock_stub: Async stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with both patches active.
        """
        with patch(_GRPC_AIO_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> AsyncSpeech2Text:
        """Construct the async service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            AsyncSpeech2Text: Service instance ready for delegation testing.
        """
        return AsyncSpeech2Text(config=client_config, use_secure_channel=False)

    async def test_transcribe_file(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``transcribe_file`` must await ``stub.TranscribeFile`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: TranscribeFileRequest = TranscribeFileRequest()
        expected: TranscribeFileResponse = TranscribeFileResponse()
        mock_stub.TranscribeFile.return_value = expected
        assert await service.transcribe_file(request) is expected
        mock_stub.TranscribeFile.assert_called_once_with(request)

    async def test_transcribe_stream(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``transcribe_stream`` must await ``stub.TranscribeStream`` with the async iterator.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request_iter: AsyncIterator[TranscribeStreamRequest] = _async_gen(TranscribeStreamRequest())
        expected: AsyncIterator[TranscribeStreamResponse] = MagicMock()  # type: ignore[assignment]
        mock_stub.TranscribeStream.return_value = expected
        result: AsyncIterator[TranscribeStreamResponse] = await service.transcribe_stream(request_iter)
        assert result is expected
        mock_stub.TranscribeStream.assert_called_once()

    async def test_get_s2t_pipeline(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``get_s2t_pipeline`` must await ``stub.GetS2tPipeline`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: S2tPipelineId = S2tPipelineId()
        expected: Speech2TextConfig = Speech2TextConfig()
        mock_stub.GetS2tPipeline.return_value = expected
        assert await service.get_s2t_pipeline(request) is expected
        mock_stub.GetS2tPipeline.assert_called_once_with(request)

    async def test_create_s2t_pipeline(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``create_s2t_pipeline`` must await ``stub.CreateS2tPipeline`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: Speech2TextConfig = Speech2TextConfig()
        expected: S2tPipelineId = S2tPipelineId()
        mock_stub.CreateS2tPipeline.return_value = expected
        assert await service.create_s2t_pipeline(request) is expected
        mock_stub.CreateS2tPipeline.assert_called_once_with(request)

    async def test_delete_s2t_pipeline(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``delete_s2t_pipeline`` must await ``stub.DeleteS2tPipeline`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: S2tPipelineId = S2tPipelineId()
        expected: Empty = Empty()
        mock_stub.DeleteS2tPipeline.return_value = expected
        assert await service.delete_s2t_pipeline(request) is expected
        mock_stub.DeleteS2tPipeline.assert_called_once_with(request)

    async def test_update_s2t_pipeline(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``update_s2t_pipeline`` must await ``stub.UpdateS2tPipeline`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: Speech2TextConfig = Speech2TextConfig()
        expected: Empty = Empty()
        mock_stub.UpdateS2tPipeline.return_value = expected
        assert await service.update_s2t_pipeline(request) is expected
        mock_stub.UpdateS2tPipeline.assert_called_once_with(request)

    async def test_list_s2t_pipelines(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_pipelines`` must await ``stub.ListS2tPipelines`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: ListS2tPipelinesRequest = ListS2tPipelinesRequest()
        expected: ListS2tPipelinesResponse = ListS2tPipelinesResponse()
        mock_stub.ListS2tPipelines.return_value = expected
        assert await service.list_s2t_pipelines(request) is expected
        mock_stub.ListS2tPipelines.assert_called_once_with(request)

    async def test_list_s2t_languages(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_languages`` must await ``stub.ListS2tLanguages`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: ListS2tLanguagesRequest = ListS2tLanguagesRequest()
        expected: ListS2tLanguagesResponse = ListS2tLanguagesResponse()
        mock_stub.ListS2tLanguages.return_value = expected
        assert await service.list_s2t_languages(request) is expected
        mock_stub.ListS2tLanguages.assert_called_once_with(request)

    async def test_list_s2t_domains(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_domains`` must await ``stub.ListS2tDomains`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: ListS2tDomainsRequest = ListS2tDomainsRequest()
        expected: ListS2tDomainsResponse = ListS2tDomainsResponse()
        mock_stub.ListS2tDomains.return_value = expected
        assert await service.list_s2t_domains(request) is expected
        mock_stub.ListS2tDomains.assert_called_once_with(request)

    async def test_get_service_info(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``get_service_info`` must await ``stub.GetServiceInfo`` with the given request.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: Empty = Empty()
        expected: S2tGetServiceInfoResponse = S2tGetServiceInfoResponse()
        mock_stub.GetServiceInfo.return_value = expected
        assert await service.get_service_info(request) is expected
        mock_stub.GetServiceInfo.assert_called_once_with(request)

    async def test_list_s2t_language_models(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_language_models`` must await ``stub.ListS2tLanguageModels``.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: ListS2tLanguageModelsRequest = ListS2tLanguageModelsRequest()
        expected: ListS2tLanguageModelsResponse = ListS2tLanguageModelsResponse()
        mock_stub.ListS2tLanguageModels.return_value = expected
        assert await service.list_s2t_language_models(request) is expected
        mock_stub.ListS2tLanguageModels.assert_called_once_with(request)

    async def test_create_user_language_model(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``create_user_language_model`` must await ``stub.CreateUserLanguageModel``.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: CreateUserLanguageModelRequest = CreateUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.CreateUserLanguageModel.return_value = expected
        assert await service.create_user_language_model(request) is expected
        mock_stub.CreateUserLanguageModel.assert_called_once_with(request)

    async def test_delete_user_language_model(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``delete_user_language_model`` must await ``stub.DeleteUserLanguageModel``.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: DeleteUserLanguageModelRequest = DeleteUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.DeleteUserLanguageModel.return_value = expected
        assert await service.delete_user_language_model(request) is expected
        mock_stub.DeleteUserLanguageModel.assert_called_once_with(request)

    async def test_add_data_to_user_language_model(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """``add_data_to_user_language_model`` must await ``stub.AddDataToUserLanguageModel``.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: AddDataToUserLanguageModelRequest = AddDataToUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.AddDataToUserLanguageModel.return_value = expected
        assert await service.add_data_to_user_language_model(request) is expected
        mock_stub.AddDataToUserLanguageModel.assert_called_once_with(request)

    async def test_train_user_language_model(self, service: AsyncSpeech2Text, mock_stub: MagicMock) -> None:
        """``train_user_language_model`` must await ``stub.TrainUserLanguageModel``.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: TrainUserLanguageModelRequest = TrainUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.TrainUserLanguageModel.return_value = expected
        assert await service.train_user_language_model(request) is expected
        mock_stub.TrainUserLanguageModel.assert_called_once_with(request)

    async def test_list_s2t_normalization_pipelines(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """``list_s2t_normalization_pipelines`` must await ``stub.ListS2tNormalizationPipelines``.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
        """
        request: ListS2tNormalizationPipelinesRequest = ListS2tNormalizationPipelinesRequest()
        expected: ListS2tNormalizationPipelinesResponse = ListS2tNormalizationPipelinesResponse()
        mock_stub.ListS2tNormalizationPipelines.return_value = expected
        assert await service.list_s2t_normalization_pipelines(request) is expected
        mock_stub.ListS2tNormalizationPipelines.assert_called_once_with(request)


# ---------------------------------------------------------------------------
# Realistic file-transcription scenarios (async)
# ---------------------------------------------------------------------------


class TestAsyncTranscribeFileScenarios:
    """Async equivalents of the file transcription scenarios from ``file_transcription_example.py``."""

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide an async-compatible stub mock for transcription scenario tests.

        Returns:
            MagicMock: Async stub mock via :func:`_make_async_stub`.
        """
        return _make_async_stub()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC aio channel and stub patched for each scenario test.

        Args:
            mock_stub: Async stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with patches active.
        """
        with patch(_GRPC_AIO_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> AsyncSpeech2Text:
        """Construct the async service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            AsyncSpeech2Text: Service instance ready for scenario testing.
        """
        return AsyncSpeech2Text(config=client_config, use_secure_channel=False)

    async def test_transcribe_file_with_audio_and_pipeline_id(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
        fake_pipeline_id: str,
    ) -> None:
        """Async transcription with raw PCM bytes and ``BEAM_SEARCH_WITH_LM`` decoding.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
            fake_audio_bytes: 32 KB of synthetic PCM data from conftest.
            fake_pipeline_id: Stable fake pipeline UUID from conftest.
        """
        request: TranscribeFileRequest = TranscribeFileRequest(
            audio_file=fake_audio_bytes,
            config=TranscribeRequestConfig(
                s2t_pipeline_id=fake_pipeline_id,
                decoding=Decoding.BEAM_SEARCH_WITH_LM,
            ),
        )
        expected: TranscribeFileResponse = TranscribeFileResponse()
        mock_stub.TranscribeFile.return_value = expected

        result: TranscribeFileResponse = await service.transcribe_file(request)

        mock_stub.TranscribeFile.assert_called_once_with(request)
        assert result is expected

    async def test_list_pipelines_then_use_first_pipeline(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
    ) -> None:
        """Async equivalent of the canonical list-then-transcribe example flow.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock programmed to return one pipeline config.
            fake_audio_bytes: Synthetic PCM payload for the transcription request.
        """
        first_pipeline: Speech2TextConfig = Speech2TextConfig(id="async-pipeline-001")
        mock_stub.ListS2tPipelines.return_value = ListS2tPipelinesResponse(
            pipeline_configs=[first_pipeline]
        )
        pipelines_result: ListS2tPipelinesResponse = await service.list_s2t_pipelines(
            ListS2tPipelinesRequest()
        )
        pipeline: Speech2TextConfig = pipelines_result.pipeline_configs[0]

        request: TranscribeFileRequest = TranscribeFileRequest(
            audio_file=fake_audio_bytes,
            config=TranscribeRequestConfig(s2t_pipeline_id=pipeline.id),
        )
        mock_stub.TranscribeFile.return_value = TranscribeFileResponse()
        await service.transcribe_file(request)

        mock_stub.ListS2tPipelines.assert_called_once()
        mock_stub.TranscribeFile.assert_called_once_with(request)
        assert pipeline.id == "async-pipeline-001"

    async def test_transcribe_file_response_exposes_transcriptions(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
        fake_pipeline_id: str,
    ) -> None:
        """Async response ``.transcriptions`` must be iterable as shown in the example.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock returning a response with one transcription.
            fake_audio_bytes: Synthetic PCM payload.
            fake_pipeline_id: Stable fake pipeline UUID.
        """
        mock_transcription: MagicMock = MagicMock()
        mock_transcription.transcription = "async hello world"
        mock_response: MagicMock = MagicMock(spec=TranscribeFileResponse)
        mock_response.transcriptions = [mock_transcription]
        mock_stub.TranscribeFile.return_value = mock_response

        request: TranscribeFileRequest = TranscribeFileRequest(
            audio_file=fake_audio_bytes,
            config=TranscribeRequestConfig(s2t_pipeline_id=fake_pipeline_id),
        )
        response: TranscribeFileResponse = await service.transcribe_file(request)

        texts: List[str] = [t.transcription for t in response.transcriptions]
        assert texts == ["async hello world"]


# ---------------------------------------------------------------------------
# Realistic streaming scenarios (async)
# ---------------------------------------------------------------------------


class TestAsyncTranscribeStreamScenarios:
    """Async streaming scenarios inspired by ``examples/streaming_example.py``."""

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide an async-compatible stub mock for streaming scenario tests.

        Returns:
            MagicMock: Async stub mock via :func:`_make_async_stub`.
        """
        return _make_async_stub()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC aio channel and stub patched for each streaming test.

        Args:
            mock_stub: Async stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with patches active.
        """
        with patch(_GRPC_AIO_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> AsyncSpeech2Text:
        """Construct the async service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            AsyncSpeech2Text: Service instance ready for streaming testing.
        """
        return AsyncSpeech2Text(config=client_config, use_secure_channel=False)

    async def test_transcribe_stream_passes_iterator_to_stub(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
        fake_pipeline_id: str,
    ) -> None:
        """The async service must pass the async iterator to ``stub.TranscribeStream`` unchanged.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to configure and assert against.
            fake_pipeline_id: Stable fake pipeline UUID.
        """
        request_iter: AsyncIterator[TranscribeStreamRequest] = _async_gen(
            TranscribeStreamRequest(
                audio_chunk=b"\x00" * 8000,
                end_of_stream=False,
                config=TranscribeRequestConfig(s2t_pipeline_id=fake_pipeline_id),
            )
        )
        expected: AsyncIterator[TranscribeStreamResponse] = MagicMock()  # type: ignore[assignment]
        mock_stub.TranscribeStream.return_value = expected

        result: AsyncIterator[TranscribeStreamResponse] = await service.transcribe_stream(request_iter)

        mock_stub.TranscribeStream.assert_called_once()
        assert result is expected

    async def test_transcribe_stream_with_end_of_stream_sentinel(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
        fake_pipeline_id: str,
    ) -> None:
        """An async iterator whose last item has ``end_of_stream=True`` must reach the stub.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock to assert against.
            fake_pipeline_id: Stable fake pipeline UUID.
        """
        request_iter: AsyncIterator[TranscribeStreamRequest] = _async_gen(
            TranscribeStreamRequest(
                audio_chunk=b"",
                end_of_stream=True,
                config=TranscribeRequestConfig(s2t_pipeline_id=fake_pipeline_id),
            )
        )
        mock_stub.TranscribeStream.return_value = MagicMock()
        await service.transcribe_stream(request_iter)
        mock_stub.TranscribeStream.assert_called_once()


# ---------------------------------------------------------------------------
# Error handling (async)
# ---------------------------------------------------------------------------


class TestAsyncErrorHandling:
    """Verifies that gRPC errors from async stub calls propagate to callers unchanged."""

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide an async-compatible stub mock pre-configured to raise on demand.

        Returns:
            MagicMock: Async stub mock whose side-effects are set per test.
        """
        return _make_async_stub()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC aio channel and stub patched for each error handling test.

        Args:
            mock_stub: Async stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with patches active.
        """
        with patch(_GRPC_AIO_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> AsyncSpeech2Text:
        """Construct the async service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            AsyncSpeech2Text: Service instance ready for error scenario testing.
        """
        return AsyncSpeech2Text(config=client_config, use_secure_channel=False)

    async def test_rpc_error_on_transcribe_file_propagates(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """A ``grpc.RpcError`` from ``TranscribeFile`` must propagate to the async caller.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock configured to raise ``UNAVAILABLE``.
        """
        mock_stub.TranscribeFile.side_effect = grpc.RpcError("UNAVAILABLE")
        with pytest.raises(grpc.RpcError):
            await service.transcribe_file(TranscribeFileRequest())

    async def test_rpc_error_on_list_pipelines_propagates(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """A ``grpc.RpcError`` from ``ListS2tPipelines`` must propagate to the async caller.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock configured to raise ``DEADLINE_EXCEEDED``.
        """
        mock_stub.ListS2tPipelines.side_effect = grpc.RpcError("DEADLINE_EXCEEDED")
        with pytest.raises(grpc.RpcError):
            await service.list_s2t_pipelines(ListS2tPipelinesRequest())

    async def test_rpc_error_on_transcribe_stream_propagates(
        self,
        service: AsyncSpeech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """A ``grpc.RpcError`` from ``TranscribeStream`` must propagate to the async caller.

        Args:
            service: Async service under test.
            mock_stub: Async stub mock configured to raise ``INTERNAL``.
        """
        mock_stub.TranscribeStream.side_effect = grpc.RpcError("INTERNAL")
        with pytest.raises(grpc.RpcError):
            await service.transcribe_stream(_async_gen(TranscribeStreamRequest()))

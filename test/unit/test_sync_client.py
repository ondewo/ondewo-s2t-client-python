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

"""Unit tests for the synchronous S2T :class:`~ondewo.s2t.client.client.Client`
and :class:`~ondewo.s2t.client.services.speech_to_text.Speech2Text` service.

All gRPC backend calls are mocked; no real server connection is required.
Test scenarios are inspired by the usage patterns in ``examples/``.

Patching strategy
-----------------
* ``grpc.insecure_channel`` is patched to prevent any real network activity
  during :class:`~ondewo.utils.base_services_interface.BaseServicesInterface`
  initialisation.
* ``Speech2TextStub`` is patched at the service-module level.  The ``stub``
  property creates a **new** stub instance on every call (non-cached), so the
  patch must be active for the entire duration of each test, not just during
  service construction.  The ``patch_grpc_and_stub`` autouse fixture achieves
  this.
"""

from typing import (
    Any,
    Iterator,
    List,
    Set,
    Tuple,
)
from unittest.mock import MagicMock, patch

import grpc
import pytest
from google.protobuf.empty_pb2 import Empty

from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.speech_to_text import Speech2Text
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

_STUB_PATH: str = "ondewo.s2t.client.services.speech_to_text.Speech2TextStub"
"""Fully-qualified import path of the stub class inside the sync service module."""

_GRPC_INSECURE: str = "grpc.insecure_channel"
"""Patch target for the gRPC insecure channel factory."""

_CLIENT_SPEECH2TEXT: str = "ondewo.s2t.client.client.Speech2Text"
"""Patch target for the Speech2Text class as imported by the Client module."""


# ---------------------------------------------------------------------------
# Client initialisation
# ---------------------------------------------------------------------------


class TestClientInitialization:
    """Tests that :class:`~ondewo.s2t.client.client.Client` wires up its services container."""

    @pytest.fixture
    def mock_speech2text(self) -> MagicMock:
        """Provide a :class:`~unittest.mock.MagicMock` spec'd to :class:`Speech2Text`.

        Returns:
            MagicMock: Mock instance with the same interface as the real service.
        """
        return MagicMock(spec=Speech2Text)

    @pytest.fixture
    def client(self, client_config: ClientConfig, mock_speech2text: MagicMock) -> Client:
        """Construct a :class:`~ondewo.s2t.client.client.Client` with all gRPC patched out.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
            mock_speech2text: Pre-built mock injected in place of the real service.

        Returns:
            Client: Fully initialised client whose ``services.speech_to_text`` is the mock.
        """
        with patch(_CLIENT_SPEECH2TEXT, return_value=mock_speech2text):
            with patch(_GRPC_INSECURE):
                return Client(config=client_config, use_secure_channel=False)

    def test_services_container_is_created(self, client: Client) -> None:
        """Services container must be present after construction.

        Args:
            client: Patched client under test.
        """
        assert client.services is not None

    def test_speech2text_service_is_present(self, client: Client) -> None:
        """``services.speech_to_text`` attribute must be set.

        Args:
            client: Patched client under test.
        """
        assert client.services.speech_to_text is not None

    def test_speech2text_service_is_the_injected_mock(
        self,
        client: Client,
        mock_speech2text: MagicMock,
    ) -> None:
        """The service stored on the container must be exactly the injected mock.

        Args:
            client: Patched client under test.
            mock_speech2text: The mock instance injected during construction.
        """
        assert client.services.speech_to_text is mock_speech2text

    def test_invalid_config_raises(self) -> None:
        """Passing a non-``BaseClientConfig`` value must raise ``ValueError`` or ``TypeError``."""
        with patch(_GRPC_INSECURE):
            with pytest.raises((ValueError, TypeError)):
                Client(config="not-a-config", use_secure_channel=False)  # type: ignore[arg-type]


class TestClientWithGrpcOptions:
    """Tests that :class:`~ondewo.s2t.client.client.Client` accepts gRPC channel options.

    Mirrors the ``options`` set construction shown in
    ``examples/file_transcription_example.py`` and ``examples/streaming_example.py``.
    """

    def test_client_accepts_custom_grpc_options(self, client_config: ClientConfig) -> None:
        """Client must be constructable with a non-empty ``options`` set.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
        """
        options: Set[Tuple[str, Any]] = {
            ("grpc.max_send_message_length", 1024 * 1024),
            ("grpc.max_receive_message_length", 1024 * 1024),
            ("grpc.keepalive_time_ms", 2 ** 31 - 1),
            ("grpc.enable_retries", 1),
        }
        with patch(_CLIENT_SPEECH2TEXT):
            with patch(_GRPC_INSECURE):
                client: Client = Client(
                    config=client_config,
                    use_secure_channel=False,
                    options=options,
                )
        assert client.services is not None

    def test_speech2text_accessible_via_services(self, client_config: ClientConfig) -> None:
        """``client.services.speech_to_text`` must be non-None after default construction.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
        """
        with patch(_CLIENT_SPEECH2TEXT):
            with patch(_GRPC_INSECURE):
                client: Client = Client(config=client_config, use_secure_channel=False)
        assert client.services.speech_to_text is not None


# ---------------------------------------------------------------------------
# Speech2Text service — stub delegation tests
# ---------------------------------------------------------------------------


class TestSpeech2TextServiceDelegation:
    """Verifies that every :class:`Speech2Text` method delegates to the correct stub RPC.

    Each test constructs the service inside the ``patch_grpc_and_stub`` autouse fixture
    which keeps both the gRPC channel and ``Speech2TextStub`` patched for the entire
    duration of the test, including internal ``self.stub`` property calls.
    """

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide a plain :class:`~unittest.mock.MagicMock` representing the gRPC stub.

        Returns:
            MagicMock: Stub mock whose RPC methods return ``MagicMock()`` by default.
        """
        return MagicMock()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Patch the gRPC channel factory and ``Speech2TextStub`` for each test.

        The ``stub`` property on :class:`Speech2Text` is non-cached and creates a new
        ``Speech2TextStub(channel=self.grpc_channel)`` on every RPC call.  This fixture
        ensures the same ``mock_stub`` instance is returned every time.

        Args:
            mock_stub: The stub mock to inject via ``Speech2TextStub.return_value``.

        Yields:
            None: Yields control to the test body with both patches active.
        """
        with patch(_GRPC_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> Speech2Text:
        """Construct a :class:`Speech2Text` service with patched gRPC infrastructure.

        Args:
            client_config: Minimal ``localhost:50051`` config from conftest.
            patch_grpc_and_stub: Autouse fixture that keeps gRPC/stub patches active.

        Returns:
            Speech2Text: Service instance ready for testing against ``mock_stub``.
        """
        return Speech2Text(config=client_config, use_secure_channel=False)

    def test_transcribe_file(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``transcribe_file`` must call ``stub.TranscribeFile`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: TranscribeFileRequest = TranscribeFileRequest()
        expected: TranscribeFileResponse = TranscribeFileResponse()
        mock_stub.TranscribeFile.return_value = expected
        assert service.transcribe_file(request) is expected
        mock_stub.TranscribeFile.assert_called_once_with(request)

    def test_transcribe_stream(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``transcribe_stream`` must pass the request iterator to ``stub.TranscribeStream``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request_iter: Iterator[TranscribeStreamRequest] = iter([TranscribeStreamRequest()])
        expected: Iterator[TranscribeStreamResponse] = iter([TranscribeStreamResponse()])
        mock_stub.TranscribeStream.return_value = expected
        assert service.transcribe_stream(request_iter) is expected
        mock_stub.TranscribeStream.assert_called_once_with(request_iter)

    def test_get_s2t_pipeline(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``get_s2t_pipeline`` must call ``stub.GetS2tPipeline`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: S2tPipelineId = S2tPipelineId()
        expected: Speech2TextConfig = Speech2TextConfig()
        mock_stub.GetS2tPipeline.return_value = expected
        assert service.get_s2t_pipeline(request) is expected
        mock_stub.GetS2tPipeline.assert_called_once_with(request)

    def test_create_s2t_pipeline(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``create_s2t_pipeline`` must call ``stub.CreateS2tPipeline`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: Speech2TextConfig = Speech2TextConfig()
        expected: S2tPipelineId = S2tPipelineId()
        mock_stub.CreateS2tPipeline.return_value = expected
        assert service.create_s2t_pipeline(request) is expected
        mock_stub.CreateS2tPipeline.assert_called_once_with(request)

    def test_delete_s2t_pipeline(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``delete_s2t_pipeline`` must call ``stub.DeleteS2tPipeline`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: S2tPipelineId = S2tPipelineId()
        expected: Empty = Empty()
        mock_stub.DeleteS2tPipeline.return_value = expected
        assert service.delete_s2t_pipeline(request) is expected
        mock_stub.DeleteS2tPipeline.assert_called_once_with(request)

    def test_update_s2t_pipeline(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``update_s2t_pipeline`` must call ``stub.UpdateS2tPipeline`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: Speech2TextConfig = Speech2TextConfig()
        expected: Empty = Empty()
        mock_stub.UpdateS2tPipeline.return_value = expected
        assert service.update_s2t_pipeline(request) is expected
        mock_stub.UpdateS2tPipeline.assert_called_once_with(request)

    def test_list_s2t_pipelines(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_pipelines`` must call ``stub.ListS2tPipelines`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: ListS2tPipelinesRequest = ListS2tPipelinesRequest()
        expected: ListS2tPipelinesResponse = ListS2tPipelinesResponse()
        mock_stub.ListS2tPipelines.return_value = expected
        assert service.list_s2t_pipelines(request) is expected
        mock_stub.ListS2tPipelines.assert_called_once_with(request)

    def test_list_s2t_languages(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_languages`` must call ``stub.ListS2tLanguages`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: ListS2tLanguagesRequest = ListS2tLanguagesRequest()
        expected: ListS2tLanguagesResponse = ListS2tLanguagesResponse()
        mock_stub.ListS2tLanguages.return_value = expected
        assert service.list_s2t_languages(request) is expected
        mock_stub.ListS2tLanguages.assert_called_once_with(request)

    def test_list_s2t_domains(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_domains`` must call ``stub.ListS2tDomains`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: ListS2tDomainsRequest = ListS2tDomainsRequest()
        expected: ListS2tDomainsResponse = ListS2tDomainsResponse()
        mock_stub.ListS2tDomains.return_value = expected
        assert service.list_s2t_domains(request) is expected
        mock_stub.ListS2tDomains.assert_called_once_with(request)

    def test_get_service_info(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``get_service_info`` must call ``stub.GetServiceInfo`` with the given request.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: Empty = Empty()
        expected: S2tGetServiceInfoResponse = S2tGetServiceInfoResponse()
        mock_stub.GetServiceInfo.return_value = expected
        assert service.get_service_info(request) is expected
        mock_stub.GetServiceInfo.assert_called_once_with(request)

    def test_list_s2t_language_models(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_language_models`` must call ``stub.ListS2tLanguageModels``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: ListS2tLanguageModelsRequest = ListS2tLanguageModelsRequest()
        expected: ListS2tLanguageModelsResponse = ListS2tLanguageModelsResponse()
        mock_stub.ListS2tLanguageModels.return_value = expected
        assert service.list_s2t_language_models(request) is expected
        mock_stub.ListS2tLanguageModels.assert_called_once_with(request)

    def test_create_user_language_model(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``create_user_language_model`` must call ``stub.CreateUserLanguageModel``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: CreateUserLanguageModelRequest = CreateUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.CreateUserLanguageModel.return_value = expected
        assert service.create_user_language_model(request) is expected
        mock_stub.CreateUserLanguageModel.assert_called_once_with(request)

    def test_delete_user_language_model(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``delete_user_language_model`` must call ``stub.DeleteUserLanguageModel``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: DeleteUserLanguageModelRequest = DeleteUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.DeleteUserLanguageModel.return_value = expected
        assert service.delete_user_language_model(request) is expected
        mock_stub.DeleteUserLanguageModel.assert_called_once_with(request)

    def test_add_data_to_user_language_model(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``add_data_to_user_language_model`` must call ``stub.AddDataToUserLanguageModel``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: AddDataToUserLanguageModelRequest = AddDataToUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.AddDataToUserLanguageModel.return_value = expected
        assert service.add_data_to_user_language_model(request) is expected
        mock_stub.AddDataToUserLanguageModel.assert_called_once_with(request)

    def test_train_user_language_model(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``train_user_language_model`` must call ``stub.TrainUserLanguageModel``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: TrainUserLanguageModelRequest = TrainUserLanguageModelRequest()
        expected: Empty = Empty()
        mock_stub.TrainUserLanguageModel.return_value = expected
        assert service.train_user_language_model(request) is expected
        mock_stub.TrainUserLanguageModel.assert_called_once_with(request)

    def test_list_s2t_normalization_pipelines(self, service: Speech2Text, mock_stub: MagicMock) -> None:
        """``list_s2t_normalization_pipelines`` must call ``stub.ListS2tNormalizationPipelines``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
        """
        request: ListS2tNormalizationPipelinesRequest = ListS2tNormalizationPipelinesRequest()
        expected: ListS2tNormalizationPipelinesResponse = ListS2tNormalizationPipelinesResponse()
        mock_stub.ListS2tNormalizationPipelines.return_value = expected
        assert service.list_s2t_normalization_pipelines(request) is expected
        mock_stub.ListS2tNormalizationPipelines.assert_called_once_with(request)


# ---------------------------------------------------------------------------
# Realistic file-transcription scenarios (inspired by file_transcription_example.py)
# ---------------------------------------------------------------------------


class TestTranscribeFileScenarios:
    """End-to-end style tests modelling ``examples/file_transcription_example.py``.

    These tests verify that the service correctly handles realistic
    :class:`~ondewo.s2t.speech_to_text_pb2.TranscribeFileRequest` payloads,
    including raw PCM audio bytes, pipeline IDs, and decoding modes.
    """

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide a plain stub mock for transcription scenario tests.

        Returns:
            MagicMock: Unconfigured stub mock.
        """
        return MagicMock()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC channel and stub patched for the duration of each scenario test.

        Args:
            mock_stub: Stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with patches active.
        """
        with patch(_GRPC_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> Speech2Text:
        """Construct the service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            Speech2Text: Service instance ready for scenario testing.
        """
        return Speech2Text(config=client_config, use_secure_channel=False)

    def test_transcribe_file_with_audio_bytes_and_pipeline_id(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
        fake_pipeline_id: str,
    ) -> None:
        """Sending raw PCM bytes with a pipeline ID must reach the stub unchanged.

        Mirrors the pattern in ``file_transcription_example.py`` where
        ``wave.readframes()`` bytes are packed into a
        :class:`~ondewo.s2t.speech_to_text_pb2.TranscribeFileRequest` together
        with a :class:`~ondewo.s2t.speech_to_text_pb2.TranscribeRequestConfig`
        specifying ``BEAM_SEARCH_WITH_LM`` decoding.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
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
        expected_response: TranscribeFileResponse = TranscribeFileResponse()
        mock_stub.TranscribeFile.return_value = expected_response

        result: TranscribeFileResponse = service.transcribe_file(request)

        mock_stub.TranscribeFile.assert_called_once_with(request)
        assert result is expected_response

    def test_transcribe_file_with_greedy_decoding(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
        fake_pipeline_id: str,
    ) -> None:
        """Transcription with ``GREEDY`` decoding must delegate to the stub correctly.

        Args:
            service: Service under test.
            mock_stub: Stub mock to assert against.
            fake_audio_bytes: Synthetic PCM payload.
            fake_pipeline_id: Stable fake pipeline UUID.
        """
        request: TranscribeFileRequest = TranscribeFileRequest(
            audio_file=fake_audio_bytes,
            config=TranscribeRequestConfig(
                s2t_pipeline_id=fake_pipeline_id,
                decoding=Decoding.GREEDY,
            ),
        )
        mock_stub.TranscribeFile.return_value = TranscribeFileResponse()
        service.transcribe_file(request)
        mock_stub.TranscribeFile.assert_called_once_with(request)

    def test_list_pipelines_then_use_first_pipeline(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
    ) -> None:
        """List pipelines, select the first, and transcribe — the canonical example flow.

        Replicates the pattern used in both example scripts:
        ``pipelines = list_s2t_pipelines(...).pipeline_configs; pipeline = pipelines[0]``.

        Args:
            service: Service under test.
            mock_stub: Stub mock programmed to return a single pipeline config.
            fake_audio_bytes: Synthetic PCM payload for the transcription request.
        """
        first_pipeline: Speech2TextConfig = Speech2TextConfig(id="pipeline-001")
        mock_stub.ListS2tPipelines.return_value = ListS2tPipelinesResponse(
            pipeline_configs=[first_pipeline]
        )

        pipelines_result: ListS2tPipelinesResponse = service.list_s2t_pipelines(
            ListS2tPipelinesRequest()
        )
        pipeline: Speech2TextConfig = pipelines_result.pipeline_configs[0]

        transcribe_request: TranscribeFileRequest = TranscribeFileRequest(
            audio_file=fake_audio_bytes,
            config=TranscribeRequestConfig(s2t_pipeline_id=pipeline.id),
        )
        mock_stub.TranscribeFile.return_value = TranscribeFileResponse()
        service.transcribe_file(transcribe_request)

        mock_stub.ListS2tPipelines.assert_called_once()
        mock_stub.TranscribeFile.assert_called_once_with(transcribe_request)
        assert pipeline.id == "pipeline-001"

    def test_transcribe_file_response_exposes_transcriptions(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        fake_audio_bytes: bytes,
        fake_pipeline_id: str,
    ) -> None:
        """Response ``.transcriptions`` must be iterable as shown in the example.

        The example iterates ``response.transcriptions`` and reads
        ``transcribe_message.transcription`` on each item.

        Args:
            service: Service under test.
            mock_stub: Stub mock returning a response with one transcription.
            fake_audio_bytes: Synthetic PCM payload.
            fake_pipeline_id: Stable fake pipeline UUID.
        """
        mock_transcription: MagicMock = MagicMock()
        mock_transcription.transcription = "hello world"
        mock_response: MagicMock = MagicMock(spec=TranscribeFileResponse)
        mock_response.transcriptions = [mock_transcription]
        mock_stub.TranscribeFile.return_value = mock_response

        request: TranscribeFileRequest = TranscribeFileRequest(
            audio_file=fake_audio_bytes,
            config=TranscribeRequestConfig(s2t_pipeline_id=fake_pipeline_id),
        )
        response: TranscribeFileResponse = service.transcribe_file(request)

        texts: List[str] = [t.transcription for t in response.transcriptions]
        assert texts == ["hello world"]


# ---------------------------------------------------------------------------
# Realistic streaming scenarios (inspired by streaming_example.py)
# ---------------------------------------------------------------------------


class TestTranscribeStreamScenarios:
    """End-to-end style tests modelling ``examples/streaming_example.py``.

    Validates the chunked streaming pattern where audio is sent chunk-by-chunk
    and the final request carries ``end_of_stream=True``.
    """

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide a plain stub mock for streaming scenario tests.

        Returns:
            MagicMock: Unconfigured stub mock.
        """
        return MagicMock()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC channel and stub patched for the duration of each scenario test.

        Args:
            mock_stub: Stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with patches active.
        """
        with patch(_GRPC_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> Speech2Text:
        """Construct the service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            Speech2Text: Service instance ready for scenario testing.
        """
        return Speech2Text(config=client_config, use_secure_channel=False)

    def test_transcribe_stream_passes_iterator_to_stub(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        streaming_requests: Iterator[TranscribeStreamRequest],
    ) -> None:
        """The service must hand the full request iterator to ``stub.TranscribeStream`` unchanged.

        Args:
            service: Service under test.
            mock_stub: Stub mock to configure and assert against.
            streaming_requests: Multi-chunk request iterator from conftest.
        """
        expected: Iterator[TranscribeStreamResponse] = iter([TranscribeStreamResponse()])
        mock_stub.TranscribeStream.return_value = expected

        result: Iterator[TranscribeStreamResponse] = service.transcribe_stream(streaming_requests)

        mock_stub.TranscribeStream.assert_called_once_with(streaming_requests)
        assert result is expected

    def test_transcribe_stream_with_end_of_stream_sentinel(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        fake_pipeline_id: str,
    ) -> None:
        """A request iterator whose last item has ``end_of_stream=True`` must reach the stub.

        Mirrors the final ``yield`` in ``create_streaming_request()`` from
        ``streaming_example.py``.

        Args:
            service: Service under test.
            mock_stub: Stub mock to assert against.
            fake_pipeline_id: Stable fake pipeline UUID.
        """
        final_request: TranscribeStreamRequest = TranscribeStreamRequest(
            audio_chunk=b"",
            end_of_stream=True,
            config=TranscribeRequestConfig(s2t_pipeline_id=fake_pipeline_id),
        )
        request_iter: Iterator[TranscribeStreamRequest] = iter([final_request])
        mock_stub.TranscribeStream.return_value = iter([])

        service.transcribe_stream(request_iter)

        mock_stub.TranscribeStream.assert_called_once()

    def test_stream_response_exposes_transcriptions(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
        streaming_requests: Iterator[TranscribeStreamRequest],
    ) -> None:
        """Each response chunk's ``.transcriptions`` must be iterable as shown in the example.

        The streaming example iterates the response generator and reads
        ``transcribe_message.transcription`` from each chunk.

        Args:
            service: Service under test.
            mock_stub: Stub mock returning one response chunk with one transcription.
            streaming_requests: Multi-chunk request iterator from conftest.
        """
        mock_transcription: MagicMock = MagicMock()
        mock_transcription.transcription = "streaming result"
        mock_chunk: MagicMock = MagicMock(spec=TranscribeStreamResponse)
        mock_chunk.transcriptions = [mock_transcription]
        mock_stub.TranscribeStream.return_value = iter([mock_chunk])

        response_gen: Iterator[TranscribeStreamResponse] = service.transcribe_stream(
            streaming_requests
        )
        texts: List[str] = [
            t.transcription for chunk in response_gen for t in chunk.transcriptions
        ]

        assert texts == ["streaming result"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Verifies that gRPC errors raised by the stub propagate to callers unchanged.

    The service layer must be transparent to :class:`grpc.RpcError` — it must
    not swallow, wrap, or retry errors on behalf of the caller.
    """

    @pytest.fixture
    def mock_stub(self) -> MagicMock:
        """Provide a stub mock pre-configured to raise on demand.

        Returns:
            MagicMock: Stub mock whose side-effects are set per test.
        """
        return MagicMock()

    @pytest.fixture(autouse=True)
    def patch_grpc_and_stub(self, mock_stub: MagicMock) -> Iterator[None]:
        """Keep gRPC channel and stub patched for each error handling test.

        Args:
            mock_stub: Stub mock injected as ``Speech2TextStub.return_value``.

        Yields:
            None: Yields to the test body with patches active.
        """
        with patch(_GRPC_INSECURE), patch(_STUB_PATH, return_value=mock_stub):
            yield

    @pytest.fixture
    def service(self, client_config: ClientConfig, patch_grpc_and_stub: None) -> Speech2Text:
        """Construct the service inside the active gRPC/stub patches.

        Args:
            client_config: Minimal config from conftest.
            patch_grpc_and_stub: Autouse fixture ensuring patches are active.

        Returns:
            Speech2Text: Service instance ready for error scenario testing.
        """
        return Speech2Text(config=client_config, use_secure_channel=False)

    def test_rpc_error_on_transcribe_file_propagates(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """A ``grpc.RpcError`` from ``TranscribeFile`` must propagate to the caller.

        Args:
            service: Service under test.
            mock_stub: Stub mock configured to raise ``UNAVAILABLE``.
        """
        mock_stub.TranscribeFile.side_effect = grpc.RpcError("UNAVAILABLE")
        with pytest.raises(grpc.RpcError):
            service.transcribe_file(TranscribeFileRequest())

    def test_rpc_error_on_list_pipelines_propagates(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """A ``grpc.RpcError`` from ``ListS2tPipelines`` must propagate to the caller.

        Args:
            service: Service under test.
            mock_stub: Stub mock configured to raise ``DEADLINE_EXCEEDED``.
        """
        mock_stub.ListS2tPipelines.side_effect = grpc.RpcError("DEADLINE_EXCEEDED")
        with pytest.raises(grpc.RpcError):
            service.list_s2t_pipelines(ListS2tPipelinesRequest())

    def test_rpc_error_on_transcribe_stream_propagates(
        self,
        service: Speech2Text,
        mock_stub: MagicMock,
    ) -> None:
        """A ``grpc.RpcError`` from ``TranscribeStream`` must propagate to the caller.

        Args:
            service: Service under test.
            mock_stub: Stub mock configured to raise ``INTERNAL``.
        """
        mock_stub.TranscribeStream.side_effect = grpc.RpcError("INTERNAL")
        with pytest.raises(grpc.RpcError):
            service.transcribe_stream(iter([TranscribeStreamRequest()]))

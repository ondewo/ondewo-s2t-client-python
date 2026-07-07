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

"""Mock-based tests that prove the scripts under ``examples/`` actually work.

Unlike ``test_sync_client.py`` (which re-implements the example *patterns*), this
module imports the real example modules from the ``examples/`` directory and drives
their public functions — the pure request builders and each script's ``main()`` — with
the :class:`~ondewo.s2t.client.client.Client` fully mocked.  No gRPC server is contacted:
the only real I/O is reading the bundled sample WAV / JSON config files that ship in the
repository, so the suite stays hermetic.

The assertions verify that every example:

* imports cleanly against the current generated stubs and client API,
* builds the correct :class:`TranscribeFileRequest` / :class:`TranscribeStreamRequest`
  payloads from the first listed pipeline, and
* handles the (mocked) transcription response it gets back.
"""

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    List,
)
from unittest.mock import MagicMock, patch

import pytest

from ondewo.s2t.speech_to_text_pb2 import (
    Decoding,
    ListS2tPipelinesResponse,
    Speech2TextConfig,
    TranscribeFileRequest,
    TranscribeStreamRequest,
)

# ---------------------------------------------------------------------------
# Locate and load the example modules straight from the examples/ directory.
# They are plain scripts (no package / __init__.py), so importlib is used to
# load each one by file path.  Loading them here is itself a smoke test that
# the examples import cleanly against the current API.
# ---------------------------------------------------------------------------

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
"""Repository root, derived from this test file's location (test/unit/ → repo)."""

EXAMPLES_DIR: Path = REPO_ROOT / "examples"
"""Directory holding the runnable example scripts and their sample assets."""

INSECURE_CONFIG_PATH: Path = EXAMPLES_DIR / "configs" / "insecure_grpc.json"
"""Absolute path to the bundled insecure (host/port only) client config."""

EXPECTED_PIPELINE_ID: str = "pipeline-under-test-001"
"""Fake pipeline id returned by the mocked ``ListS2tPipelines`` response."""


def _load_example_module(name: str) -> ModuleType:
    """Load an ``examples/<name>.py`` script as an importable module.

    Args:
        name (str): Base filename (without extension) of the example script.

    Returns:
        ModuleType: The executed example module, with its top-level functions bound.
    """
    path: Path = EXAMPLES_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None  # narrow Optional for mypy
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FILE_EXAMPLE: ModuleType = _load_example_module("file_transcription_example")
"""The imported ``examples/file_transcription_example.py`` module."""

STREAM_EXAMPLE: ModuleType = _load_example_module("streaming_example")
"""The imported ``examples/streaming_example.py`` module."""


def _one_pipeline_response() -> ListS2tPipelinesResponse:
    """Build a ``ListS2tPipelinesResponse`` carrying exactly one pipeline config.

    Returns:
        ListS2tPipelinesResponse: Response whose single pipeline has
            :data:`EXPECTED_PIPELINE_ID` as its id.
    """
    return ListS2tPipelinesResponse(pipeline_configs=[Speech2TextConfig(id=EXPECTED_PIPELINE_ID)])


def _mock_service_with_pipeline() -> MagicMock:
    """Return a mock S2T service pre-programmed to list one pipeline.

    Returns:
        MagicMock: Stand-in for ``client.services.speech_to_text`` whose
            ``list_s2t_pipelines`` yields :func:`_one_pipeline_response`.
    """
    service: MagicMock = MagicMock()
    service.list_s2t_pipelines.return_value = _one_pipeline_response()
    return service


# ---------------------------------------------------------------------------
# Import smoke tests
# ---------------------------------------------------------------------------


class TestExampleModulesImport:
    """Both example scripts must import cleanly and expose their expected entry points."""

    def test_file_example_exposes_main(self) -> None:
        """``file_transcription_example`` must expose a callable ``main``."""
        assert callable(FILE_EXAMPLE.main)

    def test_stream_example_exposes_helpers_and_main(self) -> None:
        """``streaming_example`` must expose its request builders and ``main``."""
        assert callable(STREAM_EXAMPLE.main)
        assert callable(STREAM_EXAMPLE.get_streaming_audio)
        assert callable(STREAM_EXAMPLE.create_streaming_request)


# ---------------------------------------------------------------------------
# Pure request-builder tests (streaming_example helpers)
# ---------------------------------------------------------------------------


class TestStreamingRequestBuilders:
    """The pure helpers in ``streaming_example`` that turn audio into stream requests."""

    def test_get_streaming_audio_yields_chunks(self) -> None:
        """``get_streaming_audio`` must yield non-empty byte chunks from a real WAV file."""
        audio_path: str = str(EXAMPLES_DIR / "audiofiles" / "sample_2.wav")
        chunks: List[bytes] = list(STREAM_EXAMPLE.get_streaming_audio(audio_path))
        assert chunks
        assert all(isinstance(chunk, bytes) and chunk for chunk in chunks)

    def test_create_streaming_request_appends_end_of_stream_sentinel(self) -> None:
        """The builder must emit one request per chunk plus a final ``end_of_stream`` sentinel."""
        audio_chunks: List[bytes] = [b"\x01\x02", b"\x03\x04", b"\x05\x06"]
        requests: List[TranscribeStreamRequest] = list(
            STREAM_EXAMPLE.create_streaming_request(iter(audio_chunks), EXPECTED_PIPELINE_ID)
        )

        # one request per audio chunk, plus the trailing sentinel
        assert len(requests) == len(audio_chunks) + 1

        body_requests: List[TranscribeStreamRequest] = requests[:-1]
        assert all(not req.end_of_stream for req in body_requests)
        assert [req.audio_chunk for req in body_requests] == audio_chunks

        sentinel: TranscribeStreamRequest = requests[-1]
        assert sentinel.end_of_stream is True
        assert sentinel.audio_chunk == b""

    def test_create_streaming_request_sets_pipeline_id_and_greedy_decoding(self) -> None:
        """Every emitted request must carry the pipeline id and GREEDY decoding config."""
        requests: List[TranscribeStreamRequest] = list(
            STREAM_EXAMPLE.create_streaming_request(iter([b"\x00\x01"]), EXPECTED_PIPELINE_ID)
        )
        assert requests
        for req in requests:
            assert req.config.s2t_pipeline_id == EXPECTED_PIPELINE_ID
            assert req.config.decoding == Decoding.GREEDY


# ---------------------------------------------------------------------------
# End-to-end main() tests with a mocked Client
# ---------------------------------------------------------------------------


class TestFileTranscriptionMain:
    """Drive ``file_transcription_example.main`` end-to-end with the Client mocked."""

    def test_main_lists_pipeline_and_transcribes_bundled_audio(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() must list pipelines, transcribe the sample WAV, and print the transcription.

        Args:
            monkeypatch (pytest.MonkeyPatch): Used to chdir to the repo root so the
                repo-root-relative ``AUDIO_FILE`` path in the example resolves.
            capsys (pytest.CaptureFixture[str]): Captures the transcription printed by main().
        """
        monkeypatch.chdir(REPO_ROOT)
        service: MagicMock = _mock_service_with_pipeline()
        response: MagicMock = MagicMock()
        response.transcriptions = [MagicMock(transcription="hello from a file")]
        service.transcribe_file.return_value = response

        with patch.object(FILE_EXAMPLE, "Client") as mock_client_cls:
            mock_client_cls.return_value.services.speech_to_text = service
            with patch("sys.argv", ["file_transcription_example", "--config", str(INSECURE_CONFIG_PATH)]):
                FILE_EXAMPLE.main()

        # The client was built from the parsed insecure config.
        mock_client_cls.assert_called_once()
        built_config: Any = mock_client_cls.call_args.kwargs["config"]
        assert built_config.host == "localhost"

        # The transcribe request was built from the first listed pipeline + real audio bytes.
        service.list_s2t_pipelines.assert_called_once()
        service.transcribe_file.assert_called_once()
        sent_request: TranscribeFileRequest = service.transcribe_file.call_args.kwargs["request"]
        assert sent_request.config.s2t_pipeline_id == EXPECTED_PIPELINE_ID
        assert sent_request.config.decoding == Decoding.BEAM_SEARCH_WITH_LM
        assert len(sent_request.audio_file) > 0

        # The response transcription was handled (printed).
        assert "hello from a file" in capsys.readouterr().out


class TestStreamingMain:
    """Drive ``streaming_example.main`` end-to-end with the Client mocked."""

    def test_main_lists_pipeline_and_streams_bundled_audio(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() must list pipelines, stream the sample WAV, and print the transcription.

        Args:
            monkeypatch (pytest.MonkeyPatch): Used to chdir to the repo root so the
                repo-root-relative ``AUDIO_FILE`` path in the example resolves.
            capsys (pytest.CaptureFixture[str]): Captures the transcription printed by main().
        """
        monkeypatch.chdir(REPO_ROOT)
        service: MagicMock = _mock_service_with_pipeline()
        response_chunk: MagicMock = MagicMock()
        response_chunk.transcriptions = [MagicMock(transcription="hello from a stream")]
        service.transcribe_stream.return_value = iter([response_chunk])

        with patch.object(STREAM_EXAMPLE, "Client") as mock_client_cls:
            mock_client_cls.return_value.services.speech_to_text = service
            with patch("sys.argv", ["streaming_example", "--config", str(INSECURE_CONFIG_PATH)]):
                STREAM_EXAMPLE.main()

        mock_client_cls.assert_called_once()
        service.list_s2t_pipelines.assert_called_once()
        service.transcribe_stream.assert_called_once()

        # The streaming request iterator built from the first pipeline is well-formed:
        # every request targets that pipeline and the stream terminates with a sentinel.
        request_iterator: Any = service.transcribe_stream.call_args.kwargs["request_iterator"]
        stream_requests: List[TranscribeStreamRequest] = list(request_iterator)
        assert stream_requests
        assert all(req.config.s2t_pipeline_id == EXPECTED_PIPELINE_ID for req in stream_requests)
        assert stream_requests[-1].end_of_stream is True

        assert "hello from a stream" in capsys.readouterr().out

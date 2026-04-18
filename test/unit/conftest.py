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

"""Shared pytest fixtures for the ONDEWO S2T client unit test suite.

Provides reusable test data constants and pytest fixtures used by both
test_sync_client.py and test_async_client.py.  All fixtures are session- or
function-scoped (default) and carry full type annotations.
"""

from typing import (
    Iterator,
    List,
)

import pytest

from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.speech_to_text_pb2 import (
    Decoding,
    PostProcessingOptions,
    TranscribeRequestConfig,
    TranscribeStreamRequest,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

FAKE_PIPELINE_ID: str = "test-pipeline-uuid-1234"
"""A stable, fake pipeline ID used across all unit tests."""

CHUNK_SIZE: int = 8000
"""Audio chunk size in bytes, matching the value used in streaming_example.py."""

FAKE_AUDIO_BYTES: bytes = b"\x00\x01\x02\x03" * (CHUNK_SIZE * 4)
"""32 KB of synthetic PCM audio data (repeating 4-byte pattern) used as audio payload in tests."""


# ---------------------------------------------------------------------------
# Shared pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client_config() -> ClientConfig:
    """Provide a minimal :class:`~ondewo.s2t.client.client_config.ClientConfig` for unit tests.

    Returns:
        ClientConfig: A config pointing to ``localhost:50051`` with no TLS certificate.
    """
    return ClientConfig(host="localhost", port="50051")


@pytest.fixture
def fake_audio_bytes() -> bytes:
    """Provide a block of synthetic PCM audio bytes for use in transcription requests.

    Returns:
        bytes: 32 KB of repeating ``\\x00\\x01\\x02\\x03`` pattern bytes.
    """
    return FAKE_AUDIO_BYTES


@pytest.fixture
def fake_pipeline_id() -> str:
    """Provide a stable fake pipeline UUID string for use in request configs.

    Returns:
        str: The module-level ``FAKE_PIPELINE_ID`` constant.
    """
    return FAKE_PIPELINE_ID


@pytest.fixture
def audio_chunks() -> List[bytes]:
    """Split :data:`FAKE_AUDIO_BYTES` into ``CHUNK_SIZE``-byte chunks.

    This mirrors the chunking pattern used in ``examples/streaming_example.py``
    where ``wave.readframes(CHUNK_SIZE)`` is called in a loop.

    Returns:
        List[bytes]: Ordered list of byte chunks, each at most ``CHUNK_SIZE`` bytes.
    """
    data: bytes = FAKE_AUDIO_BYTES
    return [data[i: i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]


@pytest.fixture
def streaming_requests(audio_chunks: List[bytes]) -> Iterator[TranscribeStreamRequest]:
    """Build a complete streaming request iterator mirroring ``streaming_example.py``.

    Produces one :class:`TranscribeStreamRequest` per audio chunk with
    ``end_of_stream=False``, followed by a final sentinel request with
    ``end_of_stream=True`` and an empty ``audio_chunk``.

    Args:
        audio_chunks: List of raw PCM byte chunks produced by the
            :func:`audio_chunks` fixture.

    Returns:
        Iterator[TranscribeStreamRequest]: Ready-to-use request iterator that
            can be passed directly to
            :meth:`~ondewo.s2t.client.services.speech_to_text.Speech2Text.transcribe_stream`.
    """
    requests: List[TranscribeStreamRequest] = [
        TranscribeStreamRequest(
            audio_chunk=chunk,
            end_of_stream=False,
            config=TranscribeRequestConfig(
                s2t_pipeline_id=FAKE_PIPELINE_ID,
                post_processing=PostProcessingOptions(spelling_correction=False),
                decoding=Decoding.GREEDY,
            ),
        )
        for chunk in audio_chunks
    ]
    # Final sentinel chunk signals the server that the stream is complete.
    requests.append(
        TranscribeStreamRequest(
            audio_chunk=b"",
            end_of_stream=True,
            config=TranscribeRequestConfig(
                s2t_pipeline_id=FAKE_PIPELINE_ID,
                post_processing=PostProcessingOptions(spelling_correction=False),
                decoding=Decoding.GREEDY,
            ),
        )
    )
    return iter(requests)

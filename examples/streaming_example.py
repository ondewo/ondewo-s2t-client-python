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
import json
import os
import sys
import wave
from pathlib import Path
from time import perf_counter
from typing import (
    Any,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
)

import grpc
from dotenv import load_dotenv
from loguru import logger as log

from ondewo.s2t import speech_to_text_pb2
from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.speech_to_text import Speech2Text
from ondewo.s2t.speech_to_text_pb2 import (
    ListS2tPipelinesRequest,
    Speech2TextConfig,
)

# Load the canonical example configuration (path relative to this script so the
# working directory does not matter).
load_dotenv(Path(__file__).with_name("environment.env"))

CHUNK_SIZE: int = 8000


def _env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable ("true"/"false", case-insensitive).

    Args:
        name (str):
            Name of the environment variable to read.
        default (bool):
            Value returned when the variable is unset or empty.

    Returns:
        bool:
            The parsed boolean value.
    """
    raw: str = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _resolve_audio_file(default_name: str) -> str:
    """Resolve the audio file path from the canonical env var.

    Reads ``ONDEWO_S2T_AUDIO_FILE``; relative paths are resolved against the
    ``examples/`` directory so the example is runnable from any working directory.

    Args:
        default_name (str):
            Path (relative to ``examples/``) used when the env var is unset.

    Returns:
        str:
            Absolute path to the audio file to transcribe.
    """
    configured: str = os.getenv("ONDEWO_S2T_AUDIO_FILE", "").strip() or default_name
    audio_path: Path = Path(configured)
    if not audio_path.is_absolute():
        audio_path = Path(__file__).parent / audio_path
    return str(audio_path)


def build_client_config() -> ClientConfig:
    """Build a :class:`ClientConfig` from the canonical ONDEWO_* / KEYCLOAK_* env vars.

    Returns:
        ClientConfig:
            The connection and (optional) Keycloak authentication configuration.
    """
    grpc_cert: Optional[str] = None
    cert_path: str = os.getenv("ONDEWO_GRPC_CERT", "").strip()
    if cert_path:
        log.info(f"Reading gRPC certificate from {cert_path}")
        grpc_cert = Path(cert_path).read_text()

    return ClientConfig(
        host=os.environ["ONDEWO_HOST"],
        port=os.environ["ONDEWO_PORT"],
        grpc_cert=grpc_cert,
        keycloak_url=os.getenv("KEYCLOAK_URL", ""),
        realm=os.getenv("KEYCLOAK_REALM", ""),
        client_id=os.getenv("KEYCLOAK_CLIENT_ID", ""),
        user_name=os.getenv("KEYCLOAK_USER_NAME", ""),
        password=os.getenv("KEYCLOAK_PASSWORD", ""),
        keycloak_verify_ssl=_env_bool("KEYCLOAK_VERIFY_SSL", default=True),
    )


# We are going to send the file chunk-by-chunk to simulate a stream
def get_streaming_audio(audio_path: str) -> Iterator[bytes]:
    with wave.open(audio_path) as w:
        chunk: bytes = w.readframes(CHUNK_SIZE)
        while chunk != b"":
            yield chunk
            chunk = w.readframes(CHUNK_SIZE)


def create_streaming_request(
    audio_stream: Iterator[bytes],
    pipeline_id: str,
    transcribe_not_final: bool = False,
) -> Iterator[speech_to_text_pb2.TranscribeStreamRequest]:
    for i, chunk in enumerate(audio_stream):
        yield speech_to_text_pb2.TranscribeStreamRequest(
            audio_chunk=chunk,
            end_of_stream=False,
            config=speech_to_text_pb2.TranscribeRequestConfig(
                s2t_pipeline_id=pipeline_id,
                post_processing=speech_to_text_pb2.PostProcessingOptions(
                    spelling_correction=False,
                ),
                decoding=speech_to_text_pb2.Decoding.GREEDY,
                utterance_detection=speech_to_text_pb2.UtteranceDetectionOptions(
                    transcribe_not_final=transcribe_not_final,
                ),
            ),
        )
    # End the stream
    yield speech_to_text_pb2.TranscribeStreamRequest(
        audio_chunk=b"",
        end_of_stream=True,
        config=speech_to_text_pb2.TranscribeRequestConfig(
            s2t_pipeline_id=pipeline_id,
            post_processing=speech_to_text_pb2.PostProcessingOptions(
                spelling_correction=False,
            ),
            decoding=speech_to_text_pb2.Decoding.GREEDY,
        ),
    )


def main() -> None:
    log.info("START: streaming_example: main")
    start_time: float = perf_counter()

    config: ClientConfig = build_client_config()
    use_secure_channel: bool = _env_bool("ONDEWO_USE_SECURE_CHANNEL", default=False)
    audio_file: str = _resolve_audio_file("audiofiles/sample_2.wav")
    log.info(f"Connecting to ONDEWO S2T at {config.host_and_port} (secure={use_secure_channel})")

    # https://github.com/grpc/grpc-proto/blob/master/grpc/service_config/service_config.proto
    service_config_json: str = json.dumps(
        {
            "methodConfig": [
                {
                    "name": [
                        # To apply retry to all methods, put [{}] as a value in the "name" field
                        # {}
                        # List single rpc method calls
                        {"service": "ondewo.s2t.Speech2Text", "method": "ListS2tPipelines"},
                        {"service": "ondewo.s2t.Speech2Text", "method": "TranscribeStream"},
                    ],
                    "retryPolicy": {
                        "maxAttempts": 10,
                        "initialBackoff": "1.1s",
                        "maxBackoff": "3000s",
                        "backoffMultiplier": 2,
                        "retryableStatusCodes": [
                            grpc.StatusCode.CANCELLED.name,
                            grpc.StatusCode.UNKNOWN.name,
                            grpc.StatusCode.DEADLINE_EXCEEDED.name,
                            grpc.StatusCode.NOT_FOUND.name,
                            grpc.StatusCode.RESOURCE_EXHAUSTED.name,
                            grpc.StatusCode.ABORTED.name,
                            grpc.StatusCode.INTERNAL.name,
                            grpc.StatusCode.UNAVAILABLE.name,
                            grpc.StatusCode.DATA_LOSS.name,
                        ],
                    },
                }
            ]
        }
    )

    options: Set[Tuple[str, Any]] = {
        # Define custom max message sizes: 1MB here is an arbitrary example.
        ("grpc.max_send_message_length", 1024 * 1024),
        ("grpc.max_receive_message_length", 1024 * 1024),
        # Example of setting KeepAlive options through generic channel_args
        ("grpc.keepalive_time_ms", 2**31 - 1),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.keepalive_permit_without_calls", False),
        ("grpc.http2.max_pings_without_data", 2),
        # Example arg requested for the feature
        ("grpc.dns_enable_srv_queries", 1),
        ("grpc.enable_retries", 1),
        ("grpc.service_config", service_config_json),
    }

    client: Client = Client(config=config, use_secure_channel=use_secure_channel, options=options)
    s2t_service: Speech2Text = client.services.speech_to_text  # type:ignore

    try:
        # List all speech-2-text pipelines (model setups) present on the server.
        list_s2t_pipeline_request: ListS2tPipelinesRequest = ListS2tPipelinesRequest()
        pipelines: List[Speech2TextConfig] = [
            t for t in s2t_service.list_s2t_pipelines(list_s2t_pipeline_request).pipeline_configs
        ]
        if not pipelines:
            raise RuntimeError("The S2T server returned no pipelines to transcribe with.")

        # Pick the pipeline id from the env var if provided, otherwise the first one.
        pipeline_id: str = os.getenv("ONDEWO_S2T_PIPELINE_ID", "").strip() or pipelines[0].id
        log.info(f"Using S2T pipeline id: {pipeline_id}")

        # Get audio stream (iterator of audio chunks).
        log.info(f"Streaming audio file: {audio_file}")
        audio_stream: Iterator[bytes] = get_streaming_audio(audio_file)

        # Create streaming request.
        streaming_request: Iterator[speech_to_text_pb2.TranscribeStreamRequest] = create_streaming_request(
            audio_stream=audio_stream, pipeline_id=pipeline_id
        )

        # Transcribe the stream and get back responses.
        log.info("Sending TranscribeStream request")
        response_gen: Iterator[speech_to_text_pb2.TranscribeStreamResponse] = s2t_service.transcribe_stream(
            request_iterator=streaming_request
        )

        # Print transcribed utterances.
        for i, response_chunk in enumerate(response_gen):
            for transcribe_message in response_chunk.transcriptions:
                print(f"{i}. response_chunk: {transcribe_message.transcription}")
    except grpc.RpcError as rpc_error:
        log.error(f"gRPC call failed: code={rpc_error.code()} details={rpc_error.details()}")
        raise

    log.info(f"DONE: streaming_example: main. Elapsed time: {perf_counter() - start_time:.5f}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("streaming_example failed")
        sys.exit(1)

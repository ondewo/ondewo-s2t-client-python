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
import argparse
import json
import wave
from typing import (
    Any,
    Iterator,
    List,
    Set,
    Tuple,
)

import grpc

from ondewo.s2t import speech_to_text_pb2
from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.speech_to_text import Speech2Text
from ondewo.s2t.speech_to_text_pb2 import (
    ListS2tPipelinesRequest,
    Speech2TextConfig,
)

AUDIO_FILE: str = "examples/audiofiles/sample_2.wav"
CHUNK_SIZE: int = 8000


# We are going to make to send the file chunk-by-chunk to simulate a stream
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
                )
            )
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
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming example.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    config: ClientConfig
    with open(args.config) as f:
        config = ClientConfig.from_json(f.read())  # type:ignore
    assert config

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
        ("grpc.keepalive_time_ms", 2 ** 31 - 1),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.keepalive_permit_without_calls", False),
        ("grpc.http2.max_pings_without_data", 2),
        # Example arg requested for the feature
        ("grpc.dns_enable_srv_queries", 1),
        ("grpc.enable_retries", 1),
        ("grpc.service_config", service_config_json)
    }

    client: Client = Client(config=config, use_secure_channel=args.secure, options=options)
    s2t_service: Speech2Text = client.services.speech_to_text  # type:ignore

    # List all speech-2-text pipelines (model setups) present on the server
    # We are going to pick the first pipeline (model setup)
    list_s2t_pipeline_request: ListS2tPipelinesRequest = ListS2tPipelinesRequest()
    pipelines: List[Speech2TextConfig] = [
        t for t in s2t_service.list_s2t_pipelines(list_s2t_pipeline_request).pipeline_configs
    ]
    assert pipelines
    pipeline: Speech2TextConfig = pipelines[0]
    assert pipeline

    # Get audio stream (iterator of audio chunks)
    audio_stream: Iterator[bytes] = get_streaming_audio(AUDIO_FILE)

    # Create streaming request
    streaming_request: Iterator[speech_to_text_pb2.TranscribeStreamRequest] = create_streaming_request(
        audio_stream=audio_stream, pipeline_id=pipeline.id
    )

    # Transcribe the stream and get back responses
    response_gen: Iterator[speech_to_text_pb2.TranscribeStreamResponse] = s2t_service.transcribe_stream(
        request_iterator=streaming_request
    )

    # Print transcribed utterances
    for i, response_chunk in enumerate(response_gen):
        for transcribe_message in response_chunk.transcriptions:
            print(f"{i}. response_chunk: {transcribe_message.transcription}")


if __name__ == "__main__":
    main()

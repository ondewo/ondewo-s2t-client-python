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
    List,
    Set,
    Tuple,
)

import grpc

from ondewo.s2t import speech_to_text_pb2
from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.speech_to_text import Speech2Text

AUDIO_FILE: str = "examples/audiofiles/sample_1.wav"  # noqa


def main() -> None:
    parser = argparse.ArgumentParser(description="File transcription example.")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/insecure_grpc.json",
        help="The GRPC configuration file path. "
             "See examples/configs in the ondewo-s2t-client-python repository.",
    )
    parser.add_argument(
        "--secure",
        default=False,
        action="store_true",
        help="Use secure GRPC connection (default is insecure).",
    )
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

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
                        {"service": "ondewo.s2t.Speech2Text", "method": "TranscribeFile"},
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
    s2t_service: Speech2Text = client.services.speech_to_text

    # List all speech-2-text pipelines (model setups) present on the server
    # We are going to pick the first pipeline (model setup)
    pipelines: List[speech_to_text_pb2.Speech2TextConfig] = s2t_service.list_s2t_pipelines(  # type: ignore
        request=speech_to_text_pb2.ListS2tPipelinesRequest()
    ).pipeline_configs
    pipeline: speech_to_text_pb2.Speech2TextConfig = pipelines[0]  # type: ignore

    # Read file which we want to transcribe
    with wave.open(AUDIO_FILE) as w:
        audio: bytes = w.readframes(w.getnframes())

    # Create transcription request
    request = speech_to_text_pb2.TranscribeFileRequest(
        audio_file=audio,
        config=speech_to_text_pb2.TranscribeRequestConfig(
            s2t_pipeline_id=pipeline.id,  # type: ignore
            decoding=speech_to_text_pb2.Decoding.BEAM_SEARCH_WITH_LM,  # type: ignore
        )
    )
    # Send transcription request and get response
    transcribe_response: speech_to_text_pb2.TranscribeFileResponse = s2t_service.transcribe_file(
        request=request
    )  # type: ignore
    for transcribe_message in transcribe_response.transcriptions:  # type: ignore
        print(f"File transcript: {transcribe_message.transcription}")


if __name__ == "__main__":
    main()

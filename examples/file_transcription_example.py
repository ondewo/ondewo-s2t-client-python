#!/usr/bin/env python
# coding: utf-8
# Copyright 2021 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import wave

from ondewo.s2t import speech_to_text_pb2
from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.speech_to_text import Speech2Text
from ondewo.s2t.speech_to_text_pb2 import ListS2tPipelinesRequest, Speech2TextConfig

AUDIO_FILE: str = "examples/audiofiles/sample_1.wav"


def main():
    parser = argparse.ArgumentParser(description="File transcription example.")
    parser.add_argument(
        "--config",
        type=str,
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

    client: Client = Client(config=config, use_secure_channel=args.secure)
    s2t_service: Speech2Text = client.services.speech_to_text

    # List all speech-2-text pipelines (model setups) present on the server
    # We are going to pick the first pipeline (model setup)
    pipelines = s2t_service.list_s2t_pipelines(request=ListS2tPipelinesRequest()).pipeline_configs
    pipeline: Speech2TextConfig = pipelines[0]

    # Read file which we want to transcribe
    with wave.open(AUDIO_FILE) as w:
        audio: bytes = w.readframes(w.getnframes())

    # Create transcription request
    request = speech_to_text_pb2.TranscribeFileRequest(
        audio_file=audio,
        config=speech_to_text_pb2.TranscribeRequestConfig(
            s2t_pipeline_id=pipeline.id,
            ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
        )
    )
    # Send transcription request and get response
    transcribe_response = s2t_service.transcribe_file(request=request)

    for transcribe_message in transcribe_response.transcriptions:
        print(f"File transcript: {transcribe_message.transcription}")


if __name__ == "__main__":
    main()

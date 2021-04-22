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
from typing import Iterator

from google.protobuf.empty_pb2 import Empty

from ondewo.s2t import speech_to_text_pb2
from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.client.services.speech_to_text import Speech2Text
from ondewo.s2t.speech_to_text_pb2 import Speech2TextConfig

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
) -> Iterator[speech_to_text_pb2.TranscribeStreamRequest]:
    for i, chunk in enumerate(audio_stream):
        yield speech_to_text_pb2.TranscribeStreamRequest(
            audio_chunk=chunk,
            s2t_pipeline_id=pipeline_id,
            spelling_correction=False,
            ctc_decoding=speech_to_text_pb2.CTCDecoding.GREEDY,
            end_of_stream=False,
        )
    # End the stream
    yield speech_to_text_pb2.TranscribeStreamRequest(
        audio_chunk=b"",
        s2t_pipeline_id=pipeline_id,
        spelling_correction=False,
        ctc_decoding=speech_to_text_pb2.CTCDecoding.GREEDY,
        end_of_stream=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Streaming example.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=args.secure)
    s2t_service: Speech2Text = client.services.speech_to_text

    # List all speech-2-text pipelines (model setups) present on the server
    # We are going to pick the first pipeline (model setup)
    pipelines = s2t_service.list_s2t_pipelines(request=Empty()).pipeline_configs
    pipeline: Speech2TextConfig = pipelines[0]

    # Get audio stream (iterator of audio chunks)
    audio_stream: Iterator[bytes] = get_streaming_audio(AUDIO_FILE)

    # Create streaming request
    streaming_request: Iterator[speech_to_text_pb2.TranscribeStreamRequest] = create_streaming_request(
        audio_stream=audio_stream, pipeline_id=pipeline.id
    )

    # Transcribe the stream and get back responses
    response_gen: Iterator[speech_to_text_pb2.TranscribeStreamResponse] = s2t_service.transcribe_stream(
        streaming_request
    )

    # Print transcribed utterances
    for i, response_chunk in enumerate(response_gen):
        print(response_chunk.transcription)


if __name__ == "__main__":
    main()

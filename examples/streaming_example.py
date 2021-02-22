#!/usr/bin/env python
# coding: utf-8

# EXAMPLE DESC: TODO

import wave
from typing import Iterator

import grpc
from google.protobuf.empty_pb2 import Empty

from ondewo.s2t import speech_to_text_pb2, speech_to_text_pb2_grpc

# Set up the parameters of the grpc server.
# The example below is for the case when server is running locally
MAX_MESSAGE_LENGTH: int = 6 * 1024 * 1024  # max message length in bytes
GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50655"
CHANNEL: str = f"{GRPC_HOST}:{GRPC_PORT}"

AUDIO_FILE: str = "examples/audiofiles/sample_2.wav"
CHUNK_SIZE: int = 8000


def create_stub():
    options = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ]
    channel = grpc.insecure_channel(CHANNEL, options=options)
    stub = speech_to_text_pb2_grpc.Speech2TextStub(channel=channel)

    return stub


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
        audio_chunk=b'',
        s2t_pipeline_id=pipeline_id,
        spelling_correction=False,
        ctc_decoding=speech_to_text_pb2.CTCDecoding.GREEDY,
        end_of_stream=True,
    )


def main():
    stub = create_stub()

    # List all speech-2-text pipelines (model setups) present on the server
    # We are going to pick the first pipeline (model setup)
    pipelines = stub.ListS2tPipelines(request=Empty()).pipeline_configs
    pipeline = pipelines[0]

    # Get audio stream (iterator of audio chunks)
    audio_stream: Iterator[bytes] = get_streaming_audio(AUDIO_FILE)

    # Create streaming request
    streaming_request: Iterator[speech_to_text_pb2.TranscribeStreamRequest] = \
        create_streaming_request(audio_stream=audio_stream, pipeline_id=pipeline.id)

    # Transcribe the stream and get back responses
    response_gen: Iterator[speech_to_text_pb2.TranscribeStreamResponse] = \
        stub.TranscribeStream(streaming_request)

    # Print transcribed utterances
    for i, response_chunk in enumerate(response_gen):
        print(response_chunk.transcription)


if __name__ == '__main__':
    main()
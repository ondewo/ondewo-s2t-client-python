#!/usr/bin/env python
# coding: utf-8

# EXAMPLE DESC: TODO

import wave

import grpc
from google.protobuf.empty_pb2 import Empty

from ondewo.s2t import speech_to_text_pb2, speech_to_text_pb2_grpc

# Set up the parameters of the grpc server.
# The example below is for the case when server is running locally
MAX_MESSAGE_LENGTH: int = 6 * 1024 * 1024  # max message length in bytes
GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50655"
CHANNEL: str = f"{GRPC_HOST}:{GRPC_PORT}"

AUDIO_FILE: str = "examples/audiofiles/sample_1.wav"


def create_stub():
    options = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ]
    channel = grpc.insecure_channel(CHANNEL, options=options)
    stub = speech_to_text_pb2_grpc.Speech2TextStub(channel=channel)

    return stub


def main():
    stub = create_stub()

    # List all speech-2-text pipelines (model setups) present on the server
    # We are going to pick the first pipeline (model setup)
    pipelines = stub.ListS2tPipelines(request=Empty()).pipeline_configs
    pipeline = pipelines[0]

    # Read file which we want to transcribe
    with wave.open(AUDIO_FILE) as w:
        audio: bytes = w.readframes(w.getnframes())

    # Create transcription request
    request = speech_to_text_pb2.TranscribeFileRequest(
        s2t_pipeline_id=pipeline.id,
        audio_file=audio,
        ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM
    )
    # Send transcription request and get response
    transcribe_response = stub.TranscribeFile(request=request)

    print(f"File transcript: {transcribe_response.transcription}")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import queue
import signal
import time
import wave
from datetime import datetime
from typing import Union, Dict, Any, Iterator

from google.protobuf.empty_pb2 import Empty
from ondewo.s2t import grpc_utils, speech_to_text_pb2
from ondewo.s2t.speech_to_text_pb2 import TranscribeStreamRequest
from ondewo.s2t.speech_to_text_pb2_grpc import Speech2TextStub

FORMAT: str = "%(levelname)s%(asctime)s -- \"%(message)s\""
logging.basicConfig(level=logging.INFO, format=FORMAT)

DATA_PASS: int = 16000
CHUNK: int = 8000
PATH: str = os.path.dirname(os.path.realpath(__file__))
FILE: str = PATH + "/long.wav"


settings_base = {
    's2t_grpc_config': 'secure_grpc.json',
    'language': 'de-DE',
    'ctc_decoding': 'language-model',
    'session_id': datetime.now().strftime("%Y-%m-%d--%H-%M-%S-%f"),
    'output_style': 'simple',
}


class PyAudioStreamer:
    def __init__(self) -> None:
        # So you dont have to install these things to use the file test
        try:
            import pyaudio
        except ModuleNotFoundError:
            logging.info(
                "\n\nYou don't appear to have PyAudio installed."
                " Please install pyaudio. There is a script in"
                " ./examples/scripts/ that will help.\n\n"
            )
            raise
        # os.system("pactl load-module module-loopback latency_msec=10")
        self.CHUNK: int = CHUNK
        self.pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
        self.stream: pyaudio.Stream = self.pyaudio_object.open(
            channels=1,
            format=pyaudio.paInt16,
            rate=16000,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

    def close(self) -> None:
        self.stream.close()
        self.pyaudio_object.terminate()
        os.system("pactl unload-module module-loopback")


class PySoundIoStreamer:
    def __init__(self) -> None:
        # ibid.
        try:
            import pysoundio
        except ModuleNotFoundError:
            logging.info(
                "\n\nYou don't appear to have PySoundIo installed."
                " You may need to install libsoundio to use it:\n\n"
                "apt install -y libsoundio-dev\n\n"
                "then\n\n"
                "pip install pysoundio\n\n"
            )
            raise
        self.CHUNK: int = CHUNK
        self.pysoundio_object: pysoundio.PySoundIo = pysoundio.PySoundIo(backend=None)
        self.buffer: queue.Queue = queue.Queue(maxsize=CHUNK * 50)
        logging.info("Starting stream")
        self.pysoundio_object.start_input_stream(
            device_id=None,
            channels=1,
            sample_rate=16000,
            block_size=self.CHUNK,
            dtype=pysoundio.SoundIoFormatS16LE,
            read_callback=self.callback,
        )

    def callback(self, data: bytes, length: int) -> None:
        self.buffer.put(data)

    def close(self) -> None:
        pass
        # self.pysoundio_object.close()    # this hangs


class FileStreamer:
    def __init__(self) -> None:
        self.CHUNK: int = CHUNK
        self.wf = wave.open(FILE, 'rb')

    def close(self) -> None:
        self.wf.close()


class Streamer:
    def __init__(self, streamer: str, settings: Dict[str, Any], stop: asyncio.Future) -> None:
        self.settings = settings
        self.stop: asyncio.Future = stop

        if streamer == "file":
            self.streamer: Union[FileStreamer, PyAudioStreamer, PySoundIoStreamer] = FileStreamer()
        elif streamer == "pyaudio":
            self.streamer = PyAudioStreamer()
        elif streamer == "pysoundio":
            self.streamer = PySoundIoStreamer()
        else:
            raise AttributeError(f"Streamer {streamer} does not exist.")

    def register_with_server(self) -> None:
        stub: Speech2TextStub = grpc_utils.create_stub(settings['s2t_grpc_config'], True)
        pipelines = stub.ListS2tPipelines(request=Empty()).pipeline_configs
        pipeline_id: str = pipelines[0].id

        logging.warning("Starting stream transmission")
        self.stream_over_grpc(stub, pipeline_id)

        self.streamer.close()
        logging.warning("Stream transmission ended")

    def stream_over_grpc(self, stub: Speech2TextStub, pipeline_id: str) -> None:
        if isinstance(self.streamer, FileStreamer):
            self.stream_file_to_grpc(stub, pipeline_id)
        elif isinstance(self.streamer, PyAudioStreamer):
            self.stream_pyaudio_to_grpc(stub, pipeline_id)
        elif isinstance(self.streamer, PySoundIoStreamer):
            self.stream_pysoundio_to_grpc(stub, pipeline_id)

    def stream_pysoundio_to_grpc(self, stub: Speech2TextStub, pipeline_id: str) -> None:
        for response in stub.TranscribeStream(self.get_pysoundio_stream_request(pipeline_id)):
            logging.info(f"Response: {response.transcription}")

        logging.warning("Streamer nice and broken :)")

    def get_pysoundio_stream_request(self, pipeline_id: str) -> Iterator[TranscribeStreamRequest]:
        count = 0
        data_save = bytes()
        while not self.stop.done():
            count += 1
            if not count % 1000:
                logging.warning(f"Writing {count}th byte packet")
            data: bytes = self.streamer.buffer.get()        # type: ignore
            data_save += data
            if len(data_save) < DATA_PASS:
                continue
            logging.info(f"Sending {len(data_save)} bytes")
            yield TranscribeStreamRequest(
                audio_chunk=data,
                s2t_pipeline_id=pipeline_id,
                spelling_correction=False,
                ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
                end_of_stream=False,
            )
            data_save = bytes()
            time.sleep(0.1)

    def stream_pyaudio_to_grpc(self, stub: Speech2TextStub, pipeline_id: str) -> None:
        for response in stub.TranscribeStream(self.get_pyaudio_stream_request(pipeline_id)):
            logging.info(f"Response: {response.transcription}")

        logging.warning("Streamer nice and broken :)")

    def get_pyaudio_stream_request(self, pipeline_id: str) -> Iterator[TranscribeStreamRequest]:
        while not self.stop.done():
            chunk: bytes = self.streamer.stream.read(self.streamer.CHUNK)
            yield TranscribeStreamRequest(
                audio_chunk=chunk,
                s2t_pipeline_id=pipeline_id,
                spelling_correction=False,
                ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
                end_of_stream=False,
            )
            time.sleep(0.1)

    def stream_file_to_grpc(self, stub: Speech2TextStub, pipeline_id: str) -> None:
        for response in stub.TranscribeStream(self.get_file_stream_request(pipeline_id)):
            logging.info(f"Response: {response.transcription}")

        logging.warning("Streamer nice and broken :)")

    def get_file_stream_request(self, pipeline_id: str) -> Iterator[TranscribeStreamRequest]:
        while not self.stop.done():
            chunk: bytes = self.streamer.wf.readframes(self.streamer.CHUNK)
            if not chunk:
                yield TranscribeStreamRequest(
                    audio_chunk=chunk,
                    s2t_pipeline_id=pipeline_id,
                    spelling_correction=False,
                    ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
                    end_of_stream=True,
                )
                break
            logging.info(f"Sending {len(chunk)} bytes")
            yield TranscribeStreamRequest(
                audio_chunk=chunk,
                s2t_pipeline_id=pipeline_id,
                spelling_correction=False,
                ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
                end_of_stream=False,
            )
            time.sleep(0.1)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument('--streamer', default='file', help='file, pyaudio or pysoundio streamer')
    parser.add_argument('--language', default="de-DE", type=str)

    args: argparse.Namespace = parser.parse_args()
    stop: asyncio.Future = asyncio.Future()
    settings = settings_base
    settings["language"] = args.language
    s: Streamer = Streamer(args.streamer, settings, stop)

    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    logging.info("Starting server!")
    loop.run_until_complete(s.register_with_server())

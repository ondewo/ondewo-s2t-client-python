import json

import grpc

from ondewo.s2t import speech_to_text_pb2_grpc

MAX_MESSAGE_LENGTH: int = 6 * 1024 * 1024  # max message length in bytes


def create_stub(config_file: str, is_secure: bool = False):
    with open(config_file) as json_file:
        config = json.load(json_file)
    channel_name: str = f"{config['host']}:{config['port']}"

    options = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ]
    if is_secure:
        if not config.get('grpc_cert'):
            raise ValueError("Missing GRPC certificate (grpc_cert) in the provided config file!")
        credentials = grpc.ssl_channel_credentials(root_certificates=bytes(config['grpc_cert'], encoding="UTF8"))
        channel = grpc.secure_channel(channel_name,
                                      credentials,
                                      options=options)
    else:
        channel = grpc.insecure_channel(channel_name, options=options)

    stub = speech_to_text_pb2_grpc.Speech2TextStub(channel=channel)
    return stub

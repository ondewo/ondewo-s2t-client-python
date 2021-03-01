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

from typing import Any

from ondewo.s2t.speech_to_text_pb2_grpc import Speech2TextStub
from ondewo.utils.base_services_interface import BaseServicesInterface


class Speech2Text(BaseServicesInterface):

    @property
    def stub(self) -> Any:
        stub: Speech2TextStub = Speech2TextStub(channel=self.grpc_channel)

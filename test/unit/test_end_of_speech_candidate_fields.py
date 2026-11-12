# Copyright 2021-2026 ONDEWO GmbH
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
"""Pin the wire numbers of the end-of-speech candidate fields.

ondewo-s2t and ondewo-csi exchange these two fields by NUMBER on the wire, so a renumbering on regeneration would
silently make a server and a client talk past each other. Both must stay field 9.
"""

from ondewo.s2t import speech_to_text_pb2


def test_the_end_of_speech_candidate_fields_keep_their_wire_numbers() -> None:
    """Both fields are number 9, and a set flag survives a serialisation round trip."""
    assert speech_to_text_pb2.TranscriptionReturnOptions.RETURN_END_OF_SPEECH_CANDIDATE_FIELD_NUMBER == 9
    assert speech_to_text_pb2.TranscribeStreamResponse.END_OF_SPEECH_CANDIDATE_FIELD_NUMBER == 9

    response: speech_to_text_pb2.TranscribeStreamResponse = speech_to_text_pb2.TranscribeStreamResponse(
        end_of_speech_candidate=True,
    )
    assert response.SerializeToString() == b"H\x01"
    assert speech_to_text_pb2.TranscribeStreamResponse.FromString(b"H\x01").end_of_speech_candidate is True
    assert speech_to_text_pb2.TranscribeStreamResponse().end_of_speech_candidate is False

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
"""Unit tests for the service-wrapper code generator.

`ondewo/s2t/scripts/generate_services.py` is what produces
`ondewo/s2t/client/services/{,async_}speech_to_text.py`, `{,async_}services_container.py` and
`{,async_}client.py` from `ondewo-s2t-api/ondewo/s2t/speech-to-text.proto`. It is a developer
tool rather than SDK runtime code, but it is hand-written, non-trivial (a hand-rolled proto
parser plus a code emitter) and a regression in it silently ships a broken client, so it is
gated at the same 100% as the rest of the hand-written surface.

Everything here is hermetic: protos are written into `tmp_path` and the generator's output is
asserted as text (and, for the integration cases, `compile()`d to prove it is valid Python).
"""

import textwrap
from pathlib import Path
from typing import (
    Dict,
    List,
)

import pytest

from ondewo.s2t.scripts.generate_services import (
    _build_client_content,
    _build_file_content,
    _build_services_container_content,
    _emit_import_group,
    _emit_method,
    _MAX_LINE_LENGTH,
    _strip_proto_comments,
    camel_to_snake,
    main,
    parse_proto_file,
    proto_stem_to_file_name,
    resolve_type,
    RpcMethod,
    ServiceDef,
)

# The single proto this repo actually generates from, plus the two external-module names used to
# exercise the grouped-import branch. Bound once so a test cannot drift into tautology.
S2T_STEM: str = "speech_to_text"
S2T_TYPES: Dict[str, str] = {
    "TranscribeFileRequest": "speech_to_text",
    "TranscribeFileResponse": "speech_to_text",
    "TranscribeStreamRequest": "speech_to_text",
    "TranscribeStreamResponse": "speech_to_text",
    "S2tPipelineId": "speech_to_text",
    "ListS2tPipelinesRequest": "common",
    "ListS2tPipelinesResponse": "common",
}


def _write_proto(directory: Path, name: str, content: str) -> Path:
    """Write a dedented .proto source into `directory` and return its path.

    Args:
        directory (Path):
            Directory the file is written into; must already exist.
        name (str):
            File name including the `.proto` suffix.
        content (str):
            Proto source, indented freely — it is passed through `textwrap.dedent`.

    Returns:
        Path:
            The path of the written proto file.
    """
    path: Path = directory / name
    path.write_text(textwrap.dedent(content))
    return path


def _make_svc(
    rpcs: List[RpcMethod],
    proto_stem: str = S2T_STEM,
    name: str = "Speech2Text",
) -> ServiceDef:
    """Build a `ServiceDef` for the emitter tests.

    Args:
        rpcs (List[RpcMethod]):
            The RPCs the rendered service class exposes.
        proto_stem (str):
            Proto stem the service came from; drives the `_pb2` module names.
        name (str):
            Service name as written in the proto.

    Returns:
        ServiceDef:
            The assembled service definition.
    """
    return ServiceDef(name=name, rpcs=rpcs, proto_stem=proto_stem)


class TestCamelToSnake:
    """`camel_to_snake` splits only where a lowercase/digit is followed by an uppercase letter."""

    def test_single_word(self) -> None:
        """A single PascalCase word lowercases with no separator."""
        assert camel_to_snake("Transcribe") == "transcribe"

    def test_two_words(self) -> None:
        """Two words are separated by one underscore."""
        assert camel_to_snake("TranscribeFile") == "transcribe_file"

    def test_four_words(self) -> None:
        """Every lowercase-to-uppercase boundary gets a separator."""
        assert camel_to_snake("ListS2tPipelineLanguages") == "list_s2t_pipeline_languages"

    def test_digit_before_uppercase_separates(self) -> None:
        """A digit counts as a lowercase for the boundary rule: `Speech2Text` -> `speech2_text`."""
        assert camel_to_snake("Speech2Text") == "speech2_text"

    def test_leading_all_caps_acronym_is_one_word(self) -> None:
        """With no lowercase before the uppercase run, no separator is inserted."""
        assert camel_to_snake("AIServices") == "aiservices"

    def test_mixed_case_acronym_separates(self) -> None:
        """A lowercase letter before the uppercase run does insert a separator."""
        assert camel_to_snake("AiServices") == "ai_services"

    def test_already_snake_case_is_unchanged(self) -> None:
        """An already-snake_case name passes through untouched."""
        assert camel_to_snake("transcribe_file") == "transcribe_file"


class TestProtoStemToFileName:
    """`proto_stem_to_file_name` returns the stem verbatim in this repo (no pluralisation)."""

    def test_stem_is_returned_verbatim(self) -> None:
        """The S2T stem must reach the service file name unchanged."""
        assert proto_stem_to_file_name(S2T_STEM) == S2T_STEM

    @pytest.mark.parametrize("stem", ["agent", "utility", "operations"])
    def test_no_pluralisation_is_applied(self, stem: str) -> None:
        """The nlu pluralisation rules are dead here; every stem round-trips unchanged.

        Args:
            stem (str):
                A stem shaped like one of nlu's pluralisation cases (`+s`, `y -> ies`, `s`).
        """
        assert proto_stem_to_file_name(stem) == stem


class TestStripProtoComments:
    """`_strip_proto_comments` removes comments without damaging string literals."""

    def test_line_comment_removed(self) -> None:
        """A `//` line comment is stripped."""
        assert "gone" not in _strip_proto_comments("int32 a = 1; // gone\n")

    def test_block_comment_removed_across_lines(self) -> None:
        """A `/* */` block comment is stripped even when it spans lines."""
        assert "gone" not in _strip_proto_comments("/* first\n gone\n */ int32 a = 1;")

    def test_comment_markers_inside_string_literals_survive(self) -> None:
        """`//` and `/*` inside a quoted string must not trigger comment removal."""
        source: str = 'option (google.api.http) = { get: "http://example.com/v1/*" };'
        assert _strip_proto_comments(source) == source


class TestResolveType:
    """`resolve_type` maps a proto type onto (annotation, local pb2 name, external import line)."""

    def test_local_bare_type(self) -> None:
        """A type owned by the current proto is imported from the local `_pb2` module."""
        annot, local, ext = resolve_type("TranscribeFileRequest", S2T_STEM, S2T_TYPES)
        assert (annot, local, ext) == ("TranscribeFileRequest", "TranscribeFileRequest", None)

    def test_ondewo_s2t_prefix_is_stripped(self) -> None:
        """A fully qualified `ondewo.s2t.X` resolves exactly like the bare `X`."""
        annot, local, ext = resolve_type("ondewo.s2t.TranscribeFileRequest", S2T_STEM, S2T_TYPES)
        assert (annot, local, ext) == ("TranscribeFileRequest", "TranscribeFileRequest", None)

    def test_nested_message_keeps_dotted_annotation_but_imports_root(self) -> None:
        """`Parent.Child` annotates dotted while only `Parent` is imported."""
        annot, local, ext = resolve_type("S2tPipelineId.Inner", S2T_STEM, S2T_TYPES)
        assert annot == "S2tPipelineId.Inner"
        assert local == "S2tPipelineId"
        assert ext is None

    def test_google_protobuf_empty(self) -> None:
        """`google.protobuf.Empty` becomes an `empty_pb2` import and no local name."""
        annot, local, ext = resolve_type("google.protobuf.Empty", S2T_STEM, {})
        assert annot == "Empty"
        assert local is None
        assert ext == "from google.protobuf.empty_pb2 import Empty"

    def test_google_protobuf_module_name_is_snake_cased(self) -> None:
        """A multi-word well-known type derives its module via `camel_to_snake`."""
        _, _, ext = resolve_type("google.protobuf.FieldMask", S2T_STEM, {})
        assert ext == "from google.protobuf.field_mask_pb2 import FieldMask"

    def test_type_from_another_proto_becomes_an_external_import(self) -> None:
        """A type owned by a different stem is imported from that stem's `_pb2` module."""
        annot, local, ext = resolve_type("ListS2tPipelinesRequest", S2T_STEM, S2T_TYPES)
        assert annot == "ListS2tPipelinesRequest"
        assert local is None
        assert ext == "from ondewo.s2t.common_pb2 import ListS2tPipelinesRequest"

    def test_unknown_type_falls_back_to_local_with_warning(self, capsys: pytest.CaptureFixture) -> None:
        """A type in no registry is treated as local and reported on stderr.

        Args:
            capsys (pytest.CaptureFixture):
                Fixture capturing the generator's stderr warning.
        """
        annot, local, ext = resolve_type("MysteryRequest", S2T_STEM, {})
        assert (annot, local, ext) == ("MysteryRequest", "MysteryRequest", None)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "MysteryRequest" in captured.err


class TestParseProtoFile:
    """`parse_proto_file` turns proto source into `ProtoFile` (messages + services + RPCs)."""

    def test_unary_rpc(self, tmp_path: Path) -> None:
        """A plain unary RPC parses with both streaming flags false.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            """,
        )
        parsed = parse_proto_file(proto)
        assert len(parsed.services) == 1
        service = parsed.services[0]
        assert service.name == "Speech2Text"
        assert service.proto_stem == S2T_STEM
        rpc = service.rpcs[0]
        assert (rpc.name, rpc.request_type, rpc.response_type) == (
            "TranscribeFile",
            "TranscribeFileRequest",
            "TranscribeFileResponse",
        )
        assert not rpc.client_streaming
        assert not rpc.server_streaming

    def test_dashes_in_file_name_become_underscores_in_the_stem(self, tmp_path: Path) -> None:
        """`speech-to-text.proto` must yield the importable stem `speech_to_text`.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            message TranscribeFileRequest { string a = 1; }
            """,
        )
        assert parse_proto_file(proto).stem == S2T_STEM

    def test_bidirectional_streaming_flags(self, tmp_path: Path) -> None:
        """`stream` on both sides sets both streaming flags.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
                rpc TranscribeStream (stream TranscribeStreamRequest) returns (stream TranscribeStreamResponse);
            }
            """,
        )
        rpc = parse_proto_file(proto).services[0].rpcs[0]
        assert rpc.client_streaming is True
        assert rpc.server_streaming is True

    def test_rpc_body_with_option_braces(self, tmp_path: Path) -> None:
        """Braces inside an RPC option block must not confuse the service-body brace counter.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse) {
                    option (google.api.http) = { post: "/v1/s2t:transcribe" };
                }
            }
            """,
        )
        assert [r.name for r in parse_proto_file(proto).services[0].rpcs] == ["TranscribeFile"]

    def test_duplicate_rpc_is_skipped_with_warning(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """A repeated RPC name is emitted once and reported on stderr.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
            capsys (pytest.CaptureFixture):
                Fixture capturing the generator's stderr warning.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            """,
        )
        assert len(parse_proto_file(proto).services[0].rpcs) == 1
        captured = capsys.readouterr()
        assert "duplicate" in captured.err.lower()
        assert "TranscribeFile" in captured.err

    def test_service_without_rpcs_is_dropped(self, tmp_path: Path) -> None:
        """An empty service block produces no `ServiceDef`.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
            }
            """,
        )
        assert parse_proto_file(proto).services == []

    def test_multiple_services(self, tmp_path: Path) -> None:
        """Two service blocks in one proto both parse, in declaration order.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            service Speech2TextAdmin {
                rpc ListS2tPipelines (ListS2tPipelinesRequest) returns (ListS2tPipelinesResponse);
            }
            """,
        )
        assert [s.name for s in parse_proto_file(proto).services] == ["Speech2Text", "Speech2TextAdmin"]

    def test_nested_messages_are_recorded_dotted(self, tmp_path: Path) -> None:
        """Nested messages appear as `Parent.Child`; only the parent is top-level.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            message S2tPipelineId {
                message Inner {
                    string value = 1;
                }
                enum Kind { UNSPECIFIED = 0; }
                string name = 1;
            }
            message TranscribeFileRequest { string a = 1; }
            """,
        )
        parsed = parse_proto_file(proto)
        assert parsed.top_messages == {"S2tPipelineId", "TranscribeFileRequest"}
        assert "S2tPipelineId.Inner" in parsed.messages

    def test_comments_do_not_produce_phantom_rpcs(self, tmp_path: Path) -> None:
        """A commented-out RPC must not be parsed.

        Args:
            tmp_path (Path):
                Fixture directory the proto is written to.
        """
        proto: Path = _write_proto(
            tmp_path,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
                // rpc Removed (TranscribeFileRequest) returns (TranscribeFileResponse);
                /* rpc AlsoRemoved (TranscribeFileRequest) returns (TranscribeFileResponse); */
            }
            """,
        )
        assert [r.name for r in parse_proto_file(proto).services[0].rpcs] == ["TranscribeFile"]


class TestEmitImportGroup:
    """`_emit_import_group` collapses same-module imports into one parenthesised block."""

    def test_single_name_stays_on_one_line(self) -> None:
        """One name from a module is emitted inline."""
        lines: List[str] = []
        _emit_import_group(lines, {"from ondewo.s2t.common_pb2 import ListS2tPipelinesRequest"})
        assert lines == ["from ondewo.s2t.common_pb2 import ListS2tPipelinesRequest"]

    def test_multiple_names_are_grouped_and_sorted(self) -> None:
        """Two names from one module become a sorted parenthesised block."""
        lines: List[str] = []
        _emit_import_group(
            lines,
            {
                "from ondewo.s2t.common_pb2 import ListS2tPipelinesResponse",
                "from ondewo.s2t.common_pb2 import ListS2tPipelinesRequest",
            },
        )
        assert lines == [
            "from ondewo.s2t.common_pb2 import (",
            "    ListS2tPipelinesRequest,",
            "    ListS2tPipelinesResponse,",
            ")",
        ]

    def test_modules_are_emitted_in_sorted_order(self) -> None:
        """Distinct modules are emitted alphabetically."""
        lines: List[str] = []
        _emit_import_group(
            lines,
            {
                "from ondewo.s2t.common_pb2 import ListS2tPipelinesRequest",
                "from google.protobuf.empty_pb2 import Empty",
            },
        )
        assert lines == [
            "from google.protobuf.empty_pb2 import Empty",
            "from ondewo.s2t.common_pb2 import ListS2tPipelinesRequest",
        ]

    def test_unparseable_import_line_is_ignored(self) -> None:
        """A line that is not a `from X import Y` is dropped rather than mis-emitted."""
        lines: List[str] = []
        _emit_import_group(lines, {"import grpc"})
        assert lines == []


class TestEmitMethod:
    """`_emit_method` renders one wrapper method, wrapping lines over the 120-char budget."""

    def test_unary_sync_method(self) -> None:
        """The short-line path emits a one-line signature and a one-line body."""
        out: List[str] = _emit_method(
            RpcMethod("TranscribeFile", "TranscribeFileRequest", "TranscribeFileResponse", False, False),
            "TranscribeFileRequest",
            "TranscribeFileResponse",
        )
        assert "    def transcribe_file(self, request: TranscribeFileRequest) -> TranscribeFileResponse:" in out
        assert (
            "        response: TranscribeFileResponse = "
            "self.stub.TranscribeFile(request, metadata=self.metadata)" in out
        )
        assert out[-1] == "        return response"

    def test_async_method_uses_async_await_and_async_iterator(self) -> None:
        """`for_async=True` adds `async`/`await` and swaps `Iterator` for `AsyncIterator`."""
        out: List[str] = _emit_method(
            RpcMethod("TranscribeStream", "TranscribeStreamRequest", "TranscribeStreamResponse", True, True),
            "TranscribeStreamRequest",
            "TranscribeStreamResponse",
            for_async=True,
        )
        joined: str = "\n".join(out)
        assert "async def transcribe_stream(" in joined
        assert "AsyncIterator[TranscribeStreamRequest]" in joined
        assert "AsyncIterator[TranscribeStreamResponse]" in joined
        assert "await self.stub.TranscribeStream(request_iterator, metadata=self.metadata)" in joined

    def test_client_streaming_renames_the_parameter(self) -> None:
        """A client-streaming RPC takes `request_iterator`, not `request`."""
        out: List[str] = _emit_method(
            RpcMethod("TranscribeStream", "TranscribeStreamRequest", "TranscribeStreamResponse", True, False),
            "TranscribeStreamRequest",
            "TranscribeStreamResponse",
        )
        assert (
            "    def transcribe_stream(self, request_iterator: Iterator[TranscribeStreamRequest]) "
            "-> TranscribeStreamResponse:" in out
        )

    def test_long_signature_is_wrapped(self) -> None:
        """A signature over the budget is split across parameter lines, all within the budget."""
        rpc_name: str = "GetAlternativeTranscriptionsForLongRunningStreamingSessions"
        request_type: str = f"{rpc_name}Request"
        response_type: str = f"{rpc_name}Response"
        out: List[str] = _emit_method(
            RpcMethod(rpc_name, request_type, response_type, False, False),
            request_type,
            response_type,
        )
        assert "    def get_alternative_transcriptions_for_long_running_streaming_sessions(" in out
        assert "        self," in out
        assert f"        request: {request_type}," in out
        assert f"    ) -> {response_type}:" in out
        assert all(len(line) <= _MAX_LINE_LENGTH for line in out)

    def test_long_body_uses_backslash_continuation(self) -> None:
        """A signature that fits but a body that does not splits only the body."""
        rpc_name: str = "ListS2tPipelineLanguageModels"
        response_type: str = f"{rpc_name}Response"
        out: List[str] = _emit_method(
            RpcMethod(rpc_name, "Req", response_type, False, False),
            "Req",
            response_type,
        )
        assert f"    def list_s2t_pipeline_language_models(self, request: Req) -> {response_type}:" in out
        assert f"        response: {response_type} = \\" in out
        assert f"            self.stub.{rpc_name}(request, metadata=self.metadata)" in out
        assert all(len(line) <= _MAX_LINE_LENGTH for line in out)


class TestBuildFileContent:
    """`_build_file_content` renders a complete service-wrapper module."""

    def test_sync_module_header_and_class(self) -> None:
        """The sync file imports the sync interface and subclasses it."""
        content: str = _build_file_content(
            _make_svc([RpcMethod("TranscribeFile", "TranscribeFileRequest", "TranscribeFileResponse", False, False)]),
            S2T_TYPES,
        )
        assert "from ondewo.s2t.client.services_interface import ServicesInterface" in content
        assert "class Speech2Text(ServicesInterface):" in content
        assert f"See {S2T_STEM}.proto." in content
        assert f"from ondewo.s2t.{S2T_STEM}_pb2_grpc import Speech2TextStub" in content
        assert "    def stub(self) -> Speech2TextStub:" in content
        assert "Speech2TextStub(channel=self.grpc_channel)" in content

    def test_async_module_header_and_class(self) -> None:
        """The async file imports the async interface and subclasses it."""
        content: str = _build_file_content(
            _make_svc([RpcMethod("TranscribeFile", "TranscribeFileRequest", "TranscribeFileResponse", False, False)]),
            S2T_TYPES,
            for_async=True,
        )
        assert "from ondewo.s2t.client.async_services_interface import AsyncServicesInterface" in content
        assert "class Speech2Text(AsyncServicesInterface):" in content

    def test_no_typing_import_when_nothing_streams(self) -> None:
        """A purely unary service needs no `Iterator` import."""
        content: str = _build_file_content(
            _make_svc([RpcMethod("TranscribeFile", "TranscribeFileRequest", "TranscribeFileResponse", False, False)]),
            S2T_TYPES,
        )
        assert "from typing import" not in content

    def test_streaming_adds_the_iterator_import(self) -> None:
        """A streaming RPC pulls in `Iterator` (sync) / `AsyncIterator` (async)."""
        svc: ServiceDef = _make_svc(
            [RpcMethod("TranscribeStream", "TranscribeStreamRequest", "TranscribeStreamResponse", False, True)]
        )
        assert "from typing import Iterator" in _build_file_content(svc, S2T_TYPES)
        assert "from typing import AsyncIterator" in _build_file_content(svc, S2T_TYPES, for_async=True)

    def test_local_types_are_sorted_and_deduplicated(self) -> None:
        """Types owned by this proto go into one sorted `_pb2` block with no repeats."""
        content: str = _build_file_content(
            _make_svc(
                [
                    RpcMethod("TranscribeFile", "TranscribeFileRequest", "TranscribeFileResponse", False, False),
                    RpcMethod("TranscribeAgain", "TranscribeFileRequest", "TranscribeFileResponse", False, False),
                ]
            ),
            S2T_TYPES,
        )
        assert (
            f"from ondewo.s2t.{S2T_STEM}_pb2 import (\n"
            "    TranscribeFileRequest,\n"
            "    TranscribeFileResponse,\n"
            ")" in content
        )

    def test_google_import_is_emitted_before_the_interface_import(self) -> None:
        """A `google.protobuf` type is imported from its own module, not the local `_pb2` block."""
        content: str = _build_file_content(
            _make_svc([RpcMethod("StopServer", "TranscribeFileRequest", "google.protobuf.Empty", False, False)]),
            S2T_TYPES,
        )
        assert "from google.protobuf.empty_pb2 import Empty" in content
        assert content.index("from google.protobuf.empty_pb2 import Empty") < content.index(
            "from ondewo.s2t.client.services_interface import ServicesInterface"
        )
        assert "    Empty,\n" not in content

    def test_external_module_types_are_grouped(self) -> None:
        """Two types owned by another proto share one parenthesised import block."""
        content: str = _build_file_content(
            _make_svc(
                [RpcMethod("ListS2tPipelines", "ListS2tPipelinesRequest", "ListS2tPipelinesResponse", False, False)]
            ),
            S2T_TYPES,
        )
        assert (
            "from ondewo.s2t.common_pb2 import (\n"
            "    ListS2tPipelinesRequest,\n"
            "    ListS2tPipelinesResponse,\n"
            ")" in content
        )

    def test_rendered_module_is_valid_python(self) -> None:
        """The emitted source must at least compile."""
        content: str = _build_file_content(
            _make_svc(
                [
                    RpcMethod("TranscribeFile", "TranscribeFileRequest", "TranscribeFileResponse", False, False),
                    RpcMethod("TranscribeStream", "TranscribeStreamRequest", "TranscribeStreamResponse", True, True),
                    RpcMethod("StopServer", "TranscribeFileRequest", "google.protobuf.Empty", False, False),
                ]
            ),
            S2T_TYPES,
        )
        compile(content, "speech_to_text.py", "exec")


class TestBuildServicesContainerContent:
    """`_build_services_container_content` renders the dataclass wiring the services together."""

    def test_sync_container(self) -> None:
        """The sync container imports the sync service module and names the sync class."""
        content: str = _build_services_container_content([(S2T_STEM, "Speech2Text")])
        assert f"from ondewo.s2t.client.services.{S2T_STEM} import Speech2Text" in content
        assert "class ServicesContainer(BaseServicesContainer):" in content
        assert f"    {S2T_STEM}: Speech2Text" in content
        compile(content, "services_container.py", "exec")

    def test_async_container(self) -> None:
        """The async container imports the `async_`-prefixed module and names the async class."""
        content: str = _build_services_container_content([(S2T_STEM, "Speech2Text")], for_async=True)
        assert f"from ondewo.s2t.client.services.async_{S2T_STEM} import Speech2Text" in content
        assert "class AsyncServicesContainer(BaseServicesContainer):" in content
        compile(content, "async_services_container.py", "exec")


class TestBuildClientContent:
    """`_build_client_content` renders the client that instantiates the services container."""

    def test_sync_client(self) -> None:
        """The sync client extends `BaseClient` and builds a `ServicesContainer`."""
        content: str = _build_client_content([(S2T_STEM, "Speech2Text")])
        assert "from ondewo.utils.base_client import BaseClient" in content
        assert "class Client(BaseClient):" in content
        assert f"from ondewo.s2t.client.services.{S2T_STEM} import Speech2Text" in content
        assert "        self.services: ServicesContainer = ServicesContainer(" in content
        assert f"            {S2T_STEM}=Speech2Text(**kwargs)," in content
        compile(content, "client.py", "exec")

    def test_async_client(self) -> None:
        """The async client extends `AsyncBaseClient` and imports the `async_` service module."""
        content: str = _build_client_content([(S2T_STEM, "Speech2Text")], for_async=True)
        assert "from ondewo.utils.async_base_client import AsyncBaseClient" in content
        assert "class AsyncClient(AsyncBaseClient):" in content
        assert f"from ondewo.s2t.client.services.async_{S2T_STEM} import Speech2Text" in content
        assert "        self.services: AsyncServicesContainer = AsyncServicesContainer(" in content
        assert "The core async python client" in content
        compile(content, "async_client.py", "exec")


class TestMain:
    """End-to-end: `main` walks a proto directory and writes every generated file."""

    def test_generates_the_full_file_set(self, tmp_path: Path) -> None:
        """One service yields sync+async service files plus both containers and both clients.

        Args:
            tmp_path (Path):
                Fixture directory holding the proto input and the generated output.
        """
        proto_dir: Path = tmp_path / "protos"
        proto_dir.mkdir()
        output_dir: Path = tmp_path / "client" / "services"
        _write_proto(
            proto_dir,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            message TranscribeFileRequest { string a = 1; }
            message TranscribeFileResponse { string a = 1; }
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            """,
        )

        main(proto_dir, output_dir)

        assert output_dir.is_dir()
        service_file: Path = output_dir / f"{S2T_STEM}.py"
        async_service_file: Path = output_dir / f"async_{S2T_STEM}.py"
        assert service_file.exists()
        assert async_service_file.exists()
        for generated in (
            service_file,
            async_service_file,
            output_dir.parent / "services_container.py",
            output_dir.parent / "async_services_container.py",
            output_dir.parent / "client.py",
            output_dir.parent / "async_client.py",
        ):
            compile(generated.read_text(), generated.name, "exec")

    def test_proto_without_service_generates_no_service_file(self, tmp_path: Path) -> None:
        """A message-only proto contributes nothing to the services directory.

        Args:
            tmp_path (Path):
                Fixture directory holding the proto input and the generated output.
        """
        proto_dir: Path = tmp_path / "protos"
        proto_dir.mkdir()
        output_dir: Path = tmp_path / "client" / "services"
        _write_proto(
            proto_dir,
            "common.proto",
            """
            syntax = "proto3";
            message Foo { string bar = 1; }
            """,
        )

        main(proto_dir, output_dir)

        assert list(output_dir.glob("*.py")) == []
        assert "ServicesContainer(BaseServicesContainer):" in (output_dir.parent / "services_container.py").read_text()

    def test_two_services_in_one_proto_collide_and_warn(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Both services map to the same stem-derived file name, so the second overwrites the first.

        Args:
            tmp_path (Path):
                Fixture directory holding the proto input and the generated output.
            capsys (pytest.CaptureFixture):
                Fixture capturing the two collision warnings on stderr.
        """
        proto_dir: Path = tmp_path / "protos"
        proto_dir.mkdir()
        output_dir: Path = tmp_path / "client" / "services"
        _write_proto(
            proto_dir,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            message TranscribeFileRequest { string a = 1; }
            message TranscribeFileResponse { string a = 1; }
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            service Speech2TextAdmin {
                rpc TranscribeAgain (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            """,
        )

        main(proto_dir, output_dir)

        captured = capsys.readouterr()
        assert f"WARNING: {S2T_STEM}.py already written by speech_to_text.proto" in captured.err
        assert f"WARNING: async_{S2T_STEM}.py already written by speech_to_text.proto" in captured.err
        # The later service wins the file.
        assert "class Speech2TextAdmin(" in (output_dir / f"{S2T_STEM}.py").read_text()

    def test_message_claimed_by_two_protos_warns_and_last_wins(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """A duplicated top-level message warns; the alphabetically later proto owns the registry entry.

        The winner is observable in the output: `TranscribeFileResponse` resolves as local to
        `speech_to_text` instead of as an import from `common_pb2`.

        Args:
            tmp_path (Path):
                Fixture directory holding the proto inputs and the generated output.
            capsys (pytest.CaptureFixture):
                Fixture capturing the duplicate-message warning on stderr.
        """
        proto_dir: Path = tmp_path / "protos"
        proto_dir.mkdir()
        output_dir: Path = tmp_path / "client" / "services"
        _write_proto(
            proto_dir,
            "common.proto",
            """
            syntax = "proto3";
            message TranscribeFileResponse { string a = 1; }
            """,
        )
        _write_proto(
            proto_dir,
            "speech-to-text.proto",
            """
            syntax = "proto3";
            message TranscribeFileRequest { string a = 1; }
            message TranscribeFileResponse { string a = 1; }
            service Speech2Text {
                rpc TranscribeFile (TranscribeFileRequest) returns (TranscribeFileResponse);
            }
            """,
        )

        main(proto_dir, output_dir)

        captured = capsys.readouterr()
        assert (
            'WARNING: message "TranscribeFileResponse" defined in both common.proto and speech_to_text.proto'
        ) in captured.err
        assert "using speech_to_text.proto" in captured.err
        content: str = (output_dir / f"{S2T_STEM}.py").read_text()
        assert "    TranscribeFileResponse,\n" in content
        assert "from ondewo.s2t.common_pb2 import TranscribeFileResponse" not in content

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
"""
TLS and mutual TLS end to end: the SDK's real ``Client`` / ``AsyncClient`` against a real TLS server.

Every channel of this SDK is built by ``ondewo-client-utils`` (``ServicesInterface`` and
``AsyncServicesInterface`` only forward ``config`` / ``use_secure_channel`` / ``options``), so these tests
prove that the client identity on :class:`ClientConfig` (``grpc_client_cert`` / ``grpc_client_key``) really
reaches the handshake through the SDK, and that the library's refusals surface through it unchanged.

The server has no S2T servicer: an RPC answered ``UNIMPLEMENTED`` reached the server application, so the
handshake succeeded; a refused handshake is ``UNAVAILABLE``. ``TranscribeFile`` is used because it is not
idempotent, so the SDK's retry policy never retries it and a refusal is reported at once.
"""

import datetime
from concurrent import futures
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Optional,
)
from unittest.mock import (
    MagicMock,
    patch,
)

import grpc
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import (
    ExtendedKeyUsageOID,
    NameOID,
)

from ondewo.s2t.client.async_client import AsyncClient
from ondewo.s2t.client.client import Client
from ondewo.s2t.client.client_config import ClientConfig
from ondewo.s2t.speech_to_text_pb2 import TranscribeFileRequest

SERVER_NAME: str = "localhost"
PASSWORD: str = "pa55-w0rd-never-printed"
BEARER: List[Any] = [("authorization", "Bearer test-access-token")]


class Pki:
    """One throwaway CA with a server leaf (SAN ``localhost``) and a client leaf, all PEM bytes."""

    def __init__(self, name: str) -> None:
        self._ca_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.ca_cert: bytes = self._issue(f"{name}-ca", self._ca_key.public_key(), ca=True, issuer=None)
        ca: x509.Certificate = x509.load_pem_x509_certificate(self.ca_cert)
        server_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.server_key: bytes = _pem_key(server_key)
        self.server_cert: bytes = self._issue(
            f"{name}-server", server_key.public_key(), False, ca, ExtendedKeyUsageOID.SERVER_AUTH, SERVER_NAME
        )
        client_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.client_key: bytes = _pem_key(client_key)
        self.client_cert: bytes = self._issue(
            f"{name}-client", client_key.public_key(), False, ca, ExtendedKeyUsageOID.CLIENT_AUTH
        )

    def _issue(
        self,
        subject: str,
        public_key: ec.EllipticCurvePublicKey,
        ca: bool,
        issuer: Optional[x509.Certificate],
        usage: Optional[x509.ObjectIdentifier] = None,
        san: Optional[str] = None,
    ) -> bytes:
        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        name: x509.Name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)])
        builder: x509.CertificateBuilder = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name if issuer is None else issuer.subject)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        )
        if usage is not None:
            builder = builder.add_extension(x509.ExtendedKeyUsage([usage]), critical=False)
        if san is not None:
            builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(san)]), critical=False)
        return builder.sign(self._ca_key, hashes.SHA256()).public_bytes(serialization.Encoding.PEM)


def _pem_key(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@pytest.fixture(scope="module")
def pki() -> Pki:
    return Pki("deployment")


@pytest.fixture(scope="module")
def foreign() -> Pki:
    return Pki("foreign")


class _RecordingHandler(grpc.GenericRpcHandler):
    """Serve nothing (every RPC is ``UNIMPLEMENTED``) but record the metadata each call arrived with."""

    def __init__(self) -> None:
        self.metadata: List[Any] = []

    def service(self, handler_call_details: grpc.HandlerCallDetails) -> None:
        self.metadata.append(tuple(handler_call_details.invocation_metadata))  # type: ignore[attr-defined]
        return None


@pytest.fixture
def server() -> Iterator[Callable[[Pki, bool], int]]:
    """Start a TLS server on an ephemeral port; ``(pki, require_client_auth) -> port``."""
    servers: List[grpc.Server] = []

    def start(pki: Pki, require_client_auth: bool) -> int:
        grpc_server: grpc.Server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        grpc_server.add_generic_rpc_handlers((_RecordingHandler(),))
        credentials: grpc.ServerCredentials = grpc.ssl_server_credentials(
            [(pki.server_key, pki.server_cert)],
            root_certificates=pki.ca_cert if require_client_auth else None,
            require_client_auth=require_client_auth,
        )
        port: int = grpc_server.add_secure_port(f"{SERVER_NAME}:0", credentials)
        grpc_server.start()
        servers.append(grpc_server)
        return port

    yield start
    for grpc_server in servers:
        grpc_server.stop(grace=None)


def _config(port: int, trust: Pki, client: Optional[Pki] = None, **extra: Any) -> ClientConfig:
    """A config trusting ``trust``'s CA, presenting ``client``'s leaf when given (mutual TLS)."""
    return ClientConfig(
        host=SERVER_NAME,
        port=str(port),
        grpc_cert=trust.ca_cert.decode(),
        grpc_client_cert=None if client is None else client.client_cert.decode(),
        grpc_client_key=None if client is None else client.client_key.decode(),
        **extra,
    )


def _call(config: ClientConfig) -> grpc.StatusCode:
    """Make one real ``TranscribeFile`` through the sync ``Client``; return the status it ended with."""
    client: Client = Client(config=config, use_secure_channel=True)
    try:
        with pytest.raises(grpc.RpcError) as error:
            client.services.speech_to_text.transcribe_file(TranscribeFileRequest())
        code: grpc.StatusCode = error.value.code()  # type: ignore[attr-defined]
        return code
    finally:
        client.disconnect()


async def _async_call(config: ClientConfig) -> grpc.StatusCode:
    """Make one real ``TranscribeFile`` through the ``AsyncClient``; return the status it ended with."""
    client: AsyncClient = AsyncClient(config=config, use_secure_channel=True)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as error:
            await client.services.speech_to_text.transcribe_file(TranscribeFileRequest())
        return error.value.code()
    finally:
        await client.disconnect()


class TestSyncClient:
    def test_plain_tls_reaches_the_server(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert _call(_config(server(pki, False), pki)) is grpc.StatusCode.UNIMPLEMENTED

    def test_mutual_tls_reaches_the_server(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert _call(_config(server(pki, True), pki, client=pki)) is grpc.StatusCode.UNIMPLEMENTED

    def test_no_identity_against_a_client_auth_server_is_unavailable(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        assert _call(_config(server(pki, True), pki)) is grpc.StatusCode.UNAVAILABLE

    def test_an_identity_from_an_unrelated_ca_is_rejected(
        self, server: Callable[[Pki, bool], int], pki: Pki, foreign: Pki
    ) -> None:
        assert _call(_config(server(pki, True), pki, client=foreign)) is grpc.StatusCode.UNAVAILABLE

    def test_a_server_from_an_untrusted_ca_is_rejected(
        self, server: Callable[[Pki, bool], int], pki: Pki, foreign: Pki
    ) -> None:
        assert _call(_config(server(pki, False), foreign)) is grpc.StatusCode.UNAVAILABLE

    def test_crlf_pems_complete_the_mutual_tls_handshake(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        port: int = server(pki, True)
        config: ClientConfig = ClientConfig(
            host=SERVER_NAME,
            port=str(port),
            grpc_cert=pki.ca_cert.replace(b"\n", b"\r\n").decode(),
            grpc_client_cert=pki.client_cert.replace(b"\n", b"\r\n").decode(),
            grpc_client_key=pki.client_key.replace(b"\n", b"\r\n").decode(),
        )
        assert _call(config) is grpc.StatusCode.UNIMPLEMENTED

    def test_empty_identity_on_both_is_plain_tls(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        config: ClientConfig = ClientConfig(
            host=SERVER_NAME,
            port=str(server(pki, False)),
            grpc_cert=pki.ca_cert.decode(),
            grpc_client_cert="",
            grpc_client_key="",
        )
        assert _call(config) is grpc.StatusCode.UNIMPLEMENTED

    def test_keycloak_bearer_travels_over_mutual_tls(self, pki: Pki) -> None:
        """A Keycloak config (provider faked, no login) presents the client leaf AND sends the bearer token."""
        handler: _RecordingHandler = _RecordingHandler()
        grpc_server: grpc.Server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        grpc_server.add_generic_rpc_handlers((handler,))
        port: int = grpc_server.add_secure_port(
            f"{SERVER_NAME}:0",
            grpc.ssl_server_credentials(
                [(pki.server_key, pki.server_cert)], root_certificates=pki.ca_cert, require_client_auth=True
            ),
        )
        grpc_server.start()
        provider: MagicMock = MagicMock()
        provider.bearer_metadata.return_value = BEARER
        config: ClientConfig = _config(
            port,
            pki,
            client=pki,
            keycloak_url="https://kc.example.com/auth",
            realm="realm",
            client_id="sdk-public",
            username="tech-user",
            password=PASSWORD,
        )
        try:
            with patch("ondewo.s2t.client.services_interface.get_keycloak_token_provider", return_value=provider):
                assert _call(config) is grpc.StatusCode.UNIMPLEMENTED
        finally:
            grpc_server.stop(grace=None)
        assert ("authorization", "Bearer test-access-token") in handler.metadata[0]


class TestAsyncClient:
    async def test_plain_tls_reaches_the_server(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert await _async_call(_config(server(pki, False), pki)) is grpc.StatusCode.UNIMPLEMENTED

    async def test_mutual_tls_reaches_the_server(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert await _async_call(_config(server(pki, True), pki, client=pki)) is grpc.StatusCode.UNIMPLEMENTED

    async def test_no_identity_against_a_client_auth_server_is_unavailable(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        assert await _async_call(_config(server(pki, True), pki)) is grpc.StatusCode.UNAVAILABLE

    async def test_an_identity_from_an_unrelated_ca_is_rejected(
        self, server: Callable[[Pki, bool], int], pki: Pki, foreign: Pki
    ) -> None:
        assert await _async_call(_config(server(pki, True), pki, client=foreign)) is grpc.StatusCode.UNAVAILABLE


class TestRefusedBeforeGrpc:
    @pytest.mark.parametrize("half", ["grpc_client_cert", "grpc_client_key"])
    def test_half_an_identity_is_refused_by_the_config(self, pki: Pki, half: str) -> None:
        """grpc core would abort() the process on half a pair; the config refuses it first, naming no PEM."""
        with pytest.raises(ValueError, match="set both to use mutual TLS, or neither") as refusal:
            ClientConfig(host=SERVER_NAME, port="1", grpc_cert=pki.ca_cert.decode(), **{half: "PEM-CONTENT"})  # type: ignore[arg-type]
        assert "PEM-CONTENT" not in str(refusal.value)

    @pytest.mark.parametrize("client_class", [Client, AsyncClient])
    def test_insecure_with_an_identity_is_refused(self, pki: Pki, client_class: Any) -> None:
        with pytest.raises(ValueError, match="use a secure channel") as refusal:
            client_class(config=_config(1, pki, client=pki), use_secure_channel=False)
        assert pki.client_key.decode() not in str(refusal.value)
        assert pki.client_cert.decode() not in str(refusal.value)

    def test_repr_and_str_never_contain_the_key_or_password(self, pki: Pki) -> None:
        config: ClientConfig = _config(
            1,
            pki,
            client=pki,
            keycloak_url="https://kc.example.com/auth",
            realm="realm",
            client_id="sdk-public",
            username="tech-user",
            password=PASSWORD,
        )
        for rendered in (repr(config), str(config)):
            assert PASSWORD not in rendered
            assert "PRIVATE KEY" not in rendered
            assert pki.client_key.decode() not in rendered
            assert "grpc_client_key='***REDACTED***'" in rendered

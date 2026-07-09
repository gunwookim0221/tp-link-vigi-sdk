import json

import pytest

from vigi.crypto import calculate_digest_response
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.ipc_auth import (
    IpcAuthChallenge,
    IpcAuthConfig,
    IpcAuthService,
    build_do_auth_challenge_request,
    build_do_auth_response_request,
    parse_do_auth_challenge,
    parse_do_auth_success,
)
from vigi.transport import Request, Response, Transport, TransportConfig


class FakeTransport(Transport):
    def __init__(self, responses: list[Response]) -> None:
        super().__init__(TransportConfig(base_url="https://camera.local:20443"))
        self.responses = responses
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return self.responses.pop(0)


def test_do_auth_step1_request_creation() -> None:
    request = build_do_auth_challenge_request()

    assert request.method == "POST"
    assert request.path == "/"
    assert request.headers == {"Content-Type": "application/json"}
    assert json.loads(request.body or b"{}") == {"method": "doAuth", "params": None}


def test_do_auth_challenge_parse_allows_documented_err_code() -> None:
    challenge = parse_do_auth_challenge(
        Response(
            status_code=401,
            body=json.dumps(
                {
                    "method": "doAuth",
                    "authenticate": {
                        "realm": "TP-LINK IP-Camera",
                        "nonce": "abc123",
                        "algorithm": "SHA-256",
                        "uri": "doAuth",
                        "method": "POST",
                    },
                    "errCode": -10020,
                }
            ).encode("utf-8"),
        )
    )

    assert challenge.realm == "TP-LINK IP-Camera"
    assert challenge.nonce == "abc123"
    assert challenge.algorithm == "SHA-256"
    assert challenge.uri == "doAuth"
    assert challenge.method == "POST"
    assert challenge.err_code == -10020
    assert "abc123" not in repr(challenge)


def test_do_auth_step2_request_uses_nonce_and_response_only() -> None:
    challenge = IpcAuthChallenge(
        realm="TP-LINK IP-Camera",
        nonce="abc123",
        algorithm="SHA-256",
        uri="doAuth",
        method="POST",
        err_code=-10020,
    )

    request = build_do_auth_response_request(
        username="admin",
        password="password",
        challenge=challenge,
    )
    body = json.loads(request.body or b"{}")

    assert request.method == "POST"
    assert request.path == "/"
    assert body["method"] == "doAuth"
    assert body["params"]["nonce"] == "abc123"
    assert body["params"]["response"] == (
        "ac17ca2fb8735a42a1d2ce03671708ad1d4b9de5a181320342e5ae7683a30243"
    )
    assert "username" not in body["params"]
    assert "userName" not in body["params"]
    assert "password" not in repr(request)
    assert body["params"]["response"] not in repr(request)


def test_ipc_digest_response_reuses_existing_helper() -> None:
    response = calculate_digest_response(
        username="admin",
        password="password",
        realm="TP-LINK IP-Camera",
        nonce="abc123",
        method="POST",
        uri="doAuth",
    )

    assert response == "ac17ca2fb8735a42a1d2ce03671708ad1d4b9de5a181320342e5ae7683a30243"


def test_do_auth_success_parse_masks_stok() -> None:
    session = parse_do_auth_success(
        Response(
            status_code=200,
            body=json.dumps(
                {
                    "method": "doAuth",
                    "stok": "secret-stok",
                    "errCode": 0,
                }
            ).encode("utf-8"),
        ),
        host="camera.local",
        port=20443,
        username="admin",
    )

    assert session.host == "camera.local"
    assert session.port == 20443
    assert session.stok == "secret-stok"
    assert session.stok_path() == "/stok=secret-stok"
    assert session.issued_at is not None
    assert "secret-stok" not in repr(session)
    assert "admin" not in repr(session)


def test_ipc_auth_service_runs_do_auth_flow() -> None:
    transport = FakeTransport(
        [
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": "doAuth",
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "abc123",
                            "algorithm": "SHA-256",
                            "uri": "doAuth",
                            "method": "POST",
                        },
                        "errCode": -10020,
                    }
                ).encode("utf-8"),
            ),
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": "doAuth",
                        "stok": "secret-stok",
                        "errCode": 0,
                    }
                ).encode("utf-8"),
            ),
        ]
    )
    service = IpcAuthService(
        IpcAuthConfig(host="camera.local", username="admin", password="password")
    )

    session = service.authenticate(transport)

    assert session.stok == "secret-stok"
    assert len(transport.requests) == 2
    assert json.loads(transport.requests[0].body or b"{}") == {
        "method": "doAuth",
        "params": None,
    }
    second_body = json.loads(transport.requests[1].body or b"{}")
    assert second_body["params"].keys() == {"nonce", "response"}
    assert "password" not in repr(service.config)


def test_do_auth_error_paths_are_sanitized() -> None:
    with pytest.raises(VigiResponseError, match="missing authenticate"):
        parse_do_auth_challenge(Response(status_code=200, body=b'{"errCode":-10020}'))

    with pytest.raises(AuthenticationError, match="Unsupported IPC doAuth algorithm"):
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": "MD5",
                            "uri": "doAuth",
                            "method": "POST",
                        },
                        "errCode": -10020,
                    }
                ).encode("utf-8"),
            )
        )

    with pytest.raises(VigiResponseError, match="missing nonce"):
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "algorithm": "SHA-256",
                            "uri": "doAuth",
                            "method": "POST",
                        },
                        "errCode": -10020,
                    }
                ).encode("utf-8"),
            )
        )

    with pytest.raises(AuthenticationError, match="IPC authentication failed"):
        parse_do_auth_success(
            Response(status_code=401, body=b'{"errCode":-10020}'),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(VigiResponseError, match="missing stok"):
        parse_do_auth_success(
            Response(status_code=200, body=b'{"method":"doAuth","errCode":0}'),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(AuthenticationError, match="IPC authentication failed"):
        parse_do_auth_success(
            Response(status_code=200, body=b'{"method":"doAuth","errCode":-10020}'),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(VigiResponseError, match="not valid JSON"):
        parse_do_auth_success(
            Response(status_code=200, body=b"not-json"),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(VigiApiError, match="HTTP 500"):
        parse_do_auth_challenge(Response(status_code=500, body=b"{}"))

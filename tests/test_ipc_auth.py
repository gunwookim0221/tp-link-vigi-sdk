import json

import pytest

from vigi.crypto import calculate_digest_response
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.ipc_auth import (
    IPC_AUTH_ALGORITHM,
    IPC_AUTH_HTTP_METHOD,
    IPC_AUTH_METHOD,
    IPC_ERR_AUTH_REQUIRED,
    IPC_ERR_SUCCESS,
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
    assert json.loads(request.body or b"{}") == {
        "method": IPC_AUTH_METHOD,
        "params": None,
    }


def test_ipc_auth_err_code_constants_match_documented_flow() -> None:
    assert IPC_ERR_SUCCESS == 0
    assert IPC_ERR_AUTH_REQUIRED == -10020


def test_do_auth_challenge_parse_allows_documented_err_code() -> None:
    challenge = parse_do_auth_challenge(
        Response(
            status_code=401,
            body=json.dumps(
                {
                    "method": IPC_AUTH_METHOD,
                    "authenticate": {
                        "realm": "TP-LINK IP-Camera",
                        "nonce": "abc123",
                        "algorithm": IPC_AUTH_ALGORITHM,
                        "uri": IPC_AUTH_METHOD,
                        "method": IPC_AUTH_HTTP_METHOD,
                    },
                    "errCode": IPC_ERR_AUTH_REQUIRED,
                }
            ).encode("utf-8"),
        )
    )

    assert challenge.realm == "TP-LINK IP-Camera"
    assert challenge.nonce == "abc123"
    assert challenge.algorithm == IPC_AUTH_ALGORITHM
    assert challenge.uri == IPC_AUTH_METHOD
    assert challenge.method == IPC_AUTH_HTTP_METHOD
    assert challenge.err_code == IPC_ERR_AUTH_REQUIRED
    assert "abc123" not in repr(challenge)


def test_do_auth_step2_request_uses_nonce_and_response_only() -> None:
    challenge = IpcAuthChallenge(
        realm="TP-LINK IP-Camera",
        nonce="abc123",
        algorithm=IPC_AUTH_ALGORITHM,
        uri=IPC_AUTH_METHOD,
        method=IPC_AUTH_HTTP_METHOD,
        err_code=IPC_ERR_AUTH_REQUIRED,
    )

    request = build_do_auth_response_request(
        username="admin",
        password="password",
        challenge=challenge,
    )
    body = json.loads(request.body or b"{}")

    assert request.method == "POST"
    assert request.path == "/"
    assert body["method"] == IPC_AUTH_METHOD
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
                    "method": IPC_AUTH_METHOD,
                    "stok": "secret-stok",
                    "errCode": IPC_ERR_SUCCESS,
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
                            "algorithm": IPC_AUTH_ALGORITHM,
                            "uri": IPC_AUTH_METHOD,
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            ),
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": IPC_AUTH_METHOD,
                        "stok": "secret-stok",
                        "errCode": IPC_ERR_SUCCESS,
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
        "method": IPC_AUTH_METHOD,
        "params": None,
    }
    second_body = json.loads(transport.requests[1].body or b"{}")
    assert second_body["params"].keys() == {"nonce", "response"}
    assert "password" not in repr(service.config)


def test_do_auth_error_paths_are_sanitized() -> None:
    with pytest.raises(VigiResponseError, match="missing authenticate"):
        parse_do_auth_challenge(
            Response(status_code=200, body=b'{"method":"doAuth","errCode":-10020}')
        )

    with pytest.raises(VigiResponseError, match="unexpected method"):
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": "notDoAuth",
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": IPC_AUTH_ALGORITHM,
                            "uri": IPC_AUTH_METHOD,
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            )
        )

    with pytest.raises(AuthenticationError, match="Unsupported IPC doAuth algorithm") as exc:
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": IPC_AUTH_METHOD,
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": "MD5",
                            "uri": IPC_AUTH_METHOD,
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            )
        )
    assert "secret-nonce" not in str(exc.value)

    with pytest.raises(VigiResponseError, match="unexpected uri"):
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": IPC_AUTH_METHOD,
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": IPC_AUTH_ALGORITHM,
                            "uri": "notDoAuth",
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            )
        )

    with pytest.raises(VigiResponseError, match="unexpected method"):
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": IPC_AUTH_METHOD,
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": IPC_AUTH_ALGORITHM,
                            "uri": IPC_AUTH_METHOD,
                            "method": "GET",
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            )
        )

    with pytest.raises(VigiResponseError, match="invalid errCode"):
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": IPC_AUTH_METHOD,
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": IPC_AUTH_ALGORITHM,
                            "uri": IPC_AUTH_METHOD,
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": "-10020",
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
                        "method": IPC_AUTH_METHOD,
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "algorithm": IPC_AUTH_ALGORITHM,
                            "uri": IPC_AUTH_METHOD,
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            )
        )

    with pytest.raises(VigiResponseError, match="not valid JSON"):
        parse_do_auth_challenge(Response(status_code=200, body=b""))

    with pytest.raises(AuthenticationError, match="IPC authentication failed"):
        parse_do_auth_success(
            Response(status_code=401, body=b'{"errCode":-10020,"stok":"secret-stok"}'),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(VigiResponseError, match="missing stok"):
        parse_do_auth_success(
            Response(status_code=200, body=b'{"method":"doAuth","errCode":0}'),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(VigiResponseError, match="unexpected method"):
        parse_do_auth_success(
            Response(
                status_code=200,
                body=b'{"method":"notDoAuth","errCode":0,"stok":"secret-stok"}',
            ),
            host="camera.local",
            port=20443,
        )

    with pytest.raises(VigiResponseError, match="invalid errCode"):
        parse_do_auth_success(
            Response(
                status_code=200,
                body=b'{"method":"doAuth","errCode":"0","stok":"secret-stok"}',
            ),
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


def test_do_auth_error_messages_do_not_expose_secrets() -> None:
    secrets = ("secret-password", "secret-nonce", "secret-response", "secret-stok")
    errors: list[BaseException] = []

    with pytest.raises(AuthenticationError) as auth_exc:
        parse_do_auth_challenge(
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "method": IPC_AUTH_METHOD,
                        "authenticate": {
                            "realm": "TP-LINK IP-Camera",
                            "nonce": "secret-nonce",
                            "algorithm": "MD5",
                            "uri": IPC_AUTH_METHOD,
                            "method": IPC_AUTH_HTTP_METHOD,
                        },
                        "errCode": IPC_ERR_AUTH_REQUIRED,
                    }
                ).encode("utf-8"),
            )
        )
    errors.append(auth_exc.value)

    with pytest.raises(AuthenticationError) as success_exc:
        parse_do_auth_success(
            Response(
                status_code=200,
                body=b'{"method":"doAuth","errCode":-10020,"stok":"secret-stok"}',
            ),
            host="camera.local",
            port=20443,
            username="admin",
        )
    errors.append(success_exc.value)

    config = IpcAuthConfig(
        host="camera.local",
        username="admin",
        password="secret-password",
    )
    challenge = IpcAuthChallenge(
        realm="TP-LINK IP-Camera",
        nonce="secret-nonce",
        algorithm=IPC_AUTH_ALGORITHM,
        uri=IPC_AUTH_METHOD,
        method=IPC_AUTH_HTTP_METHOD,
        err_code=IPC_ERR_AUTH_REQUIRED,
    )
    request = build_do_auth_response_request(
        username="admin",
        password="secret-password",
        challenge=challenge,
    )
    body = json.loads(request.body or b"{}")
    errors.extend(
        [
            Exception(repr(config)),
            Exception(repr(challenge)),
            Exception(repr(request)),
        ]
    )

    for error in errors:
        message = str(error)
        for secret in secrets:
            assert secret not in message
        assert body["params"]["response"] not in message

import json

import pytest

from vigi.auth import (
    build_digest_authorization,
    build_refresh_token_request,
    build_token_request,
    parse_digest_challenge,
    parse_token_response,
)
from vigi.crypto import calculate_digest_response
from vigi.exceptions import AuthenticationError, VigiResponseError
from vigi.transport import Response
from vigi.types import AuthMode


def test_digest_response_calculation() -> None:
    response = calculate_digest_response(
        username="admin",
        password="password",
        realm="TP-LINK NVR",
        nonce="abc123",
        method="GET",
        uri="/openapi/token",
    )

    assert response == (
        "a3f7e86332d25692c9ba1cd261d55d25"
        "938b5ea7ff78580d0a9110102ba8fcd5"
    )


def test_token_endpoint_request_creation() -> None:
    request = build_token_request()

    assert request.method == "GET"
    assert request.path == "/openapi/token"
    assert request.headers == {}


def test_refresh_token_request_creation() -> None:
    request = build_refresh_token_request("/openapi/token", "refresh/token")

    assert request.method == "GET"
    assert request.path == "/openapi/token?grant_type=refresh_token&refresh_token=refresh%2Ftoken"


def test_digest_challenge_and_authorization_header() -> None:
    challenge = parse_digest_challenge(
        Response(
            status_code=200,
            headers={
                "WWW-Authenticate": (
                    'Digest realm="TP-LINK NVR", nonce="abc123", '
                    'algorithm="SHA-256", url="/openapi/token"'
                )
            },
        )
    )

    authorization = build_digest_authorization(
        username="admin",
        password="password",
        method="GET",
        uri="/openapi/token",
        challenge=challenge,
    )

    assert authorization.startswith('Digest username="admin"')
    assert "password" not in authorization
    assert "response=" in authorization


def test_access_token_response_parsing() -> None:
    response = Response(
        status_code=200,
        body=json.dumps(
            {
                "token_type": "bearer",
                "expires_in": 1800,
                "access_token": "access%2Ftoken",
                "refresh_token": "refresh%2Ftoken",
            }
        ).encode("utf-8"),
    )

    result = parse_token_response(response)

    assert result.session_info.authenticated is True
    assert result.session_info.auth_mode is AuthMode.BEARER
    assert result.session_info.access_token == "access/token"
    assert result.session_info.refresh_token == "refresh/token"
    assert result.headers == {"Authorization": "Bearer access/token"}
    assert "access/token" not in repr(result)
    assert "refresh/token" not in repr(result.session_info)


def test_invalid_token_response_raises_response_error() -> None:
    with pytest.raises(VigiResponseError):
        parse_token_response(Response(status_code=200, body=b"not-json"))

    with pytest.raises(VigiResponseError):
        parse_token_response(
            Response(status_code=200, body=json.dumps({"token_type": "bearer"}).encode())
        )


def test_authentication_error_status_and_missing_challenge() -> None:
    with pytest.raises(AuthenticationError):
        parse_token_response(Response(status_code=401, body=b"{}"))

    with pytest.raises(AuthenticationError):
        parse_digest_challenge(Response(status_code=200, headers={}))

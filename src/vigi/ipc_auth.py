"""Internal IPC doAuth helpers for standalone camera verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Any

from vigi.crypto import calculate_digest_response
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.ipc_session import IpcSessionInfo
from vigi.transport import Request, Response, Transport


CONTENT_TYPE_JSON = {"Content-Type": "application/json"}
IPC_AUTH_METHOD = "doAuth"
IPC_AUTH_HTTP_METHOD = "POST"
IPC_AUTH_ALGORITHM = "SHA-256"
IPC_ERR_SUCCESS = 0
IPC_ERR_AUTH_REQUIRED = -10020


@dataclass(frozen=True, slots=True)
class IpcAuthConfig:
    """Connection credentials for internal IPC authentication."""

    host: str
    username: str
    password: str = field(repr=False)
    port: int = 20443
    verify_tls: bool = True


@dataclass(frozen=True, slots=True)
class IpcAuthChallenge:
    """Parsed IPC doAuth challenge."""

    realm: str
    nonce: str = field(repr=False)
    algorithm: str
    uri: str
    method: str
    err_code: int


class IpcAuthService:
    """Internal IPC doAuth strategy.

    This is separate from the NVR ``AuthService`` by design. It is not exported
    as part of the public SDK surface.
    """

    def __init__(self, config: IpcAuthConfig) -> None:
        self.config = config

    def authenticate(self, transport: Transport) -> IpcSessionInfo:
        """Authenticate using the documented IPC doAuth flow."""

        challenge_response = transport.send(build_do_auth_challenge_request())
        challenge = parse_do_auth_challenge(challenge_response)
        success_response = transport.send(
            build_do_auth_response_request(
                username=self.config.username,
                password=self.config.password,
                challenge=challenge,
            )
        )
        return parse_do_auth_success(
            success_response,
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
        )


def build_do_auth_challenge_request() -> Request:
    """Build IPC doAuth Step 1 challenge request."""

    return _json_request({"method": IPC_AUTH_METHOD, "params": None})


def build_do_auth_response_request(
    *, username: str, password: str, challenge: IpcAuthChallenge
) -> Request:
    """Build IPC doAuth Step 2 response request."""

    response = calculate_digest_response(
        username=username,
        password=password,
        realm=challenge.realm,
        nonce=challenge.nonce,
        method=challenge.method,
        uri=challenge.uri,
        algorithm=challenge.algorithm,
    )
    return _json_request(
        {
            "method": IPC_AUTH_METHOD,
            "params": {
                "nonce": challenge.nonce,
                "response": response,
            },
        }
    )


def parse_do_auth_challenge(response: Response) -> IpcAuthChallenge:
    """Parse IPC doAuth Step 1 challenge response."""

    if response.status_code not in {200, 401}:
        raise VigiApiError(f"IPC doAuth challenge returned HTTP {response.status_code}.")

    payload = _json_payload(response, "IPC doAuth challenge response is not valid JSON.")
    _require_payload_method(
        payload,
        expected=IPC_AUTH_METHOD,
        context="IPC doAuth challenge",
    )
    authenticate = payload.get("authenticate")
    if not isinstance(authenticate, dict):
        raise VigiResponseError("IPC doAuth challenge is missing authenticate.")

    fields = {
        "realm": authenticate.get("realm"),
        "nonce": authenticate.get("nonce"),
        "algorithm": authenticate.get("algorithm", "SHA-256"),
        "uri": authenticate.get("uri"),
        "method": authenticate.get("method"),
    }
    for name, value in fields.items():
        if not isinstance(value, str) or not value:
            raise VigiResponseError(f"IPC doAuth challenge is missing {name}.")

    algorithm = fields["algorithm"]
    if algorithm.upper() != IPC_AUTH_ALGORITHM:
        raise AuthenticationError("Unsupported IPC doAuth algorithm.")
    if fields["uri"] != IPC_AUTH_METHOD:
        raise VigiResponseError("IPC doAuth challenge has unexpected uri.")
    if fields["method"] != IPC_AUTH_HTTP_METHOD:
        raise VigiResponseError("IPC doAuth challenge has unexpected method.")

    err_code = payload.get("errCode")
    if not isinstance(err_code, int):
        raise VigiResponseError("IPC doAuth challenge has invalid errCode.")
    if err_code != IPC_ERR_AUTH_REQUIRED:
        raise AuthenticationError("IPC doAuth challenge did not request authentication.")

    return IpcAuthChallenge(
        realm=fields["realm"],
        nonce=fields["nonce"],
        algorithm=algorithm,
        uri=fields["uri"],
        method=fields["method"],
        err_code=err_code,
    )


def parse_do_auth_success(
    response: Response,
    *,
    host: str,
    port: int,
    username: str | None = None,
    issued_at: datetime | None = None,
) -> IpcSessionInfo:
    """Parse IPC doAuth Step 2 success response."""

    if response.status_code in {401, 403}:
        raise AuthenticationError("IPC authentication failed.")
    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"IPC doAuth returned HTTP {response.status_code}.")

    payload = _json_payload(response, "IPC doAuth response is not valid JSON.")
    _require_payload_method(
        payload,
        expected=IPC_AUTH_METHOD,
        context="IPC doAuth response",
    )
    err_code = payload.get("errCode")
    if not isinstance(err_code, int):
        raise VigiResponseError("IPC doAuth response has invalid errCode.")
    if err_code != IPC_ERR_SUCCESS:
        raise AuthenticationError("IPC authentication failed.")

    stok = payload.get("stok")
    if not isinstance(stok, str) or not stok:
        raise VigiResponseError("IPC doAuth response is missing stok.")

    return IpcSessionInfo(
        host=host,
        port=port,
        stok=stok,
        issued_at=issued_at or datetime.now(timezone.utc),
        username=username,
    )


def _json_request(payload: dict[str, Any]) -> Request:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return Request(method="POST", path="/", headers=CONTENT_TYPE_JSON, body=body)


def _json_payload(response: Response, error_message: str) -> dict[str, Any]:
    if not response.body:
        raise VigiResponseError(error_message)
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VigiResponseError(error_message) from exc
    if not isinstance(payload, dict):
        raise VigiResponseError(error_message)
    return payload


def _require_payload_method(
    payload: dict[str, Any], *, expected: str, context: str
) -> None:
    method = payload.get("method")
    if method != expected:
        raise VigiResponseError(f"{context} has unexpected method.")

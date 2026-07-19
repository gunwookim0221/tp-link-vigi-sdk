"""OpenAPI authentication support."""

from dataclasses import dataclass, field
import json
from urllib.parse import quote, unquote

from vigi.auth_provider import AuthProvider, AuthenticationContext, AuthenticationResult
from vigi.crypto import calculate_digest_response
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.session import SessionInfo
from vigi.transport import Request, Response, Transport
from vigi.types import AuthMode


@dataclass(frozen=True, slots=True)
class AuthConfig:
    """Connection credentials for future documented OpenAPI authentication."""

    host: str
    username: str
    password: str = field(repr=False)
    port: int = 20443
    verify_tls: bool = True


class AuthService(AuthProvider):
    """Documented Digest-to-Bearer authentication flow."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config

    def authenticate(
        self,
        context: AuthenticationContext | None = None,
        transport: Transport | None = None,
    ) -> AuthenticationResult:
        """Authenticate with the OpenAPI token endpoint."""

        if transport is None:
            raise AuthenticationError("A transport is required for authentication.")

        context = context or self._default_context()
        challenge_response = transport.send(build_token_request(context.token_path))
        challenge = parse_digest_challenge(challenge_response)
        authorization = build_digest_authorization(
            username=context.username,
            password=context.password,
            method="GET",
            uri=context.token_path,
            challenge=challenge,
        )
        token_response = transport.send(
            build_token_request(
                context.token_path,
                headers={"Authorization": authorization},
            )
        )
        return parse_token_response(token_response)

    def refresh(
        self,
        refresh_token: str,
        context: AuthenticationContext | None = None,
        transport: Transport | None = None,
    ) -> AuthenticationResult:
        """Refresh an access token using the documented refresh-token query."""

        if transport is None:
            raise AuthenticationError("A transport is required for token refresh.")

        context = context or self._default_context()
        request = build_refresh_token_request(context.token_path, refresh_token)
        return parse_token_response(transport.send(request))

    def _default_context(self) -> AuthenticationContext:
        return AuthenticationContext(
            base_url=f"https://{self.config.host}:{self.config.port}",
            username=self.config.username,
            password=self.config.password,
        )


def build_token_request(
    token_path: str = "/openapi/token", headers: dict[str, str] | None = None
) -> Request:
    """Build a token endpoint request."""

    return Request(method="GET", path=token_path, headers=headers or {})


def build_refresh_token_request(token_path: str, refresh_token: str) -> Request:
    """Build a documented refresh-token request."""

    return Request(
        method="GET",
        path=f"{token_path}?grant_type=refresh_token&refresh_token={quote(refresh_token, safe='')}",
    )


def parse_digest_challenge(response: Response) -> dict[str, str]:
    """Parse a WWW-Authenticate Digest challenge."""

    header = _get_header(response, "WWW-Authenticate")
    if not header:
        raise AuthenticationError("Missing WWW-Authenticate challenge.")
    if not header.lower().startswith("digest "):
        raise AuthenticationError("Unsupported authentication challenge.")

    result: dict[str, str] = {}
    for part in header[len("Digest ") :].split(","):
        key, separator, value = part.strip().partition("=")
        if not separator:
            continue
        result[key.strip().lower()] = value.strip().strip('"')

    for required_key in ("realm", "nonce"):
        if required_key not in result:
            raise AuthenticationError(f"Missing Digest challenge field: {required_key}")
    result.setdefault("algorithm", "SHA-256")
    return result


def build_digest_authorization(
    *,
    username: str,
    password: str,
    method: str,
    uri: str,
    challenge: dict[str, str],
) -> str:
    """Build the documented Digest Authorization header."""

    realm = challenge["realm"]
    nonce = challenge["nonce"]
    algorithm = challenge.get("algorithm", "SHA-256")
    response = calculate_digest_response(
        username=username,
        password=password,
        realm=realm,
        nonce=nonce,
        method=method,
        uri=uri,
        algorithm=algorithm,
    )
    return (
        'Digest username="{username}", nonce="{nonce}", realm="{realm}", response="{response}"'
    ).format(username=username, nonce=nonce, realm=realm, response=response)


def parse_token_response(response: Response) -> AuthenticationResult:
    """Parse a token endpoint response into session state."""

    if response.status_code in {401, 403}:
        raise AuthenticationError("Authentication failed.")
    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"Token endpoint returned HTTP {response.status_code}.")

    try:
        payload = json.loads((response.body or b"{}").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VigiResponseError("Token response is not valid JSON.") from exc

    token_type = payload.get("token_type")
    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    expires_in = payload.get("expires_in")

    if token_type != "bearer" or not isinstance(access_token, str):
        raise VigiResponseError("Token response is missing bearer access_token.")
    if not isinstance(expires_in, int):
        raise VigiResponseError("Token response is missing numeric expires_in.")
    if refresh_token is not None and not isinstance(refresh_token, str):
        raise VigiResponseError("Token response refresh_token must be a string.")

    decoded_access_token = unquote(access_token)
    decoded_refresh_token = unquote(refresh_token) if refresh_token else None
    session_info = SessionInfo(
        authenticated=True,
        auth_mode=AuthMode.BEARER,
        token_type=token_type,
        expires_in=expires_in,
        access_token=decoded_access_token,
        refresh_token=decoded_refresh_token,
    )
    return AuthenticationResult(
        session_info=session_info,
        headers=session_info.bearer_headers(),
    )


def _get_header(response: Response, name: str) -> str | None:
    for key, value in response.headers.items():
        if key.lower() == name.lower():
            return value
    return None

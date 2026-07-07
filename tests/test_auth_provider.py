import json

from vigi import AuthConfig, AuthService, AuthMode, VigiClient
from vigi.auth_provider import AuthenticationContext, AuthenticationResult, AuthProvider
from vigi.session import SessionInfo
from vigi.transport import Request, Response, Transport, TransportConfig


class FakeTransport(Transport):
    def __init__(self, responses: list[Response]) -> None:
        super().__init__(TransportConfig(base_url="https://nvr.local:20443"))
        self.responses = responses
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return self.responses.pop(0)


class FakeAuthProvider(AuthProvider):
    def __init__(self) -> None:
        self.calls: list[AuthenticationContext] = []

    def authenticate(
        self, context: AuthenticationContext, transport: Transport
    ) -> AuthenticationResult:
        self.calls.append(context)
        return AuthenticationResult(
            session_info=SessionInfo(
                authenticated=True,
                auth_mode=AuthMode.BEARER,
                access_token="token",
            ),
            headers={"Authorization": "Bearer token"},
        )


def test_auth_service_stores_bearer_session_state() -> None:
    transport = FakeTransport(
        [
            Response(
                status_code=200,
                headers={
                    "WWW-Authenticate": (
                        'Digest realm="TP-LINK NVR", nonce="abc123", '
                        'algorithm="SHA-256", url="/openapi/token"'
                    )
                },
            ),
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "access_token": "access%2Ftoken",
                        "refresh_token": "refresh%2Ftoken",
                    }
                ).encode("utf-8"),
            ),
        ]
    )
    auth = AuthService(AuthConfig(host="nvr.local", username="admin", password="secret"))

    result = auth.authenticate(transport=transport)

    assert result.session_info.authenticated is True
    assert result.headers == {"Authorization": "Bearer access/token"}
    assert len(transport.requests) == 2
    assert transport.requests[0].headers == {}
    assert transport.requests[1].headers["Authorization"].startswith("Digest ")
    assert "secret" not in repr(auth.config)
    assert "access/token" not in repr(result)


def test_client_login_calls_auth_provider() -> None:
    provider = FakeAuthProvider()
    transport = FakeTransport([])
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="secret"),
        transport=transport,
        auth_provider=provider,
    )

    client.login()

    assert len(provider.calls) == 1
    assert client.session.info.authenticated is True
    assert client.session.info.access_token == "token"

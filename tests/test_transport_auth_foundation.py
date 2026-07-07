import pytest

from vigi import (
    AuthConfig,
    AuthProvider,
    AuthenticationContext,
    Request,
    Response,
    Session,
    SessionInfo,
    Timeout,
    Transport,
    TransportConfig,
    VigiClient,
)


def test_transport_boundary_can_be_created() -> None:
    config = TransportConfig(
        base_url="https://nvr.local:20443",
        timeout=Timeout(connect=1.0, read=2.0),
        verify_ssl=True,
    )
    transport = Transport(config)
    request = Request(method="GET", path="/openapi/token")
    response = Response(status_code=200, body=b"{}")

    assert transport.config == config
    assert request.method == "GET"
    assert response.status_code == 200


def test_transport_send_is_not_implemented() -> None:
    transport = Transport(TransportConfig(base_url="https://nvr.local:20443"))

    with pytest.raises(NotImplementedError):
        transport.send(Request(method="GET", path="/openapi/token"))


def test_session_boundary_can_be_created() -> None:
    transport = Transport(TransportConfig(base_url="https://nvr.local:20443"))
    session = Session(transport=transport, info=SessionInfo())

    assert session.transport is transport
    assert session.info.authenticated is False


def test_auth_provider_stub_is_not_implemented() -> None:
    provider = AuthProvider()
    context = AuthenticationContext(
        base_url="https://nvr.local:20443",
        username="admin",
        password="secret",
    )

    with pytest.raises(NotImplementedError):
        provider.authenticate(context, Transport(TransportConfig(base_url=context.base_url)))


def test_client_wires_transport_and_auth_provider() -> None:
    client = VigiClient(AuthConfig(host="nvr.local", username="admin", password="secret"))

    assert isinstance(client.transport, Transport)
    assert isinstance(client.auth_provider, AuthProvider)
    assert isinstance(client.session, Session)

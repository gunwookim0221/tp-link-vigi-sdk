import pytest

from vigi import AuthConfig, AuthMode, SnapshotImage, VigiClient
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError, ValidationError
from vigi.session import Session, SessionInfo
from vigi.snapshots import (
    SNAPSHOT_PATH,
    build_snapshot_request,
    parse_snapshot_response,
)
from vigi.transport import Request, Response, Transport, TransportConfig


JPEG = b"\xff\xd8\xff\xe0vigi-test\xff\xd9"


class FakeTransport(Transport):
    def __init__(self, responses: list[Response]) -> None:
        super().__init__(TransportConfig(base_url="https://nvr.local:20443"))
        self.responses = responses
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return self.responses.pop(0)


def _bearer_session(transport: Transport) -> Session:
    return Session(
        transport=transport,
        info=SessionInfo(
            authenticated=True,
            auth_mode=AuthMode.BEARER,
            access_token="secret-token",
        ),
    )


def test_snapshot_request_creation() -> None:
    request = build_snapshot_request(
        {"Authorization": "Bearer secret-token"},
        channel_id=3,
    )

    assert request == Request(
        method="GET",
        path=f"{SNAPSHOT_PATH}?channel=3",
        headers={"Authorization": "Bearer secret-token"},
    )
    assert "secret-token" not in repr(request)


def test_parse_snapshot_response_accepts_documented_jpeg() -> None:
    parsed = parse_snapshot_response(
        Response(status_code=200, headers={"Content-Type": "image/jpeg"}, body=JPEG)
    )

    assert parsed == SnapshotImage(data=JPEG)


@pytest.mark.parametrize(
    "response",
    [
        Response(status_code=500, body=b"server error"),
        Response(status_code=200, headers={"Content-Type": "application/json"}, body=JPEG),
        Response(status_code=200, headers={"Content-Type": "image/jpeg"}, body=b"not-jpeg"),
        Response(status_code=200, body=b""),
    ],
)
def test_parse_snapshot_response_rejects_errors_and_non_images(response: Response) -> None:
    with pytest.raises((VigiApiError, VigiResponseError)):
        parse_snapshot_response(response)


@pytest.mark.parametrize("channel_id", [0, -1, "1", True])
def test_snapshot_request_rejects_invalid_channel(channel_id: object) -> None:
    with pytest.raises(ValidationError, match="channel_id"):
        build_snapshot_request({}, channel_id=channel_id)  # type: ignore[arg-type]


def test_snapshot_service_requires_bearer_before_network_call() -> None:
    transport = FakeTransport([])
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )

    with pytest.raises(AuthenticationError):
        client.snapshots.get_snapshot(1)

    assert transport.requests == []


def test_snapshot_service_uses_bearer_and_returns_jpeg_bytes() -> None:
    transport = FakeTransport(
        [Response(status_code=200, headers={"Content-Type": "image/jpeg"}, body=JPEG)]
    )
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )
    client.session.info = _bearer_session(transport).info

    result = client.snapshots.get_snapshot(1)

    assert result.data == JPEG
    assert transport.requests[0].method == "GET"
    assert transport.requests[0].path == f"{SNAPSHOT_PATH}?channel=1"
    assert transport.requests[0].headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(result)

import json

import pytest

from vigi import AuthConfig, AuthMode, VigiClient
from vigi.devices import (
    ADDED_DEVICES_PATH,
    build_added_devices_request,
    parse_added_devices_response,
)
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.models import AddedDevice, AddedDevicesResponse
from vigi.session import Session, SessionInfo
from vigi.transport import Request, Response, Transport, TransportConfig
from vigi.types import ChannelStatus


class FakeTransport(Transport):
    def __init__(self, responses: list[Response]) -> None:
        super().__init__(TransportConfig(base_url="https://nvr.local:20443"))
        self.responses = responses
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return self.responses.pop(0)


def _bearer_session(transport: Transport, token: str = "secret-token") -> Session:
    return Session(
        transport=transport,
        info=SessionInfo(
            authenticated=True,
            auth_mode=AuthMode.BEARER,
            token_type="bearer",
            access_token=token,
        ),
    )


def test_added_devices_request_creation() -> None:
    request = build_added_devices_request({"Authorization": "Bearer secret-token"})

    assert request.method == "GET"
    assert request.path == ADDED_DEVICES_PATH
    assert request.headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(request)


def test_parse_added_devices_success_response() -> None:
    response = Response(
        status_code=200,
        body=json.dumps(
            {
                "devices": [
                    {
                        "id": 1,
                        "name": "Camera 1",
                        "alias": "VIGI Camera",
                        "online": "1",
                        "ip": "192.168.0.10",
                        "mac": "AA-BB-CC-DD-EE-FF",
                    },
                    {
                        "id": 2,
                        "name": "Camera 2",
                        "alias": "VIGI Camera 2",
                        "online": "0",
                        "ip": "192.168.0.11",
                        "mac": "AA-BB-CC-DD-EE-00",
                    },
                ],
                "error_code": 0,
            }
        ).encode("utf-8"),
    )

    parsed = parse_added_devices_response(response)

    assert parsed == AddedDevicesResponse(
        devices=(
            AddedDevice(
                channel_id=1,
                name="Camera 1",
                alias="VIGI Camera",
                online=ChannelStatus.ONLINE,
                ip_address="192.168.0.10",
                mac_address="AA-BB-CC-DD-EE-FF",
            ),
            AddedDevice(
                channel_id=2,
                name="Camera 2",
                alias="VIGI Camera 2",
                online=ChannelStatus.OFFLINE,
                ip_address="192.168.0.11",
                mac_address="AA-BB-CC-DD-EE-00",
            ),
        ),
        error_code=0,
    )


def test_parse_added_devices_empty_response() -> None:
    response = Response(
        status_code=200,
        body=json.dumps({"devices": [], "error_code": 0}).encode("utf-8"),
    )

    parsed = parse_added_devices_response(response)

    assert parsed.devices == ()
    assert parsed.error_code == 0


@pytest.mark.parametrize(
    "body",
    [
        b"not-json",
        json.dumps([]).encode("utf-8"),
        json.dumps({"error_code": 0}).encode("utf-8"),
        json.dumps({"devices": {}, "error_code": 0}).encode("utf-8"),
        json.dumps(
            {
                "devices": [
                    {
                        "id": 1,
                        "name": "Camera",
                        "alias": "Alias",
                        "online": "1",
                        "ip": "192.168.0.10",
                    }
                ],
                "error_code": 0,
            }
        ).encode("utf-8"),
        json.dumps(
            {
                "devices": [
                    {
                        "id": 1,
                        "name": "Camera",
                        "alias": "Alias",
                        "online": "2",
                        "ip": "192.168.0.10",
                        "mac": "AA-BB-CC-DD-EE-FF",
                    }
                ],
                "error_code": 0,
            }
        ).encode("utf-8"),
    ],
)
def test_parse_added_devices_malformed_response(body: bytes) -> None:
    with pytest.raises(VigiResponseError):
        parse_added_devices_response(Response(status_code=200, body=body))


def test_parse_added_devices_api_errors() -> None:
    with pytest.raises(VigiApiError):
        parse_added_devices_response(Response(status_code=500, body=b"{}"))

    with pytest.raises(VigiApiError):
        parse_added_devices_response(
            Response(
                status_code=200,
                body=json.dumps({"devices": [], "error_code": 1001}).encode("utf-8"),
            )
        )


def test_list_added_devices_requires_authentication_before_network_call() -> None:
    transport = FakeTransport([])
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )

    with pytest.raises(AuthenticationError):
        client.devices.list_added_devices()

    assert transport.requests == []


def test_list_added_devices_uses_bearer_session_and_parser() -> None:
    transport = FakeTransport(
        [
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "devices": [
                            {
                                "id": 1,
                                "name": "Camera 1",
                                "alias": "VIGI Camera",
                                "online": "1",
                                "ip": "192.168.0.10",
                                "mac": "AA-BB-CC-DD-EE-FF",
                            }
                        ],
                        "error_code": 0,
                    }
                ).encode("utf-8"),
            )
        ]
    )
    session = _bearer_session(transport)
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )
    client.session.info = session.info

    result = client.devices.list_added_devices()

    assert result.devices[0].channel_id == 1
    assert result.devices[0].online is ChannelStatus.ONLINE
    assert transport.requests[0].method == "GET"
    assert transport.requests[0].path == "/openapi/added_devices"
    assert transport.requests[0].headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(result)

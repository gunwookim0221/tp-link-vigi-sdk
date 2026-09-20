import json

import pytest

from vigi import AuthConfig, AuthMode, ConnectionProtocol, VigiClient
from vigi.devices import (
    ADD_DEVICE_PATH,
    ADD_DEVICE_RTSP_PATH,
    ADDED_DEVICES_PATH,
    DEVICE_SCAN_PATH,
    REMOVE_DEVICE_PATH,
    build_add_device_request,
    build_add_device_rtsp_request,
    build_added_devices_request,
    build_device_scan_request,
    build_remove_device_request,
    parse_device_scan_response,
    parse_added_devices_response,
)
from vigi.exceptions import AuthenticationError, ValidationError, VigiApiError, VigiResponseError
from vigi.models import (
    AddedDevice,
    AddedDevicesResponse,
    DeviceScanResponse,
    ErrorCodeResponse,
    ScannedDevice,
)
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


def test_device_scan_request_creation() -> None:
    request = build_device_scan_request({"Authorization": "Bearer secret-token"})

    assert request.method == "GET"
    assert request.path == DEVICE_SCAN_PATH
    assert request.headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(request)


def test_parse_device_scan_success_preserves_protocol_values_and_empty_results() -> None:
    parsed = parse_device_scan_response(
        Response(
            status_code=200,
            body=json.dumps(
                {
                    "devices": [
                        {
                            "ip": "192.168.0.10",
                            "name": "Camera%20One",
                            "connect_prot": "TP-LINK",
                            "port": "443",
                            "mac": "AA-BB-CC-DD-EE-FF",
                            "model": "VIGI%20C450",
                        },
                        {
                            "ip": "192.168.0.11",
                            "name": "RTSP Camera",
                            "connect_prot": "FUTURE",
                            "port": "554",
                            "mac": "AA-BB-CC-DD-EE-00",
                            "model": "External",
                        },
                    ],
                    "error_code": 0,
                }
            ).encode("utf-8"),
        )
    )

    assert parsed == DeviceScanResponse(
        devices=(
            ScannedDevice(
                ip_address="192.168.0.10",
                name="Camera%20One",
                connect_protocol="TP-LINK",
                port="443",
                mac_address="AA-BB-CC-DD-EE-FF",
                model="VIGI%20C450",
            ),
            ScannedDevice(
                ip_address="192.168.0.11",
                name="RTSP Camera",
                connect_protocol="FUTURE",
                port="554",
                mac_address="AA-BB-CC-DD-EE-00",
                model="External",
            ),
        ),
        error_code=0,
    )
    assert (
        parse_device_scan_response(
            Response(status_code=200, body=b'{"devices": [], "error_code": 0}')
        ).devices
        == ()
    )


@pytest.mark.parametrize(
    "body",
    [
        b"not-json",
        b"[]",
        b'{"devices": {}, "error_code": 0}',
        b'{"devices": [{"ip": "192.168.0.10"}], "error_code": 0}',
        b'{"devices": [], "error_code": 1001}',
    ],
)
def test_parse_device_scan_errors(body: bytes) -> None:
    with pytest.raises((VigiApiError, VigiResponseError)):
        parse_device_scan_response(Response(status_code=200, body=body))


def test_device_management_request_builders_use_exact_payloads_and_redact_secrets() -> None:
    headers = {"Authorization": "Bearer secret-token"}
    add_request = build_add_device_request(
        headers,
        username="admin",
        password="device-password",
        connect_protocol=ConnectionProtocol.TP_LINK,
        ip_address="192.168.0.10",
        port="443",
    )
    remove_request = build_remove_device_request(headers, channel_id=2)
    rtsp_request = build_add_device_rtsp_request(
        headers,
        username="admin",
        password="rtsp-password",
        rtsp_url_main="rtsp://192.168.0.10:554/stream1",
    )

    assert add_request.method == "POST"
    assert add_request.path == ADD_DEVICE_PATH
    assert json.loads(add_request.body or b"") == {
        "username": "admin",
        "password": "device-password",
        "connect_prot": "TP-LINK",
        "ip": "192.168.0.10",
        "port": "443",
    }
    assert remove_request.method == "POST"
    assert remove_request.path == REMOVE_DEVICE_PATH
    assert json.loads(remove_request.body or b"") == {"channel": 2}
    assert rtsp_request.method == "POST"
    assert rtsp_request.path == ADD_DEVICE_RTSP_PATH
    assert json.loads(rtsp_request.body or b"") == {
        "username": "admin",
        "password": "rtsp-password",
        "rtsp_url_main": "rtsp://192.168.0.10:554/stream1",
    }
    assert add_request.headers == {
        "Authorization": "Bearer secret-token",
        "Content-Type": "application/json",
    }
    assert "device-password" not in repr(add_request)
    assert "rtsp-password" not in repr(rtsp_request)


@pytest.mark.parametrize(
    ("builder", "kwargs"),
    [
        (
            build_add_device_request,
            {
                "username": "",
                "password": "password",
                "connect_protocol": ConnectionProtocol.TP_LINK,
                "ip_address": "192.168.0.10",
                "port": "443",
            },
        ),
        (
            build_add_device_request,
            {
                "username": "admin",
                "password": "password",
                "connect_protocol": ConnectionProtocol.RTSP,
                "ip_address": "192.168.0.10",
                "port": "443",
            },
        ),
        (
            build_remove_device_request,
            {"channel_id": 0},
        ),
        (
            build_add_device_rtsp_request,
            {"username": "admin", "password": "password", "rtsp_url_main": ""},
        ),
    ],
)
def test_device_management_request_validation(builder, kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        builder({"Authorization": "Bearer token"}, **kwargs)


def test_device_management_services_use_bearer_and_do_not_retry() -> None:
    transport = FakeTransport(
        [
            Response(status_code=200, body=b'{"devices": [], "error_code": 0}'),
            Response(status_code=200, body=b'{"error_code": 0}'),
            Response(status_code=200, body=b'{"error_code": 0}'),
            Response(status_code=200, body=b'{"error_code": 1001}'),
        ]
    )
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )
    client.session.info = _bearer_session(transport).info

    assert client.devices.scan_devices().devices == ()
    assert client.devices.add_device(
        "admin",
        "device-password",
        ConnectionProtocol.ONVIF,
        "192.168.0.10",
        "443",
    ) == ErrorCodeResponse(error_code=0)
    assert client.devices.remove_device(2) == ErrorCodeResponse(error_code=0)
    with pytest.raises(VigiApiError):
        client.devices.add_rtsp_device(
            "admin",
            "rtsp-password",
            "rtsp://192.168.0.10:554/stream1",
        )

    assert len(transport.requests) == 4
    assert [request.method for request in transport.requests] == ["GET", "POST", "POST", "POST"]
    assert all(
        request.headers["Authorization"] == "Bearer secret-token" for request in transport.requests
    )
    assert "device-password" not in repr(transport.requests[1])
    assert "rtsp-password" not in repr(transport.requests[3])


def test_device_management_services_require_bearer_before_network_call() -> None:
    transport = FakeTransport([])
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )

    with pytest.raises(AuthenticationError):
        client.devices.scan_devices()
    with pytest.raises(AuthenticationError):
        client.devices.add_device(
            "admin",
            "password",
            ConnectionProtocol.TP_LINK,
            "192.168.0.10",
            "443",
        )
    with pytest.raises(AuthenticationError):
        client.devices.remove_device(1)
    with pytest.raises(AuthenticationError):
        client.devices.add_rtsp_device("admin", "password", "rtsp://nvr.local/stream1")
    assert transport.requests == []

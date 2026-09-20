"""NVR device inventory support."""

import json
from typing import Mapping

from vigi.exceptions import AuthenticationError, ValidationError, VigiApiError, VigiResponseError
from vigi.models import (
    AddedDevice,
    AddedDevicesResponse,
    DeviceScanResponse,
    ErrorCodeResponse,
    ScannedDevice,
)
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AuthMode, ChannelStatus, ConnectionProtocol


ADDED_DEVICES_PATH = "/openapi/added_devices"
DEVICE_SCAN_PATH = "/openapi/device_scan"
ADD_DEVICE_PATH = "/openapi/add_device"
REMOVE_DEVICE_PATH = "/openapi/remove_device"
ADD_DEVICE_RTSP_PATH = "/openapi/add_device_rtsp"


class DeviceService:
    """Documented NVR device inventory and management APIs."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def list_added_devices(self) -> AddedDevicesResponse:
        """List NVR-managed devices through the documented OpenAPI endpoint."""

        headers = self._bearer_headers()
        session = self._session()
        request = build_added_devices_request(headers)
        return parse_added_devices_response(session.transport.send(request))

    def scan_devices(self) -> DeviceScanResponse:
        """Scan the network for devices without adding any result."""

        session = self._session()
        request = build_device_scan_request(self._bearer_headers())
        return parse_device_scan_response(session.transport.send(request))

    def add_device(
        self,
        username: str,
        password: str,
        connect_protocol: ConnectionProtocol,
        ip_address: str,
        port: str,
    ) -> ErrorCodeResponse:
        """Add one NVR-managed device using the documented control protocol."""

        session = self._session()
        request = build_add_device_request(
            self._bearer_headers(),
            username=username,
            password=password,
            connect_protocol=connect_protocol,
            ip_address=ip_address,
            port=port,
        )
        return parse_error_code_response(
            session.transport.send(request),
            label="Add device",
        )

    def remove_device(self, channel_id: int) -> ErrorCodeResponse:
        """Remove the NVR-managed device at the documented channel."""

        session = self._session()
        request = build_remove_device_request(self._bearer_headers(), channel_id=channel_id)
        return parse_error_code_response(
            session.transport.send(request),
            label="Remove device",
        )

    def add_rtsp_device(
        self,
        username: str,
        password: str,
        rtsp_url_main: str,
    ) -> ErrorCodeResponse:
        """Add one device through the documented RTSP registration endpoint."""

        session = self._session()
        request = build_add_device_rtsp_request(
            self._bearer_headers(),
            username=username,
            password=password,
            rtsp_url_main=rtsp_url_main,
        )
        return parse_error_code_response(
            session.transport.send(request),
            label="Add RTSP device",
        )

    def _session(self) -> Session:
        if self.session is None:
            raise AuthenticationError("An authenticated session is required.")
        return self.session

    def _bearer_headers(self) -> Mapping[str, str]:
        session = self._session()
        if not session.info.authenticated:
            raise AuthenticationError("An authenticated session is required.")
        if session.info.auth_mode is not AuthMode.BEARER:
            raise AuthenticationError("Bearer authentication is required.")

        headers = session.info.bearer_headers()
        if "Authorization" not in headers:
            raise AuthenticationError("Bearer authentication is required.")
        return headers


def build_added_devices_request(headers: Mapping[str, str]) -> Request:
    """Build the documented added-devices inventory request."""

    return Request(method="GET", path=ADDED_DEVICES_PATH, headers=headers)


def build_device_scan_request(headers: Mapping[str, str]) -> Request:
    """Build the documented read-only device-scan request."""

    return Request(method="GET", path=DEVICE_SCAN_PATH, headers=headers)


def build_add_device_request(
    headers: Mapping[str, str],
    *,
    username: str,
    password: str,
    connect_protocol: ConnectionProtocol,
    ip_address: str,
    port: str,
) -> Request:
    """Build the documented standard device-add request."""

    _require_non_empty_string(username, "username")
    _require_non_empty_string(password, "password")
    if (
        type(connect_protocol) is not ConnectionProtocol
        or connect_protocol is ConnectionProtocol.RTSP
    ):
        raise ValidationError("connect_protocol must be ConnectionProtocol.TP_LINK or ONVIF.")
    _require_non_empty_string(ip_address, "ip_address")
    _require_non_empty_string(port, "port")
    payload = {
        "username": username,
        "password": password,
        "connect_prot": connect_protocol.value,
        "ip": ip_address,
        "port": port,
    }
    return _build_json_request(headers, ADD_DEVICE_PATH, payload)


def build_remove_device_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    """Build the documented device-remove request."""

    _require_positive_int(channel_id, "channel_id")
    return _build_json_request(headers, REMOVE_DEVICE_PATH, {"channel": channel_id})


def build_add_device_rtsp_request(
    headers: Mapping[str, str],
    *,
    username: str,
    password: str,
    rtsp_url_main: str,
) -> Request:
    """Build the documented RTSP-device registration request."""

    _require_non_empty_string(username, "username")
    _require_non_empty_string(password, "password")
    _require_non_empty_string(rtsp_url_main, "rtsp_url_main")
    payload = {
        "username": username,
        "password": password,
        "rtsp_url_main": rtsp_url_main,
    }
    return _build_json_request(headers, ADD_DEVICE_RTSP_PATH, payload)


def parse_added_devices_response(response: Response) -> AddedDevicesResponse:
    """Parse a documented added-devices response."""

    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"Added devices endpoint returned HTTP {response.status_code}.")

    try:
        payload = json.loads((response.body or b"{}").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VigiResponseError("Added devices response is not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise VigiResponseError("Added devices response must be a JSON object.")

    error_code = payload.get("error_code")
    if not isinstance(error_code, int):
        raise VigiResponseError("Added devices response is missing numeric error_code.")
    if error_code != 0:
        raise VigiApiError(f"Added devices endpoint returned error_code {error_code}.")

    devices_payload = payload.get("devices")
    if not isinstance(devices_payload, list):
        raise VigiResponseError("Added devices response devices must be a list.")

    devices = tuple(_parse_added_device(device) for device in devices_payload)
    return AddedDevicesResponse(devices=devices, error_code=error_code)


def parse_device_scan_response(response: Response) -> DeviceScanResponse:
    """Parse the documented device-scan response without normalizing values."""

    payload, error_code = _parse_json_error_response(response, "Device scan")
    devices_payload = payload.get("devices")
    if not isinstance(devices_payload, list):
        raise VigiResponseError("Device scan response devices must be a list.")

    devices: list[ScannedDevice] = []
    for device_payload in devices_payload:
        if not isinstance(device_payload, dict):
            raise VigiResponseError("Scanned device entry must be a JSON object.")
        devices.append(
            ScannedDevice(
                ip_address=_required_string(device_payload, "ip", "Scanned device"),
                name=_required_string(device_payload, "name", "Scanned device"),
                connect_protocol=_required_string(
                    device_payload,
                    "connect_prot",
                    "Scanned device",
                ),
                port=_required_string(device_payload, "port", "Scanned device"),
                mac_address=_required_string(device_payload, "mac", "Scanned device"),
                model=_required_string(device_payload, "model", "Scanned device"),
            )
        )
    return DeviceScanResponse(devices=tuple(devices), error_code=error_code)


def parse_error_code_response(response: Response, *, label: str) -> ErrorCodeResponse:
    """Parse a documented mutation response containing only ``error_code``."""

    _, error_code = _parse_json_error_response(response, label)
    return ErrorCodeResponse(error_code=error_code)


def _parse_json_error_response(response: Response, label: str) -> tuple[dict[str, object], int]:
    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"{label} endpoint returned HTTP {response.status_code}.")

    try:
        payload = json.loads((response.body or b"{}").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VigiResponseError(f"{label} response is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise VigiResponseError(f"{label} response must be a JSON object.")

    error_code = payload.get("error_code")
    if not isinstance(error_code, int) or isinstance(error_code, bool):
        raise VigiResponseError(f"{label} response is missing numeric error_code.")
    if error_code != 0:
        raise VigiApiError(f"{label} endpoint returned error_code {error_code}.")
    return payload, error_code


def _parse_added_device(payload: object) -> AddedDevice:
    if not isinstance(payload, dict):
        raise VigiResponseError("Added device entry must be a JSON object.")

    channel_id = _required_int(payload, "id")
    name = _required_str(payload, "name")
    alias = _required_str(payload, "alias")
    online_value = _required_str(payload, "online")
    ip_address = _required_str(payload, "ip")
    mac_address = _required_str(payload, "mac")

    try:
        online = ChannelStatus(online_value)
    except ValueError as exc:
        raise VigiResponseError("Added device online value must be '0' or '1'.") from exc
    if online is ChannelStatus.UNKNOWN:
        raise VigiResponseError("Added device online value must be '0' or '1'.")

    return AddedDevice(
        channel_id=channel_id,
        name=name,
        alias=alias,
        online=online,
        ip_address=ip_address,
        mac_address=mac_address,
    )


def _required_int(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise VigiResponseError(f"Added device field {key} must be an integer.")
    return value


def _required_str(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise VigiResponseError(f"Added device field {key} must be a string.")
    return value


def _required_string(payload: dict[str, object], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise VigiResponseError(f"{label} field {key} must be a non-empty string.")
    return value


def _require_non_empty_string(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field_name} must be a non-empty string.")


def _require_positive_int(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer.")


def _build_json_request(
    headers: Mapping[str, str], path: str, payload: Mapping[str, object]
) -> Request:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    return Request(
        method="POST",
        path=path,
        headers=request_headers,
        body=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
    )

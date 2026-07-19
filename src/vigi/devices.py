"""NVR device inventory support."""

import json
from typing import Mapping

from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.models import AddedDevice, AddedDevicesResponse
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AuthMode, ChannelStatus


ADDED_DEVICES_PATH = "/openapi/added_devices"


class DeviceService:
    """Documented NVR device/channel inventory APIs."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def list_added_devices(self) -> AddedDevicesResponse:
        """List NVR-managed devices through the documented OpenAPI endpoint."""

        if self.session is None:
            raise AuthenticationError("An authenticated session is required.")
        if not self.session.info.authenticated:
            raise AuthenticationError("An authenticated session is required.")
        if self.session.info.auth_mode is not AuthMode.BEARER:
            raise AuthenticationError("Bearer authentication is required.")

        headers = self.session.info.bearer_headers()
        if "Authorization" not in headers:
            raise AuthenticationError("Bearer authentication is required.")

        request = build_added_devices_request(headers)
        return parse_added_devices_response(self.session.transport.send(request))


def build_added_devices_request(headers: Mapping[str, str]) -> Request:
    """Build the documented added-devices inventory request."""

    return Request(method="GET", path=ADDED_DEVICES_PATH, headers=headers)


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

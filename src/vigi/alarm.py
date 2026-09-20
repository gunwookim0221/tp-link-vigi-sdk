"""VIGI NVR alarm-output capability and control support."""

import json
from typing import Mapping, cast
from urllib.parse import urlencode

from vigi.exceptions import AuthenticationError, ValidationError, VigiApiError, VigiResponseError
from vigi.models import (
    AlarmManualResponse,
    BatchIpcAlarmOutput,
    BatchIpcAlarmOutputResponse,
    ErrorCodeResponse,
    IpcAlarmOutput,
    IpcAlarmOutputResponse,
    NvrAlarmOutput,
    NvrAlarmOutputResponse,
)
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AlarmAction, AlarmDelayTime, AlarmEnabled, AlarmType, AuthMode


NVR_ALARM_PATH = "/openapi/alarm_output/nvr_alarm"
IPC_ALARM_PATH = "/openapi/alarm_output/ipc_alarm"
NVR_MANUAL_ALARM_PATH = "/openapi/alarm_output/nvr_manual_alarm"
IPC_MANUAL_ALARM_PATH = "/openapi/alarm_output/ipc_manual_alarm"
BATCH_IPC_ALARM_PATH = "/openapi/alarm_output/batch_get_ipc_alarm"


class AlarmOutputService:
    """Documented VIGI NVR alarm-output capability and control APIs."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def get_nvr_alarm(self) -> NvrAlarmOutputResponse:
        request = build_nvr_alarm_get_request(self._bearer_headers())
        session = cast(Session, self.session)
        return parse_nvr_alarm_response(session.transport.send(request))

    def set_nvr_alarm(
        self,
        device_id: int,
        alarm_name: str,
        delay_time: AlarmDelayTime,
        enabled: AlarmEnabled,
        alarm_type: AlarmType,
    ) -> ErrorCodeResponse:
        request = build_nvr_alarm_set_request(
            self._bearer_headers(),
            device_id=device_id,
            alarm_name=alarm_name,
            delay_time=delay_time,
            enabled=enabled,
            alarm_type=alarm_type,
        )
        session = cast(Session, self.session)
        return parse_error_code_response(session.transport.send(request), "NVR alarm output")

    def get_ipc_alarm(self, channel_id: int) -> IpcAlarmOutputResponse:
        request = build_ipc_alarm_get_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_ipc_alarm_response(session.transport.send(request), channel_id)

    def set_ipc_alarm(
        self,
        channel_id: int,
        alarm_name: str,
        delay_time: AlarmDelayTime,
        enabled: AlarmEnabled,
    ) -> ErrorCodeResponse:
        request = build_ipc_alarm_set_request(
            self._bearer_headers(),
            channel_id=channel_id,
            alarm_name=alarm_name,
            delay_time=delay_time,
            enabled=enabled,
        )
        session = cast(Session, self.session)
        return parse_error_code_response(session.transport.send(request), "IPC alarm output")

    def manual_nvr_alarm(self, device_id: int, action: AlarmAction) -> AlarmManualResponse:
        request = build_nvr_manual_alarm_request(
            self._bearer_headers(), device_id=device_id, action=action
        )
        session = cast(Session, self.session)
        return parse_alarm_manual_response(session.transport.send(request), "NVR manual alarm")

    def manual_ipc_alarm(self, channel_id: int, action: AlarmAction) -> AlarmManualResponse:
        request = build_ipc_manual_alarm_request(
            self._bearer_headers(), channel_id=channel_id, action=action
        )
        session = cast(Session, self.session)
        return parse_alarm_manual_response(session.transport.send(request), "IPC manual alarm")

    def get_batch_ipc_alarm(self) -> BatchIpcAlarmOutputResponse:
        request = build_batch_ipc_alarm_request(self._bearer_headers())
        session = cast(Session, self.session)
        return parse_batch_ipc_alarm_response(session.transport.send(request))

    def _bearer_headers(self) -> Mapping[str, str]:
        if self.session is None:
            raise AuthenticationError("An authenticated session is required.")
        if not self.session.info.authenticated:
            raise AuthenticationError("An authenticated session is required.")
        if self.session.info.auth_mode is not AuthMode.BEARER:
            raise AuthenticationError("Bearer authentication is required.")

        headers = self.session.info.bearer_headers()
        if "Authorization" not in headers:
            raise AuthenticationError("Bearer authentication is required.")
        return headers


def build_nvr_alarm_get_request(headers: Mapping[str, str]) -> Request:
    return Request(method="GET", path=NVR_ALARM_PATH, headers=headers)


def build_nvr_alarm_set_request(
    headers: Mapping[str, str],
    *,
    device_id: int,
    alarm_name: str,
    delay_time: AlarmDelayTime,
    enabled: AlarmEnabled,
    alarm_type: AlarmType,
) -> Request:
    _require_device_id(device_id)
    _require_name(alarm_name)
    _require_enum(delay_time, AlarmDelayTime, "delay_time")
    _require_enum(enabled, AlarmEnabled, "enabled")
    _require_enum(alarm_type, AlarmType, "alarm_type")
    return _build_json_request(
        headers,
        NVR_ALARM_PATH,
        {
            "device_id": device_id,
            "alarm_name": alarm_name,
            "delay_time": delay_time.value,
            "enabled": enabled.value,
            "alarm_type": alarm_type.value,
        },
    )


def build_ipc_alarm_get_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    return _build_channel_get_request(headers, IPC_ALARM_PATH, channel_id)


def build_ipc_alarm_set_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    alarm_name: str,
    delay_time: AlarmDelayTime,
    enabled: AlarmEnabled,
) -> Request:
    _require_channel(channel_id)
    _require_name(alarm_name)
    _require_enum(delay_time, AlarmDelayTime, "delay_time")
    _require_enum(enabled, AlarmEnabled, "enabled")
    return _build_json_request(
        headers,
        IPC_ALARM_PATH,
        {
            "channel": channel_id,
            "alarm_name": alarm_name,
            "delay_time": delay_time.value,
            "enabled": enabled.value,
        },
    )


def build_nvr_manual_alarm_request(
    headers: Mapping[str, str], *, device_id: int, action: AlarmAction
) -> Request:
    _require_device_id(device_id)
    _require_enum(action, AlarmAction, "action")
    return _build_json_request(
        headers,
        NVR_MANUAL_ALARM_PATH,
        {"device_id": device_id, "action": action.value},
    )


def build_ipc_manual_alarm_request(
    headers: Mapping[str, str], *, channel_id: int, action: AlarmAction
) -> Request:
    _require_channel(channel_id)
    _require_enum(action, AlarmAction, "action")
    return _build_json_request(
        headers,
        IPC_MANUAL_ALARM_PATH,
        {"channel": channel_id, "action": action.value},
    )


def build_batch_ipc_alarm_request(headers: Mapping[str, str]) -> Request:
    return Request(method="GET", path=BATCH_IPC_ALARM_PATH, headers=headers)


def parse_nvr_alarm_response(response: Response) -> NvrAlarmOutputResponse:
    payload, error_code = _parse_payload(response, "NVR alarm output")
    entries = payload.get("alarm_output_info")
    if not isinstance(entries, list):
        raise VigiResponseError("NVR alarm output response alarm_output_info must be a list.")

    outputs: list[NvrAlarmOutput] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise VigiResponseError("NVR alarm output entry must be a JSON object.")
        outputs.append(
            NvrAlarmOutput(
                device_id=_required_int(entry, "device_id", "NVR alarm output"),
                delay_time=_parse_enum(entry, "delay_time", AlarmDelayTime, "NVR alarm output"),
                enabled=_parse_enum(entry, "enabled", AlarmEnabled, "NVR alarm output"),
                alarm_name=_required_string(entry, "alarm_name", "NVR alarm output"),
                alarm_type=_parse_enum(entry, "alarm_type", AlarmType, "NVR alarm output"),
            )
        )
    return NvrAlarmOutputResponse(outputs=tuple(outputs), error_code=error_code)


def parse_ipc_alarm_response(response: Response, channel_id: int) -> IpcAlarmOutputResponse:
    _require_channel(channel_id)
    payload, error_code = _parse_payload(response, "IPC alarm output")
    return IpcAlarmOutputResponse(
        output=IpcAlarmOutput(
            channel_id=channel_id,
            delay_time=_parse_enum(payload, "delay_time", AlarmDelayTime, "IPC alarm output"),
            enabled=_parse_enum(payload, "enabled", AlarmEnabled, "IPC alarm output"),
            alarm_name=_required_string(payload, "alarm_name", "IPC alarm output"),
        ),
        error_code=error_code,
    )


def parse_alarm_manual_response(response: Response, label: str) -> AlarmManualResponse:
    payload, error_code = _parse_payload(response, label)
    return AlarmManualResponse(
        timer=_required_int(payload, "timer", label),
        error_code=error_code,
    )


def parse_error_code_response(response: Response, label: str) -> ErrorCodeResponse:
    _, error_code = _parse_payload(response, label)
    return ErrorCodeResponse(error_code=error_code)


def parse_batch_ipc_alarm_response(response: Response) -> BatchIpcAlarmOutputResponse:
    payload, error_code = _parse_payload(response, "Batch IPC alarm output")
    entries = payload.get("alarm_output")
    if not isinstance(entries, list):
        raise VigiResponseError("Batch IPC alarm output response alarm_output must be a list.")

    outputs: list[BatchIpcAlarmOutput] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise VigiResponseError("Batch IPC alarm output entry must be a JSON object.")
        outputs.append(
            BatchIpcAlarmOutput(
                channel_id=_required_int(entry, "channel", "Batch IPC alarm output"),
                delay_time=_parse_enum(
                    entry, "delay_time", AlarmDelayTime, "Batch IPC alarm output"
                ),
                enabled=_parse_enum(entry, "enabled", AlarmEnabled, "Batch IPC alarm output"),
                alarm_name=_required_string(entry, "alarm_name", "Batch IPC alarm output"),
                manual_alarm_out_supported=_required_flag_string(
                    entry, "manual_alarm_out_supported", "Batch IPC alarm output"
                ),
            )
        )
    return BatchIpcAlarmOutputResponse(outputs=tuple(outputs), error_code=error_code)


def _parse_payload(response: Response, label: str) -> tuple[dict[str, object], int]:
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


def _build_channel_get_request(headers: Mapping[str, str], path: str, channel_id: int) -> Request:
    _require_channel(channel_id)
    query = urlencode({"channel": channel_id})
    return Request(method="GET", path=f"{path}?{query}", headers=headers)


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


def _parse_enum(payload: dict[str, object], key: str, enum_type, label: str):
    value = payload.get(key)
    if not isinstance(value, str):
        raise VigiResponseError(f"{label} field {key} must be a string.")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise VigiResponseError(f"{label} field {key} has an unsupported value.") from exc


def _required_string(payload: dict[str, object], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise VigiResponseError(f"{label} field {key} must be a non-empty string.")
    return value


def _required_flag_string(payload: dict[str, object], key: str, label: str) -> str:
    value = _required_string(payload, key, label)
    if value not in {"0", "1"}:
        raise VigiResponseError(f"{label} field {key} must be '0' or '1'.")
    return value


def _required_int(payload: dict[str, object], key: str, label: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise VigiResponseError(f"{label} field {key} must be an integer.")
    return value


def _require_enum(value: object, enum_type, field_name: str) -> None:
    if type(value) is not enum_type:
        raise ValidationError(f"{field_name} must be a documented enum value.")


def _require_name(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValidationError("alarm_name must be a non-empty string.")


def _require_channel(channel_id: int) -> None:
    if not isinstance(channel_id, int) or isinstance(channel_id, bool) or channel_id <= 0:
        raise ValidationError("channel_id must be a positive integer.")


def _require_device_id(device_id: int) -> None:
    if not isinstance(device_id, int) or isinstance(device_id, bool) or device_id <= 0:
        raise ValidationError("device_id must be a positive integer.")

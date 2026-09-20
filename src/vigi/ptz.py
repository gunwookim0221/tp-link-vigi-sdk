"""VIGI NVR PTZ capability and control support."""

import json
from typing import Mapping, cast
from urllib.parse import urlencode

from vigi.exceptions import AuthenticationError, ValidationError, VigiApiError, VigiResponseError
from vigi.models import (
    ErrorCodeResponse,
    PtzBatchCapability,
    PtzBatchCapabilityResponse,
    PtzCapability,
    PtzCapabilityResponse,
    PtzParkResponse,
    PtzParkSettings,
    PtzPreset,
    PtzPresetResponse,
    PtzTour,
    PtzTourResponse,
    TargetTrackingResponse,
    TargetTrackingSettings,
)
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AuthMode, PtzParkActionMode, PtzTargetTrackMode


PTZ_CAPABILITY_PATH = "/openapi/ptz/capability"
PTZ_MOVE_PATH = "/openapi/ptz/move"
PTZ_PARK_PATH = "/openapi/ptz/park"
PTZ_PRESET_PATH = "/openapi/ptz/preset"
PTZ_TOUR_PATH = "/openapi/ptz/tour"
PTZ_TARGET_TRACK_PATH = "/openapi/ptz/target_track"
PTZ_BATCH_CAPABILITY_PATH = "/openapi/ptz/batch_capability"


class PtzService:
    """Documented VIGI NVR PTZ capability and control APIs."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def get_capability(self, channel_id: int) -> PtzCapabilityResponse:
        request = build_ptz_capability_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_ptz_capability_response(session.transport.send(request), channel_id=channel_id)

    def get_batch_capability(self) -> PtzBatchCapabilityResponse:
        request = build_ptz_batch_capability_request(self._bearer_headers())
        session = cast(Session, self.session)
        return parse_ptz_batch_capability_response(session.transport.send(request))

    def move(self, channel_id: int, direction: int, speed: str) -> ErrorCodeResponse:
        request = build_ptz_move_request(
            self._bearer_headers(),
            channel_id=channel_id,
            direction=direction,
            speed=speed,
        )
        session = cast(Session, self.session)
        return parse_error_code_response(session.transport.send(request), label="PTZ move")

    def get_park(self, channel_id: int) -> PtzParkResponse:
        request = build_ptz_park_get_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_ptz_park_response(session.transport.send(request))

    def set_park(
        self,
        channel_id: int,
        action_mode: PtzParkActionMode,
        park_time: int,
        action_id: int,
        enabled: int,
    ) -> ErrorCodeResponse:
        request = build_ptz_park_set_request(
            self._bearer_headers(),
            channel_id=channel_id,
            action_mode=action_mode,
            park_time=park_time,
            action_id=action_id,
            enabled=enabled,
        )
        session = cast(Session, self.session)
        return parse_error_code_response(session.transport.send(request), label="PTZ park")

    def list_presets(self, channel_id: int) -> PtzPresetResponse:
        request = build_ptz_preset_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_ptz_preset_response(session.transport.send(request))

    def list_tours(self, channel_id: int) -> PtzTourResponse:
        request = build_ptz_tour_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_ptz_tour_response(session.transport.send(request))

    def get_target_tracking(self, channel_id: int) -> TargetTrackingResponse:
        request = build_ptz_target_track_get_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_target_tracking_response(session.transport.send(request))

    def set_target_tracking(
        self,
        channel_id: int,
        enabled: PtzTargetTrackMode,
        people_enabled: PtzTargetTrackMode,
    ) -> ErrorCodeResponse:
        request = build_ptz_target_track_set_request(
            self._bearer_headers(),
            channel_id=channel_id,
            enabled=enabled,
            people_enabled=people_enabled,
        )
        session = cast(Session, self.session)
        return parse_error_code_response(
            session.transport.send(request), label="PTZ target tracking"
        )

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


def build_ptz_capability_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    _require_positive_int(channel_id, "channel_id")
    return _build_get_request(headers, PTZ_CAPABILITY_PATH, {"channel": channel_id})


def build_ptz_batch_capability_request(headers: Mapping[str, str]) -> Request:
    return Request(method="GET", path=PTZ_BATCH_CAPABILITY_PATH, headers=headers)


def build_ptz_move_request(
    headers: Mapping[str, str], *, channel_id: int, direction: int, speed: str
) -> Request:
    _require_positive_int(channel_id, "channel_id")
    _require_int(direction, "direction")
    if not isinstance(speed, str):
        raise ValidationError("speed must be a string.")
    return _build_json_request(
        headers,
        PTZ_MOVE_PATH,
        {"channel": channel_id, "direction": direction, "speed": speed},
    )


def build_ptz_park_get_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    _require_positive_int(channel_id, "channel_id")
    return _build_get_request(headers, PTZ_PARK_PATH, {"channel": channel_id})


def build_ptz_park_set_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    action_mode: PtzParkActionMode,
    park_time: int,
    action_id: int,
    enabled: int,
) -> Request:
    _require_positive_int(channel_id, "channel_id")
    if type(action_mode) is not PtzParkActionMode:
        raise ValidationError("action_mode must be PtzParkActionMode.PRESET or TOUR.")
    _require_int(park_time, "park_time")
    _require_int(action_id, "action_id")
    _require_binary_int(enabled, "enabled")
    return _build_json_request(
        headers,
        PTZ_PARK_PATH,
        {
            "action_mode": action_mode.value,
            "park_time": park_time,
            "action_id": action_id,
            "enabled": enabled,
            "channel": channel_id,
        },
    )


def build_ptz_preset_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    _require_positive_int(channel_id, "channel_id")
    return _build_get_request(headers, PTZ_PRESET_PATH, {"channel": channel_id})


def build_ptz_tour_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    _require_positive_int(channel_id, "channel_id")
    return _build_get_request(headers, PTZ_TOUR_PATH, {"channel": channel_id})


def build_ptz_target_track_get_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    _require_positive_int(channel_id, "channel_id")
    return _build_get_request(headers, PTZ_TARGET_TRACK_PATH, {"channel": channel_id})


def build_ptz_target_track_set_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    enabled: PtzTargetTrackMode,
    people_enabled: PtzTargetTrackMode,
) -> Request:
    _require_positive_int(channel_id, "channel_id")
    if type(enabled) is not PtzTargetTrackMode:
        raise ValidationError("enabled must be a PtzTargetTrackMode value.")
    if type(people_enabled) is not PtzTargetTrackMode:
        raise ValidationError("people_enabled must be a PtzTargetTrackMode value.")
    return _build_json_request(
        headers,
        PTZ_TARGET_TRACK_PATH,
        {
            "channel": channel_id,
            "enabled": enabled.value,
            "people_enabled": people_enabled.value,
        },
    )


def parse_ptz_capability_response(response: Response, *, channel_id: int) -> PtzCapabilityResponse:
    _require_positive_int(channel_id, "channel_id")
    payload, error_code = _parse_payload(response, "PTZ capability")
    return PtzCapabilityResponse(
        channel_id=channel_id,
        capability=_parse_ptz_capability(payload),
        error_code=error_code,
    )


def parse_ptz_batch_capability_response(response: Response) -> PtzBatchCapabilityResponse:
    payload, error_code = _parse_payload(response, "PTZ batch capability")
    entries = payload.get("capability")
    if not isinstance(entries, list):
        raise VigiResponseError("PTZ batch capability response capability must be a list.")

    capabilities: list[PtzBatchCapability] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise VigiResponseError("PTZ batch capability entry must be a JSON object.")
        channel_id = _required_int(entry, "id", "PTZ batch capability")
        capabilities.append(
            PtzBatchCapability(
                channel_id=channel_id,
                capability=_parse_ptz_capability(entry),
            )
        )
    return PtzBatchCapabilityResponse(capabilities=tuple(capabilities), error_code=error_code)


def parse_error_code_response(response: Response, *, label: str) -> ErrorCodeResponse:
    _, error_code = _parse_payload(response, label)
    return ErrorCodeResponse(error_code=error_code)


def parse_ptz_park_response(response: Response) -> PtzParkResponse:
    payload, error_code = _parse_payload(response, "PTZ park")
    return PtzParkResponse(
        settings=PtzParkSettings(
            action_mode=_parse_enum(payload, "action_mode", PtzParkActionMode, "PTZ park"),
            park_time=_required_int(payload, "park_time", "PTZ park"),
            action_id=_required_int(payload, "action_id", "PTZ park"),
            enabled=_required_binary_int(payload, "enabled", "PTZ park"),
        ),
        error_code=error_code,
    )


def parse_ptz_preset_response(response: Response) -> PtzPresetResponse:
    payload, error_code = _parse_payload(response, "PTZ preset")
    entries = payload.get("preset")
    if not isinstance(entries, list):
        raise VigiResponseError("PTZ preset response preset must be a list.")

    presets: list[PtzPreset] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise VigiResponseError("PTZ preset entry must be a JSON object.")
        presets.append(
            PtzPreset(
                preset_id=_required_int(entry, "preset_id", "PTZ preset"),
                read_only=_required_binary_int(entry, "read_only", "PTZ preset"),
                name=_required_string(entry, "name", "PTZ preset"),
            )
        )
    return PtzPresetResponse(presets=tuple(presets), error_code=error_code)


def parse_ptz_tour_response(response: Response) -> PtzTourResponse:
    payload, error_code = _parse_payload(response, "PTZ tour")
    entries = payload.get("tour")
    if not isinstance(entries, list):
        raise VigiResponseError("PTZ tour response tour must be a list.")

    tours: list[PtzTour] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise VigiResponseError("PTZ tour entry must be a JSON object.")
        tours.append(
            PtzTour(
                tour_id=_required_int(entry, "tour_id", "PTZ tour"),
                preset_count=_required_int(entry, "preset_count", "PTZ tour"),
                name=_optional_string(entry, "name", "PTZ tour"),
                preset_ids=_optional_string_array(entry, "preset_id", "PTZ tour"),
                times=_optional_string_array(entry, "time", "PTZ tour"),
                speeds=_optional_string_array(entry, "speed", "PTZ tour"),
            )
        )
    return PtzTourResponse(tours=tuple(tours), error_code=error_code)


def parse_target_tracking_response(response: Response) -> TargetTrackingResponse:
    payload, error_code = _parse_payload(response, "PTZ target tracking")
    return TargetTrackingResponse(
        settings=TargetTrackingSettings(
            enabled=_parse_enum(
                payload,
                "enabled",
                PtzTargetTrackMode,
                "PTZ target tracking",
            ),
            people_enabled=_parse_enum(
                payload,
                "people_enabled",
                PtzTargetTrackMode,
                "PTZ target tracking",
            ),
        ),
        error_code=error_code,
    )


def _parse_ptz_capability(payload: dict[str, object]) -> PtzCapability:
    return PtzCapability(
        pan_tilt_supported=_required_string(payload, "pan_tilt_supported", "PTZ capability"),
        zoom_supported=_required_string(payload, "zoom_supported", "PTZ capability"),
        preset_supported=_required_string(payload, "preset_supported", "PTZ capability"),
        preset_number_max=_required_string(payload, "preset_number_max", "PTZ capability"),
        tour_number_max=_required_string(payload, "tour_number_max", "PTZ capability"),
        pattern_number_max=_required_string(payload, "pattern_number_max", "PTZ capability"),
        tour_spots_number_max=_required_string(payload, "tour_spots_number_max", "PTZ capability"),
        tour_supported=_required_string(payload, "tour_supported", "PTZ capability"),
        pattern_supported=_required_string(payload, "pattern_supported", "PTZ capability"),
        aperture_supported=_required_string(payload, "aperture_supported", "PTZ capability"),
        focus_supported=_required_string(payload, "focus_supported", "PTZ capability"),
        calibrate_supported=_required_string(payload, "calibrate_supported", "PTZ capability"),
        diagonal_motion_supported=_required_string(
            payload, "diagonal_motion_supported", "PTZ capability"
        ),
        x_min=_required_string(payload, "x_min", "PTZ capability"),
        x_max=_required_string(payload, "x_max", "PTZ capability"),
        y_min=_required_string(payload, "y_min", "PTZ capability"),
        y_max=_required_string(payload, "y_max", "PTZ capability"),
        z_min=_required_string(payload, "z_min", "PTZ capability"),
        z_max=_required_string(payload, "z_max", "PTZ capability"),
        move_min=_required_string(payload, "move_min", "PTZ capability"),
        move_max=_required_string(payload, "move_max", "PTZ capability"),
        tour_stay_time_max=_required_string(payload, "tour_stay_time_max", "PTZ capability"),
        tour_stay_time_min=_required_string(payload, "tour_stay_time_min", "PTZ capability"),
    )


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


def _build_get_request(
    headers: Mapping[str, str], path: str, query_values: Mapping[str, object]
) -> Request:
    query = urlencode(query_values)
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


def _required_string(payload: dict[str, object], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise VigiResponseError(f"{label} field {key} must be a non-empty string.")
    return value


def _optional_string(payload: dict[str, object], key: str, label: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise VigiResponseError(f"{label} field {key} must be a string when present.")
    return value


def _optional_string_array(
    payload: dict[str, object], key: str, label: str
) -> tuple[str, ...] | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise VigiResponseError(f"{label} field {key} must be a string array when present.")
    return tuple(value)


def _required_int(payload: dict[str, object], key: str, label: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise VigiResponseError(f"{label} field {key} must be an integer.")
    return value


def _required_binary_int(payload: dict[str, object], key: str, label: str) -> int:
    value = _required_int(payload, key, label)
    if value not in {0, 1}:
        raise VigiResponseError(f"{label} field {key} must be 0 or 1.")
    return value


def _parse_enum(payload: dict[str, object], key: str, enum_type, label: str):
    value = payload.get(key)
    if not isinstance(value, str):
        raise VigiResponseError(f"{label} field {key} must be a string.")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise VigiResponseError(f"{label} field {key} has an unsupported value.") from exc


def _require_positive_int(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer.")


def _require_int(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{field_name} must be an integer.")


def _require_binary_int(value: int, field_name: str) -> None:
    _require_int(value, field_name)
    if value not in {0, 1}:
        raise ValidationError(f"{field_name} must be 0 or 1.")

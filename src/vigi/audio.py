"""VIGI NVR audio capability and sound-control support."""

import json
from typing import Mapping, cast
from urllib.parse import urlencode

from vigi.exceptions import AuthenticationError, ValidationError, VigiApiError, VigiResponseError
from vigi.models import (
    AudioCapability,
    AudioCapabilityResponse,
    AudioChannelCapabilityResponse,
    AudioControlResponse,
    AudioInputSound,
    AudioInputSoundResponse,
    AudioOutputSound,
    AudioOutputSoundResponse,
)
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AudioToggle, AuthMode


AUDIO_OUTPUT_SOUND_PATH = "/openapi/audio/output/sound"
AUDIO_INPUT_SOUND_PATH = "/openapi/audio/input/sound"
AUDIO_CHANNEL_CAPABILITY_PATH = "/openapi/audio/channel_capability"
AUDIO_CAPABILITY_PATH = "/openapi/audio/capability"


class AudioService:
    """Documented VIGI NVR audio capability and sound APIs."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def get_output_sound(self, channel_id: int) -> AudioOutputSoundResponse:
        request = build_audio_output_sound_get_request(
            self._bearer_headers(), channel_id=channel_id
        )
        session = cast(Session, self.session)
        return parse_audio_output_sound_response(session.transport.send(request))

    def get_input_sound(self, channel_id: int) -> AudioInputSoundResponse:
        request = build_audio_input_sound_get_request(self._bearer_headers(), channel_id=channel_id)
        session = cast(Session, self.session)
        return parse_audio_input_sound_response(session.transport.send(request))

    def set_output_sound(
        self,
        channel_id: int,
        mute: AudioToggle,
        volume: int,
        system_volume: int,
    ) -> AudioControlResponse:
        request = build_audio_output_sound_set_request(
            self._bearer_headers(),
            channel_id=channel_id,
            mute=mute,
            volume=volume,
            system_volume=system_volume,
        )
        session = cast(Session, self.session)
        return parse_audio_control_response(session.transport.send(request))

    def set_input_sound(
        self,
        channel_id: int,
        mute: AudioToggle,
        volume: int,
        noise_cancelling: AudioToggle,
    ) -> AudioControlResponse:
        request = build_audio_input_sound_set_request(
            self._bearer_headers(),
            channel_id=channel_id,
            mute=mute,
            volume=volume,
            noise_cancelling=noise_cancelling,
        )
        session = cast(Session, self.session)
        return parse_audio_control_response(session.transport.send(request))

    def get_channel_capability(self, channel_id: int) -> AudioChannelCapabilityResponse:
        request = build_audio_channel_capability_request(
            self._bearer_headers(), channel_id=channel_id
        )
        session = cast(Session, self.session)
        return parse_audio_channel_capability_response(session.transport.send(request), channel_id)

    def get_capability(self) -> AudioCapabilityResponse:
        request = build_audio_capability_request(self._bearer_headers())
        session = cast(Session, self.session)
        return parse_audio_capability_response(session.transport.send(request))

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


def build_audio_output_sound_get_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    return _build_channel_get_request(headers, AUDIO_OUTPUT_SOUND_PATH, channel_id)


def build_audio_input_sound_get_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    return _build_channel_get_request(headers, AUDIO_INPUT_SOUND_PATH, channel_id)


def build_audio_output_sound_set_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    mute: AudioToggle,
    volume: int,
    system_volume: int,
) -> Request:
    _require_channel(channel_id)
    _require_toggle(mute, "mute")
    _require_volume(volume, "volume")
    _require_volume(system_volume, "system_volume")
    return _build_json_request(
        headers,
        AUDIO_OUTPUT_SOUND_PATH,
        {
            "mute": mute.value,
            "volume": volume,
            "system_volume": system_volume,
            "channel": channel_id,
        },
    )


def build_audio_input_sound_set_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    mute: AudioToggle,
    volume: int,
    noise_cancelling: AudioToggle,
) -> Request:
    _require_channel(channel_id)
    _require_toggle(mute, "mute")
    _require_volume(volume, "volume")
    _require_toggle(noise_cancelling, "noise_cancelling")
    return _build_json_request(
        headers,
        AUDIO_INPUT_SOUND_PATH,
        {
            "mute": mute.value,
            "volume": volume,
            "noise_cancelling": noise_cancelling.value,
            "channel": channel_id,
        },
    )


def build_audio_channel_capability_request(
    headers: Mapping[str, str], *, channel_id: int
) -> Request:
    return _build_channel_get_request(headers, AUDIO_CHANNEL_CAPABILITY_PATH, channel_id)


def build_audio_capability_request(headers: Mapping[str, str]) -> Request:
    return Request(method="GET", path=AUDIO_CAPABILITY_PATH, headers=headers)


def parse_audio_output_sound_response(response: Response) -> AudioOutputSoundResponse:
    payload, error_code = _parse_payload(response, "Audio output sound")
    return AudioOutputSoundResponse(
        settings=AudioOutputSound(
            mute=_parse_toggle(payload, "mute", "Audio output sound"),
            volume=_required_volume(payload, "volume", "Audio output sound"),
            system_volume=_required_volume(payload, "system_volume", "Audio output sound"),
        ),
        error_code=error_code,
    )


def parse_audio_input_sound_response(response: Response) -> AudioInputSoundResponse:
    payload, error_code = _parse_payload(response, "Audio input sound")
    return AudioInputSoundResponse(
        settings=AudioInputSound(
            mute=_parse_toggle(payload, "mute", "Audio input sound"),
            volume=_required_volume(payload, "volume", "Audio input sound"),
            noise_cancelling=_parse_toggle(payload, "noise_cancelling", "Audio input sound"),
        ),
        error_code=error_code,
    )


def parse_audio_channel_capability_response(
    response: Response, channel_id: int
) -> AudioChannelCapabilityResponse:
    _require_channel(channel_id)
    payload, error_code = _parse_payload(response, "Audio channel capability")
    return AudioChannelCapabilityResponse(
        channel_id=channel_id,
        capability=_parse_audio_capability(payload, "Audio channel capability"),
        error_code=error_code,
    )


def parse_audio_capability_response(response: Response) -> AudioCapabilityResponse:
    payload, error_code = _parse_payload(response, "Audio capability")
    return AudioCapabilityResponse(
        capability=_parse_audio_capability(payload, "Audio capability"),
        error_code=error_code,
    )


def parse_audio_control_response(response: Response) -> AudioControlResponse:
    payload, error_code = _parse_payload(response, "Audio control")
    sub_code = payload.get("sub_code")
    if sub_code is not None and (not isinstance(sub_code, int) or isinstance(sub_code, bool)):
        raise VigiResponseError("Audio control field sub_code must be an integer when present.")
    return AudioControlResponse(error_code=error_code, sub_code=sub_code)


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


def _parse_audio_capability(payload: dict[str, object], label: str) -> AudioCapability:
    speaker_enabled = _required_int(payload, "speaker_enable", label)
    microphone_enabled = _required_int(payload, "microphone_enable", label)
    if speaker_enabled not in {0, 1}:
        raise VigiResponseError(f"{label} field speaker_enable must be 0 or 1.")
    if microphone_enabled not in {0, 1}:
        raise VigiResponseError(f"{label} field microphone_enable must be 0 or 1.")
    return AudioCapability(
        speaker_enabled=speaker_enabled,
        microphone_enabled=microphone_enabled,
    )


def _parse_toggle(payload: dict[str, object], key: str, label: str) -> AudioToggle:
    value = payload.get(key)
    if not isinstance(value, str):
        raise VigiResponseError(f"{label} field {key} must be a string.")
    try:
        return AudioToggle(value)
    except ValueError as exc:
        raise VigiResponseError(f"{label} field {key} has an unsupported value.") from exc


def _required_int(payload: dict[str, object], key: str, label: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise VigiResponseError(f"{label} field {key} must be an integer.")
    return value


def _required_volume(payload: dict[str, object], key: str, label: str) -> int:
    value = _required_int(payload, key, label)
    if not 0 <= value <= 100:
        raise VigiResponseError(f"{label} field {key} must be from 0 to 100.")
    return value


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


def _require_channel(channel_id: int) -> None:
    if not isinstance(channel_id, int) or isinstance(channel_id, bool) or channel_id <= 0:
        raise ValidationError("channel_id must be a positive integer.")


def _require_toggle(value: AudioToggle, field_name: str) -> None:
    if type(value) is not AudioToggle:
        raise ValidationError(f"{field_name} must be an AudioToggle value.")


def _require_volume(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
        raise ValidationError(f"{field_name} must be an integer from 0 to 100.")

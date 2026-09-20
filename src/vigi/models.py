"""Core data models for the SDK."""

from dataclasses import dataclass
from datetime import datetime

from vigi.exceptions import ValidationError
from vigi.types import (
    AlarmDelayTime,
    AlarmEnabled,
    AlarmType,
    AudioToggle,
    ChannelStatus,
    DeviceType,
    PtzParkActionMode,
    PtzTargetTrackMode,
    StreamType,
)


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValidationError(f"{field_name} must not be empty.")


def _require_positive(value: int, field_name: str) -> None:
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")


@dataclass(frozen=True, slots=True)
class TimeRange:
    """Start and end timestamps for recording and replay workflows."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start >= self.end:
            raise ValidationError("TimeRange start must be before end.")


@dataclass(frozen=True, slots=True)
class NvrInfo:
    """Static identity metadata for a VIGI NVR."""

    model: str
    hardware_version: str | None = None
    firmware_version: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.model, "model")


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    """Device metadata returned by future documented inventory APIs."""

    device_id: str
    name: str
    device_type: DeviceType = DeviceType.UNKNOWN
    ip_address: str | None = None
    mac_address: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.device_id, "device_id")


@dataclass(frozen=True, slots=True)
class ChannelInfo:
    """Channel metadata for a device attached to an NVR."""

    channel_id: int
    name: str | None = None
    status: ChannelStatus = ChannelStatus.UNKNOWN
    device: DeviceInfo | None = None

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")


@dataclass(frozen=True, slots=True)
class AddedDevice:
    """Device entry returned by NVR ``GET /openapi/added_devices``."""

    channel_id: int
    name: str
    alias: str
    online: ChannelStatus
    ip_address: str
    mac_address: str

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")
        _require_non_empty(self.name, "name")
        _require_non_empty(self.alias, "alias")
        _require_non_empty(self.ip_address, "ip_address")
        _require_non_empty(self.mac_address, "mac_address")


@dataclass(frozen=True, slots=True)
class AddedDevicesResponse:
    """Parsed response for NVR ``GET /openapi/added_devices``."""

    devices: tuple[AddedDevice, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class ScannedDevice:
    """A device discovered by NVR ``GET /openapi/device_scan``."""

    ip_address: str
    name: str
    connect_protocol: str
    port: str
    mac_address: str
    model: str

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.ip_address, "ip_address"),
            (self.name, "name"),
            (self.connect_protocol, "connect_protocol"),
            (self.port, "port"),
            (self.mac_address, "mac_address"),
            (self.model, "model"),
        ):
            if not isinstance(value, str) or not value:
                raise ValidationError(f"{field_name} must be a non-empty string.")


@dataclass(frozen=True, slots=True)
class DeviceScanResponse:
    """Parsed response for NVR ``GET /openapi/device_scan``."""

    devices: tuple[ScannedDevice, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class ErrorCodeResponse:
    """Response containing the documented OpenAPI result code only."""

    error_code: int

    def __post_init__(self) -> None:
        if not isinstance(self.error_code, int) or isinstance(self.error_code, bool):
            raise ValidationError("error_code must be an integer.")


@dataclass(frozen=True, slots=True)
class PtzCapability:
    """Documented PTZ capability fields for one channel."""

    pan_tilt_supported: str
    zoom_supported: str
    preset_supported: str
    preset_number_max: str
    tour_number_max: str
    pattern_number_max: str
    tour_spots_number_max: str
    tour_supported: str
    pattern_supported: str
    aperture_supported: str
    focus_supported: str
    calibrate_supported: str
    diagonal_motion_supported: str
    x_min: str
    x_max: str
    y_min: str
    y_max: str
    z_min: str
    z_max: str
    move_min: str
    move_max: str
    tour_stay_time_max: str
    tour_stay_time_min: str

    def __post_init__(self) -> None:
        flags = (
            (self.pan_tilt_supported, "pan_tilt_supported"),
            (self.zoom_supported, "zoom_supported"),
            (self.preset_supported, "preset_supported"),
            (self.tour_supported, "tour_supported"),
            (self.pattern_supported, "pattern_supported"),
            (self.aperture_supported, "aperture_supported"),
            (self.focus_supported, "focus_supported"),
            (self.calibrate_supported, "calibrate_supported"),
            (self.diagonal_motion_supported, "diagonal_motion_supported"),
        )
        for value, field_name in flags:
            if value not in {"0", "1"}:
                raise ValidationError(f"{field_name} must be '0' or '1'.")
        for value, field_name in (
            (self.preset_number_max, "preset_number_max"),
            (self.tour_number_max, "tour_number_max"),
            (self.pattern_number_max, "pattern_number_max"),
            (self.tour_spots_number_max, "tour_spots_number_max"),
            (self.x_min, "x_min"),
            (self.x_max, "x_max"),
            (self.y_min, "y_min"),
            (self.y_max, "y_max"),
            (self.z_min, "z_min"),
            (self.z_max, "z_max"),
            (self.move_min, "move_min"),
            (self.move_max, "move_max"),
            (self.tour_stay_time_max, "tour_stay_time_max"),
            (self.tour_stay_time_min, "tour_stay_time_min"),
        ):
            if not isinstance(value, str) or not value:
                raise ValidationError(f"{field_name} must be a non-empty string.")


@dataclass(frozen=True, slots=True)
class PtzCapabilityResponse:
    """Parsed response for per-channel PTZ capability."""

    channel_id: int
    capability: PtzCapability
    error_code: int

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")


@dataclass(frozen=True, slots=True)
class PtzBatchCapability:
    """Documented PTZ capability associated with a channel identifier."""

    channel_id: int
    capability: PtzCapability

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")


@dataclass(frozen=True, slots=True)
class PtzBatchCapabilityResponse:
    """Parsed response for batch PTZ capability."""

    capabilities: tuple[PtzBatchCapability, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class PtzParkSettings:
    """Documented PTZ park settings for one channel."""

    action_mode: PtzParkActionMode
    park_time: int
    action_id: int
    enabled: int

    def __post_init__(self) -> None:
        if type(self.action_mode) is not PtzParkActionMode:
            raise ValidationError("action_mode must be PtzParkActionMode.PRESET or TOUR.")
        for value, field_name in ((self.park_time, "park_time"), (self.action_id, "action_id")):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValidationError(f"{field_name} must be an integer.")
        if self.enabled not in {0, 1} or isinstance(self.enabled, bool):
            raise ValidationError("enabled must be 0 or 1.")


@dataclass(frozen=True, slots=True)
class PtzParkResponse:
    """Parsed response for PTZ park settings."""

    settings: PtzParkSettings
    error_code: int


@dataclass(frozen=True, slots=True)
class PtzPreset:
    """Documented PTZ preset entry."""

    preset_id: int
    read_only: int
    name: str

    def __post_init__(self) -> None:
        if not 1 <= self.preset_id <= 300:
            raise ValidationError("preset_id must be between 1 and 300.")
        if self.read_only not in {0, 1} or isinstance(self.read_only, bool):
            raise ValidationError("read_only must be 0 or 1.")
        _require_non_empty(self.name, "name")


@dataclass(frozen=True, slots=True)
class PtzPresetResponse:
    """Parsed response for the documented PTZ preset list."""

    presets: tuple[PtzPreset, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class PtzTour:
    """Documented PTZ tour entry, preserving omitted empty-tour fields."""

    tour_id: int
    preset_count: int
    name: str | None = None
    preset_ids: tuple[str, ...] | None = None
    times: tuple[str, ...] | None = None
    speeds: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.tour_id <= 8:
            raise ValidationError("tour_id must be between 1 and 8.")
        if not isinstance(self.preset_count, int) or isinstance(self.preset_count, bool):
            raise ValidationError("preset_count must be an integer.")
        if self.preset_count < 0:
            raise ValidationError("preset_count must not be negative.")
        if self.name is not None and (not isinstance(self.name, str) or not self.name):
            raise ValidationError("name must be a non-empty string when present.")
        for values, field_name in (
            (self.preset_ids, "preset_ids"),
            (self.times, "times"),
            (self.speeds, "speeds"),
        ):
            if values is not None and any(not isinstance(value, str) for value in values):
                raise ValidationError(f"{field_name} must contain only strings.")


@dataclass(frozen=True, slots=True)
class PtzTourResponse:
    """Parsed response for the documented PTZ tour list."""

    tours: tuple[PtzTour, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class TargetTrackingSettings:
    """Documented PTZ target-tracking settings for one channel."""

    enabled: PtzTargetTrackMode
    people_enabled: PtzTargetTrackMode

    def __post_init__(self) -> None:
        if type(self.enabled) is not PtzTargetTrackMode:
            raise ValidationError("enabled must be a PtzTargetTrackMode value.")
        if type(self.people_enabled) is not PtzTargetTrackMode:
            raise ValidationError("people_enabled must be a PtzTargetTrackMode value.")


@dataclass(frozen=True, slots=True)
class TargetTrackingResponse:
    """Parsed response for PTZ target tracking."""

    settings: TargetTrackingSettings
    error_code: int


@dataclass(frozen=True, slots=True)
class AudioCapability:
    """Documented audio input/output capability flags."""

    speaker_enabled: int
    microphone_enabled: int

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.speaker_enabled, "speaker_enabled"),
            (self.microphone_enabled, "microphone_enabled"),
        ):
            if value not in {0, 1} or isinstance(value, bool):
                raise ValidationError(f"{field_name} must be 0 or 1.")


@dataclass(frozen=True, slots=True)
class AudioCapabilityResponse:
    """Parsed NVR-level audio capability response."""

    capability: AudioCapability
    error_code: int


@dataclass(frozen=True, slots=True)
class AudioChannelCapabilityResponse:
    """Parsed channel-specific audio capability response."""

    channel_id: int
    capability: AudioCapability
    error_code: int

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")


@dataclass(frozen=True, slots=True)
class AudioOutputSound:
    """Documented output sound settings."""

    mute: AudioToggle
    volume: int
    system_volume: int

    def __post_init__(self) -> None:
        if type(self.mute) is not AudioToggle:
            raise ValidationError("mute must be an AudioToggle value.")
        _require_volume(self.volume, "volume")
        _require_volume(self.system_volume, "system_volume")


@dataclass(frozen=True, slots=True)
class AudioOutputSoundResponse:
    """Parsed output sound response."""

    settings: AudioOutputSound
    error_code: int


@dataclass(frozen=True, slots=True)
class AudioInputSound:
    """Documented input sound settings."""

    mute: AudioToggle
    volume: int
    noise_cancelling: AudioToggle

    def __post_init__(self) -> None:
        if type(self.mute) is not AudioToggle:
            raise ValidationError("mute must be an AudioToggle value.")
        if type(self.noise_cancelling) is not AudioToggle:
            raise ValidationError("noise_cancelling must be an AudioToggle value.")
        _require_volume(self.volume, "volume")


@dataclass(frozen=True, slots=True)
class AudioInputSoundResponse:
    """Parsed input sound response."""

    settings: AudioInputSound
    error_code: int


@dataclass(frozen=True, slots=True)
class AudioControlResponse:
    """Documented audio mutation response."""

    error_code: int
    sub_code: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.error_code, int) or isinstance(self.error_code, bool):
            raise ValidationError("error_code must be an integer.")
        if self.sub_code is not None and (
            not isinstance(self.sub_code, int) or isinstance(self.sub_code, bool)
        ):
            raise ValidationError("sub_code must be an integer when present.")


@dataclass(frozen=True, slots=True)
class NvrAlarmOutput:
    """Documented NVR alarm-output settings."""

    device_id: int
    delay_time: AlarmDelayTime
    enabled: AlarmEnabled
    alarm_name: str
    alarm_type: AlarmType

    def __post_init__(self) -> None:
        _require_positive(self.device_id, "device_id")
        if type(self.delay_time) is not AlarmDelayTime:
            raise ValidationError("delay_time must be an AlarmDelayTime value.")
        if type(self.enabled) is not AlarmEnabled:
            raise ValidationError("enabled must be an AlarmEnabled value.")
        if type(self.alarm_type) is not AlarmType:
            raise ValidationError("alarm_type must be an AlarmType value.")
        _require_non_empty(self.alarm_name, "alarm_name")


@dataclass(frozen=True, slots=True)
class NvrAlarmOutputResponse:
    """Parsed NVR alarm-output settings response."""

    outputs: tuple[NvrAlarmOutput, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class IpcAlarmOutput:
    """Documented IPC-channel alarm-output settings."""

    channel_id: int
    delay_time: AlarmDelayTime
    enabled: AlarmEnabled
    alarm_name: str

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")
        if type(self.delay_time) is not AlarmDelayTime:
            raise ValidationError("delay_time must be an AlarmDelayTime value.")
        if type(self.enabled) is not AlarmEnabled:
            raise ValidationError("enabled must be an AlarmEnabled value.")
        _require_non_empty(self.alarm_name, "alarm_name")


@dataclass(frozen=True, slots=True)
class IpcAlarmOutputResponse:
    """Parsed IPC-channel alarm-output settings response."""

    output: IpcAlarmOutput
    error_code: int


@dataclass(frozen=True, slots=True)
class BatchIpcAlarmOutput:
    """Documented batch IPC alarm-output capability/settings entry."""

    channel_id: int
    delay_time: AlarmDelayTime
    enabled: AlarmEnabled
    alarm_name: str
    manual_alarm_out_supported: str

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")
        if type(self.delay_time) is not AlarmDelayTime:
            raise ValidationError("delay_time must be an AlarmDelayTime value.")
        if type(self.enabled) is not AlarmEnabled:
            raise ValidationError("enabled must be an AlarmEnabled value.")
        _require_non_empty(self.alarm_name, "alarm_name")
        if self.manual_alarm_out_supported not in {"0", "1"}:
            raise ValidationError("manual_alarm_out_supported must be '0' or '1'.")


@dataclass(frozen=True, slots=True)
class BatchIpcAlarmOutputResponse:
    """Parsed batch IPC alarm-output response."""

    outputs: tuple[BatchIpcAlarmOutput, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class AlarmManualResponse:
    """Documented manual alarm-output control response."""

    timer: int
    error_code: int

    def __post_init__(self) -> None:
        if not isinstance(self.timer, int) or isinstance(self.timer, bool):
            raise ValidationError("timer must be an integer.")


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """A module/version entry returned by NVR ``GET /openapi/module_list``."""

    name: str
    version: int

    def __post_init__(self) -> None:
        _require_non_empty(self.name, "name")
        if not isinstance(self.version, int) or isinstance(self.version, bool):
            raise ValidationError("version must be an integer.")


@dataclass(frozen=True, slots=True)
class ModuleListResponse:
    """Parsed response for NVR ``GET /openapi/module_list``."""

    modules: tuple[ModuleInfo, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class SnapshotImage:
    """JPEG bytes returned by NVR ``GET /openapi/snapshot``."""

    data: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.data, bytes) or not self.data:
            raise ValidationError("snapshot data must be non-empty bytes.")


@dataclass(frozen=True, slots=True)
class RecordDay:
    """A day with recording returned by ``GET /openapi/record/days``."""

    day: str

    def __post_init__(self) -> None:
        _require_non_empty(self.day, "day")


@dataclass(frozen=True, slots=True)
class RecordDaysResponse:
    """Parsed response for NVR ``GET /openapi/record/days``."""

    days: tuple[RecordDay, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class RecordSearchProcessResponse:
    """Parsed response for NVR ``GET /openapi/record/search/free_process``."""

    process_id: int
    error_code: int

    def __post_init__(self) -> None:
        _require_positive(self.process_id, "process_id")


@dataclass(frozen=True, slots=True)
class RecordSegment:
    """Recording time range returned by ``GET /openapi/record/search/results``."""

    start_time: str
    end_time: str

    def __post_init__(self) -> None:
        _require_non_empty(self.start_time, "start_time")
        _require_non_empty(self.end_time, "end_time")


@dataclass(frozen=True, slots=True)
class RecordSearchResultsResponse:
    """Parsed response for NVR ``GET /openapi/record/search/results``."""

    results: tuple[RecordSegment, ...]
    error_code: int


@dataclass(frozen=True, slots=True)
class RtspStreamInfo:
    """RTSP stream metadata for future live and replay helpers."""

    channel_id: int
    stream_type: StreamType
    time_range: TimeRange | None = None

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")


def _require_volume(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
        raise ValidationError(f"{field_name} must be an integer from 0 to 100.")

"""Core data models for the SDK."""

from dataclasses import dataclass
from datetime import datetime

from vigi.exceptions import ValidationError
from vigi.types import ChannelStatus, DeviceType, RecordType, StreamType


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
class RecordSearchQuery:
    """Input shape for a future documented recording search flow."""

    channel_id: int
    day: str

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")
        _require_non_empty(self.day, "day")


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
class RecordFile:
    """Recording time range metadata returned by future search APIs."""

    channel_id: int
    time_range: TimeRange
    record_type: RecordType = RecordType.UNKNOWN

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")


@dataclass(frozen=True, slots=True)
class RtspStreamInfo:
    """RTSP stream metadata for future live and replay helpers."""

    channel_id: int
    stream_type: StreamType
    time_range: TimeRange | None = None

    def __post_init__(self) -> None:
        _require_positive(self.channel_id, "channel_id")

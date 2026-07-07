"""Python SDK skeleton for TP-Link VIGI NVR OpenAPI."""

from vigi.auth import AuthConfig
from vigi.capabilities import Capability
from vigi.client import VigiClient
from vigi.devices import DeviceService
from vigi.exceptions import (
    AuthenticationError,
    CapabilityError,
    DeviceError,
    RecordError,
    StreamError,
    ValidationError,
    VigiError,
)
from vigi.models import (
    ChannelInfo,
    DeviceInfo,
    NvrInfo,
    RecordFile,
    RecordSearchQuery,
    RtspStreamInfo,
    TimeRange,
)
from vigi.records import RecordService
from vigi.stream import StreamService
from vigi.types import (
    AuthMode,
    CapabilityName,
    ChannelStatus,
    DeviceType,
    RecordType,
    StreamType,
)

__all__ = [
    "AuthConfig",
    "AuthMode",
    "AuthenticationError",
    "Capability",
    "CapabilityName",
    "CapabilityError",
    "ChannelInfo",
    "ChannelStatus",
    "DeviceInfo",
    "DeviceError",
    "DeviceService",
    "DeviceType",
    "NvrInfo",
    "RecordFile",
    "RecordError",
    "RecordSearchQuery",
    "RecordService",
    "RecordType",
    "RtspStreamInfo",
    "StreamError",
    "StreamService",
    "StreamType",
    "TimeRange",
    "ValidationError",
    "VigiClient",
    "VigiError",
]

__version__ = "0.0.0"

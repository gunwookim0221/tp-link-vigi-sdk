"""Python SDK skeleton for TP-Link VIGI NVR OpenAPI."""

from vigi.auth import AuthConfig, AuthService
from vigi.auth_provider import AuthProvider, AuthenticationContext, AuthenticationResult
from vigi.capabilities import Capability
from vigi.client import VigiClient
from vigi.devices import DeviceService
from vigi.exceptions import (
    AuthenticationError,
    CapabilityError,
    ConnectionError,
    DeviceError,
    RecordError,
    StreamError,
    TimeoutError,
    TransportError,
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
from vigi.session import Session, SessionInfo
from vigi.stream import StreamService
from vigi.transport import Request, Response, Timeout, Transport, TransportConfig
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
    "AuthProvider",
    "AuthService",
    "AuthenticationContext",
    "AuthenticationError",
    "AuthenticationResult",
    "Capability",
    "CapabilityName",
    "CapabilityError",
    "ChannelInfo",
    "ChannelStatus",
    "ConnectionError",
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
    "Request",
    "Response",
    "RtspStreamInfo",
    "Session",
    "SessionInfo",
    "StreamError",
    "StreamService",
    "StreamType",
    "Timeout",
    "TimeoutError",
    "TimeRange",
    "Transport",
    "TransportConfig",
    "TransportError",
    "ValidationError",
    "VigiClient",
    "VigiError",
]

__version__ = "0.0.0"

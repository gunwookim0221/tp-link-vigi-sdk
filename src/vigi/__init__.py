"""Python SDK for TP-Link VIGI NVR OpenAPI."""

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
from vigi.crypto import calculate_digest_response, sha256_hex
from vigi.http_transport import HttpTransport
from vigi.models import (
    AddedDevice,
    AddedDevicesResponse,
    ChannelInfo,
    DeviceInfo,
    NvrInfo,
    RecordDay,
    RecordDaysResponse,
    RecordSearchProcessResponse,
    RecordSearchResultsResponse,
    RecordSegment,
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
    "AddedDevice",
    "AddedDevicesResponse",
    "calculate_digest_response",
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
    "HttpTransport",
    "NvrInfo",
    "RecordDay",
    "RecordDaysResponse",
    "RecordError",
    "RecordSearchProcessResponse",
    "RecordSearchResultsResponse",
    "RecordSegment",
    "RecordService",
    "Request",
    "Response",
    "RtspStreamInfo",
    "Session",
    "SessionInfo",
    "sha256_hex",
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

__version__ = "0.1.0"

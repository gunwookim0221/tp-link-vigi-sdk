"""Shared enum types for the SDK data model layer."""

from enum import Enum


class AuthMode(str, Enum):
    """Documented authentication modes used by VIGI OpenAPI surfaces."""

    DIGEST = "digest"
    BEARER = "bearer"


class CapabilityName(str, Enum):
    """Known capability names used to gate future SDK behavior."""

    AUTH_TOKEN = "auth.token"
    DEVICE_ADDED_DEVICES = "device.added_devices"
    RECORDING_SEARCH = "recording.search"
    STREAM_LIVE_RTSP = "stream.live_rtsp"
    STREAM_REPLAY_RTSP = "stream.replay_rtsp"


class DeviceType(str, Enum):
    """Device type values known to the SDK.

    TODO: Extend only when official TP-Link documentation or verified device
    responses justify additional concrete values.
    """

    UNKNOWN = "unknown"


class ChannelStatus(str, Enum):
    """Channel online status values from documented device inventory behavior."""

    OFFLINE = "0"
    ONLINE = "1"
    UNKNOWN = "unknown"


class RecordType(str, Enum):
    """Recording type values used before official subtype mapping is verified."""

    UNKNOWN = "unknown"


class StreamType(str, Enum):
    """RTSP stream selectors documented by the OpenAPI stream interface."""

    MAIN = "1"
    MINOR = "2"

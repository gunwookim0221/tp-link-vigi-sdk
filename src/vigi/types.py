"""Shared enum types for the SDK data model layer."""

from enum import Enum


class AuthMode(str, Enum):
    """Documented authentication modes used by VIGI OpenAPI surfaces."""

    DIGEST = "digest"
    BEARER = "bearer"


class ConnectionProtocol(str, Enum):
    """Connection protocols documented by NVR device-management APIs."""

    TP_LINK = "TP-LINK"
    ONVIF = "ONVIF"
    RTSP = "RTSP"


class RecordControlMode(str, Enum):
    """Documented NVR recording-control modes."""

    AUTO = "auto"
    OFF = "off"


class PtzParkActionMode(str, Enum):
    """Documented PTZ park destinations."""

    PRESET = "preset"
    TOUR = "tour"


class PtzTargetTrackMode(str, Enum):
    """Documented PTZ target-tracking modes."""

    ON = "on"
    OFF = "off"


class AudioToggle(str, Enum):
    """Documented audio on/off values."""

    ON = "on"
    OFF = "off"


class AlarmEnabled(str, Enum):
    """Documented alarm-output enabled values."""

    ON = "on"
    OFF = "off"


class AlarmType(str, Enum):
    """Documented alarm-output electrical types."""

    NORMALLY_OPEN = "NO"
    NORMALLY_CLOSED = "NC"


class AlarmAction(str, Enum):
    """Documented manual alarm-output actions."""

    START = "start"
    STOP = "stop"


class AlarmDelayTime(str, Enum):
    """Documented alarm-output delay durations in seconds."""

    FIVE = "5"
    TEN = "10"
    THIRTY = "30"
    SIXTY = "60"
    ONE_HUNDRED_TWENTY = "120"
    THREE_HUNDRED = "300"
    SIX_HUNDRED = "600"


class CapabilityName(str, Enum):
    """Known capability names used to gate future SDK behavior."""

    AUTH_TOKEN = "auth.token"
    MODULE_DISCOVERY = "capability.module_discovery"
    DEVICE_ADDED_DEVICES = "device.added_devices"
    SNAPSHOT = "snapshot.current"
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


class StreamType(str, Enum):
    """RTSP stream selectors documented by the OpenAPI stream interface."""

    MAIN = "1"
    MINOR = "2"

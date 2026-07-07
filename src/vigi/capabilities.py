"""Capability declarations for documented and verified SDK features."""

from enum import Enum


class Capability(str, Enum):
    """Known capability keys used to gate future SDK behavior."""

    AUTH_TOKEN = "auth.token"
    DEVICE_ADDED_DEVICES = "device.added_devices"
    RECORDING_SEARCH = "recording.search"
    STREAM_LIVE_RTSP = "stream.live_rtsp"
    STREAM_REPLAY_RTSP = "stream.replay_rtsp"

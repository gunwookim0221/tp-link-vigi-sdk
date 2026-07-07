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
    VigiError,
)
from vigi.records import RecordService
from vigi.stream import StreamService

__all__ = [
    "AuthConfig",
    "AuthenticationError",
    "Capability",
    "CapabilityError",
    "DeviceError",
    "DeviceService",
    "RecordError",
    "RecordService",
    "StreamError",
    "StreamService",
    "VigiClient",
    "VigiError",
]

__version__ = "0.0.0"

"""Client facade for the SDK skeleton."""

from dataclasses import dataclass, field

from vigi.auth import AuthConfig, AuthService
from vigi.devices import DeviceService
from vigi.records import RecordService
from vigi.stream import StreamService


@dataclass(slots=True)
class VigiClient:
    """Minimal client facade that wires future service objects."""

    auth_config: AuthConfig
    auth: AuthService = field(init=False)
    devices: DeviceService = field(init=False)
    records: RecordService = field(init=False)
    stream: StreamService = field(init=False)

    def __post_init__(self) -> None:
        self.auth = AuthService(self.auth_config)
        self.devices = DeviceService()
        self.records = RecordService()
        self.stream = StreamService()

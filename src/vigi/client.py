"""Client facade for the TP-Link VIGI SDK."""

from dataclasses import dataclass, field
from typing import cast

from vigi.alarm import AlarmOutputService
from vigi.auth_provider import AuthProvider
from vigi.auth import AuthConfig, AuthService
from vigi.audio import AudioService
from vigi.capabilities import CapabilityService
from vigi.devices import DeviceService
from vigi.http_transport import HttpTransport
from vigi.ptz import PtzService
from vigi.records import RecordService
from vigi.session import Session, SessionInfo
from vigi.snapshots import SnapshotService
from vigi.stream import StreamService
from vigi.transport import Transport, TransportConfig
from vigi.types import CapabilityName


@dataclass(slots=True)
class VigiClient:
    """Client facade that wires the current service objects."""

    auth_config: AuthConfig
    transport: Transport | None = None
    auth_provider: AuthProvider | None = None
    auth: AuthService = field(init=False)
    session: Session = field(init=False)
    capabilities: CapabilityService = field(init=False)
    devices: DeviceService = field(init=False)
    records: RecordService = field(init=False)
    snapshots: SnapshotService = field(init=False)
    stream: StreamService = field(init=False)
    ptz: PtzService = field(init=False)
    audio: AudioService = field(init=False)
    alarm_outputs: AlarmOutputService = field(init=False)

    def __post_init__(self) -> None:
        self.auth = AuthService(self.auth_config)
        if self.transport is None:
            self.transport = HttpTransport(
                TransportConfig(
                    base_url=f"https://{self.auth_config.host}:{self.auth_config.port}",
                    verify_ssl=self.auth_config.verify_tls,
                )
            )
        if self.auth_provider is None:
            self.auth_provider = self.auth
        self.session = Session(transport=self.transport, info=SessionInfo())
        self.capabilities = CapabilityService(self.session)
        self.devices = DeviceService(self.session)
        self.records = RecordService(self.session)
        self.snapshots = SnapshotService(self.session)
        self.ptz = PtzService(self.session)
        self.audio = AudioService(self.session)
        self.alarm_outputs = AlarmOutputService(self.session)
        self.stream = StreamService(
            {
                CapabilityName.STREAM_LIVE_RTSP,
                CapabilityName.STREAM_REPLAY_RTSP,
            }
        )

    def login(self) -> None:
        """Authenticate the client and update session state."""

        auth_provider = cast(AuthProvider, self.auth_provider)
        transport = cast(Transport, self.transport)
        result = auth_provider.authenticate(self.auth._default_context(), transport)
        self.session.info = result.session_info

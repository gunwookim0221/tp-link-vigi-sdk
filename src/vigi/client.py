"""Client facade for the TP-Link VIGI SDK."""

from dataclasses import dataclass, field
from typing import cast

from vigi.auth_provider import AuthProvider
from vigi.auth import AuthConfig, AuthService
from vigi.devices import DeviceService
from vigi.http_transport import HttpTransport
from vigi.records import RecordService
from vigi.session import Session, SessionInfo
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
    devices: DeviceService = field(init=False)
    records: RecordService = field(init=False)
    stream: StreamService = field(init=False)

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
        self.devices = DeviceService(self.session)
        self.records = RecordService(self.session)
        self.stream = StreamService({CapabilityName.STREAM_REPLAY_RTSP})

    def login(self) -> None:
        """Authenticate the client and update session state."""

        auth_provider = cast(AuthProvider, self.auth_provider)
        transport = cast(Transport, self.transport)
        result = auth_provider.authenticate(self.auth._default_context(), transport)
        self.session.info = result.session_info

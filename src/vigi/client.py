"""Client facade for the SDK skeleton."""

from dataclasses import dataclass, field

from vigi.auth_provider import AuthProvider
from vigi.auth import AuthConfig, AuthService
from vigi.devices import DeviceService
from vigi.http_transport import HttpTransport
from vigi.records import RecordService
from vigi.session import Session, SessionInfo
from vigi.stream import StreamService
from vigi.transport import Transport, TransportConfig


@dataclass(slots=True)
class VigiClient:
    """Minimal client facade that wires future service objects."""

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
        self.devices = DeviceService()
        self.records = RecordService()
        self.stream = StreamService()

    def login(self) -> None:
        """Authenticate the client and update session state."""

        result = self.auth_provider.authenticate(self.auth._default_context(), self.transport)
        self.session.info = result.session_info

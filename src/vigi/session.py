"""Session boundary objects for future authenticated SDK calls."""

from dataclasses import dataclass, field

from vigi.transport import Transport
from vigi.types import AuthMode


@dataclass(frozen=True, slots=True)
class SessionInfo:
    """Authentication/session state shared with future transport calls."""

    authenticated: bool = False
    auth_mode: AuthMode | None = None


@dataclass(slots=True)
class Session:
    """Lightweight session container for transport and auth state."""

    transport: Transport
    info: SessionInfo = field(default_factory=SessionInfo)

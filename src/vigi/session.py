"""Session boundary objects for authenticated SDK calls."""

from dataclasses import dataclass, field
from typing import Mapping

from vigi.transport import Transport
from vigi.types import AuthMode


@dataclass(frozen=True, slots=True)
class SessionInfo:
    """Authentication/session state shared with transport calls."""

    authenticated: bool = False
    auth_mode: AuthMode | None = None
    token_type: str | None = None
    expires_in: int | None = None
    access_token: str | None = field(default=None, repr=False)
    refresh_token: str | None = field(default=None, repr=False)

    def bearer_headers(self) -> Mapping[str, str]:
        """Return Authorization headers for authenticated OpenAPI requests."""

        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}


@dataclass(slots=True)
class Session:
    """Lightweight session container for transport and auth state."""

    transport: Transport
    info: SessionInfo = field(default_factory=SessionInfo)

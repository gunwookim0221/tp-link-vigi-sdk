"""Authentication provider boundary for future OpenAPI authentication."""

from dataclasses import dataclass, field
from typing import Mapping

from vigi.session import SessionInfo
from vigi.types import AuthMode


@dataclass(frozen=True, slots=True)
class AuthenticationContext:
    """Input context for a future authentication provider."""

    base_url: str
    username: str
    auth_mode: AuthMode = AuthMode.DIGEST


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    """Result shape for future authentication providers."""

    session_info: SessionInfo
    headers: Mapping[str, str] = field(default_factory=dict)


class AuthProvider:
    """Authentication strategy interface placeholder."""

    def authenticate(self, context: AuthenticationContext) -> AuthenticationResult:
        """Authenticate in a future implementation."""

        raise NotImplementedError("Authentication provider is not implemented yet.")

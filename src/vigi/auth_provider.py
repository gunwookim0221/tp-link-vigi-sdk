"""Authentication provider boundary for OpenAPI authentication."""

from dataclasses import dataclass, field
from typing import Mapping

from vigi.session import SessionInfo
from vigi.transport import Transport
from vigi.types import AuthMode


@dataclass(frozen=True, slots=True)
class AuthenticationContext:
    """Input context for an authentication provider."""

    base_url: str
    username: str
    password: str = field(repr=False)
    auth_mode: AuthMode = AuthMode.DIGEST
    token_path: str = "/openapi/token"


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    """Result shape for authentication providers."""

    session_info: SessionInfo
    headers: Mapping[str, str] = field(default_factory=dict, repr=False)


class AuthProvider:
    """Authentication strategy interface."""

    def authenticate(
        self, context: AuthenticationContext, transport: Transport
    ) -> AuthenticationResult:
        """Authenticate using the provided transport."""

        raise NotImplementedError("Authentication provider is not implemented yet.")

"""Authentication placeholders for the SDK skeleton."""

from dataclasses import dataclass, field

from vigi.auth_provider import AuthProvider, AuthenticationContext, AuthenticationResult


@dataclass(frozen=True, slots=True)
class AuthConfig:
    """Connection credentials for future documented OpenAPI authentication."""

    host: str
    username: str
    password: str = field(repr=False)
    port: int = 20443
    verify_tls: bool = True


class AuthService(AuthProvider):
    """Placeholder for the documented Digest-to-Bearer authentication flow."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config

    def authenticate(
        self, context: AuthenticationContext | None = None
    ) -> AuthenticationResult:
        """Authenticate with the NVR in a later implementation phase."""

        raise NotImplementedError("Authentication is planned for a later phase.")

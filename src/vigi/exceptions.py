"""Exception hierarchy for the SDK skeleton."""


class VigiError(Exception):
    """Base exception for all SDK errors."""


class VigiConnectionError(VigiError):
    """Raised for future connection failures."""


class VigiTimeoutError(VigiConnectionError):
    """Raised for future timeout failures."""


class VigiAuthenticationError(VigiError):
    """Raised for future authentication failures."""


class AuthenticationError(VigiAuthenticationError):
    """Public shorthand for authentication failures."""


class VigiAuthorizationError(VigiError):
    """Raised for future authorization failures."""


class VigiApiError(VigiError):
    """Raised for future documented OpenAPI errors."""


class VigiCapabilityError(VigiError):
    """Raised when a feature is not supported by declared capabilities."""


class CapabilityError(VigiCapabilityError):
    """Public shorthand for capability failures."""


class VigiResponseError(VigiError):
    """Raised for future response parsing failures."""


class DeviceError(VigiError):
    """Raised for future device API failures."""


class RecordError(VigiError):
    """Raised for future recording API failures."""


class StreamError(VigiError):
    """Raised for future stream API failures."""

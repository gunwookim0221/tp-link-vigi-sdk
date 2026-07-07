"""Exception hierarchy for the SDK skeleton."""


class VigiError(Exception):
    """Base exception for all SDK errors."""


class VigiConnectionError(VigiError):
    """Raised for future connection failures."""


class ConnectionError(VigiConnectionError):
    """Public shorthand for connection failures."""


class VigiTimeoutError(VigiConnectionError):
    """Raised for future timeout failures."""


class TimeoutError(VigiTimeoutError):
    """Public shorthand for timeout failures."""


class VigiAuthenticationError(VigiError):
    """Raised for future authentication failures."""


class AuthenticationError(VigiAuthenticationError):
    """Public shorthand for authentication failures."""


class VigiAuthorizationError(VigiError):
    """Raised for future authorization failures."""


class VigiApiError(VigiError):
    """Raised for future documented OpenAPI errors."""


class VigiTransportError(VigiError):
    """Raised for future transport failures."""


class TransportError(VigiTransportError):
    """Public shorthand for transport failures."""


class VigiCapabilityError(VigiError):
    """Raised when a feature is not supported by declared capabilities."""


class CapabilityError(VigiCapabilityError):
    """Public shorthand for capability failures."""


class VigiResponseError(VigiError):
    """Raised for future response parsing failures."""


class VigiValidationError(VigiError, ValueError):
    """Raised when SDK data models receive invalid values."""


class ValidationError(VigiValidationError):
    """Public shorthand for validation failures."""


class DeviceError(VigiError):
    """Raised for future device API failures."""


class RecordError(VigiError):
    """Raised for future recording API failures."""


class StreamError(VigiError):
    """Raised for future stream API failures."""

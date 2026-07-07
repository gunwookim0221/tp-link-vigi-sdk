"""Transport boundary types for future HTTP integrations."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Timeout:
    """Timeout settings for future transport implementations."""

    connect: float = 10.0
    read: float = 30.0


@dataclass(frozen=True, slots=True)
class TransportConfig:
    """Configuration for the transport boundary."""

    base_url: str
    timeout: Timeout = field(default_factory=Timeout)
    verify_ssl: bool = True


@dataclass(frozen=True, slots=True)
class Request:
    """SDK transport request shape without an HTTP client dependency."""

    method: str
    path: str
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes | None = None


@dataclass(frozen=True, slots=True)
class Response:
    """SDK transport response shape without an HTTP client dependency."""

    status_code: int
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes | None = None


class Transport:
    """Transport interface placeholder.

    A concrete implementation will adapt this boundary to an HTTP library in a
    later phase.
    """

    def __init__(self, config: TransportConfig) -> None:
        self.config = config

    def send(self, request: Request) -> Response:
        """Send a request in a future transport implementation."""

        raise NotImplementedError("HTTP transport is not implemented yet.")


EMPTY_HEADERS: Mapping[str, str] = MappingProxyType({})

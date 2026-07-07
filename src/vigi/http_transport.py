"""Standard-library HTTP transport for OpenAPI calls."""

from __future__ import annotations

import ssl
from builtins import TimeoutError as BuiltinTimeoutError
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from vigi.exceptions import ConnectionError, TimeoutError, TransportError
from vigi.transport import Request, Response, Transport, TransportConfig


class HttpTransport(Transport):
    """urllib-based transport adapter.

    This module adds no runtime dependency. It is intentionally thin so tests can
    continue using fake transports without network access.
    """

    def __init__(self, config: TransportConfig) -> None:
        super().__init__(config)

    def send(self, request: Request) -> Response:
        url = self._build_url(request.path)
        url_request = UrlRequest(
            url,
            data=request.body,
            headers=dict(request.headers),
            method=request.method.upper(),
        )
        context = None if self.config.verify_ssl else ssl._create_unverified_context()

        try:
            with urlopen(
                url_request,
                timeout=self.config.timeout.read,
                context=context,
            ) as response:
                return Response(
                    status_code=response.status,
                    headers=dict(response.headers.items()),
                    body=response.read(),
                )
        except BuiltinTimeoutError as exc:
            raise TimeoutError("HTTP request timed out.") from exc
        except HTTPError as exc:
            return Response(
                status_code=exc.code,
                headers=dict(exc.headers.items()),
                body=exc.read(),
            )
        except URLError as exc:
            raise ConnectionError("HTTP request failed.") from exc
        except OSError as exc:
            raise TransportError("HTTP transport failed.") from exc

    def _build_url(self, path: str) -> str:
        base_url = self.config.base_url.rstrip("/")
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{base_url}{normalized_path}"

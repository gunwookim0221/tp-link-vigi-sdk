"""NVR snapshot retrieval support."""

from collections.abc import Mapping
from typing import cast
from urllib.parse import urlencode

from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError, ValidationError
from vigi.models import SnapshotImage
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AuthMode


SNAPSHOT_PATH = "/openapi/snapshot"


class SnapshotService:
    """Retrieve current channel snapshots documented by NVR OpenAPI V1.4."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def get_snapshot(self, channel_id: int) -> SnapshotImage:
        """Get the current JPEG snapshot for an NVR channel."""

        headers = self._bearer_headers()
        session = cast(Session, self.session)
        request = build_snapshot_request(headers, channel_id=channel_id)
        return parse_snapshot_response(session.transport.send(request))

    def _bearer_headers(self) -> Mapping[str, str]:
        if self.session is None:
            raise AuthenticationError("An authenticated session is required.")
        if not self.session.info.authenticated:
            raise AuthenticationError("An authenticated session is required.")
        if self.session.info.auth_mode is not AuthMode.BEARER:
            raise AuthenticationError("Bearer authentication is required.")

        headers = self.session.info.bearer_headers()
        if "Authorization" not in headers:
            raise AuthenticationError("Bearer authentication is required.")
        return headers


def build_snapshot_request(headers: Mapping[str, str], *, channel_id: int) -> Request:
    """Build the documented current-snapshot request."""

    _require_positive_channel(channel_id)
    query = urlencode({"channel": channel_id})
    return Request(method="GET", path=f"{SNAPSHOT_PATH}?{query}", headers=headers)


def parse_snapshot_response(response: Response) -> SnapshotImage:
    """Parse a documented JPEG response without accepting JSON as an image."""

    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"Snapshot endpoint returned HTTP {response.status_code}.")

    data = response.body or b""
    content_type = _get_header(response, "Content-Type")
    if content_type and content_type.split(";", 1)[0].strip().lower() != "image/jpeg":
        raise VigiResponseError("Snapshot response content type is not image/jpeg.")
    if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
        raise VigiResponseError("Snapshot response is not a valid JPEG image.")
    return SnapshotImage(data=data)


def _require_positive_channel(channel_id: int) -> None:
    if not isinstance(channel_id, int) or isinstance(channel_id, bool) or channel_id <= 0:
        raise ValidationError("channel_id must be a positive integer.")


def _get_header(response: Response, name: str) -> str | None:
    for key, value in response.headers.items():
        if key.lower() == name.lower():
            return value
    return None

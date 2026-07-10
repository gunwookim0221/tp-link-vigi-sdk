"""Documented RTSP stream URL helpers."""

from collections.abc import Collection
from datetime import datetime
import re

from vigi.exceptions import CapabilityError, ValidationError
from vigi.models import RtspStreamInfo
from vigi.types import CapabilityName


_REPLAY_TIME_FORMAT = "%Y%m%dt%H%M%Sz"
_REPLAY_TIME_PATTERN = re.compile(r"^\d{8}t\d{6}z$")


class StreamService:
    """Build documented RTSP URLs without opening RTSP connections."""

    def __init__(self, capabilities: Collection[CapabilityName] | None = None) -> None:
        self._capabilities = frozenset(
            {CapabilityName.STREAM_REPLAY_RTSP} if capabilities is None else capabilities
        )

    def build_replay_url(
        self,
        host: str,
        channel_id: int,
        start_time: str,
        end_time: str,
        stream: int = 1,
    ) -> str:
        """Build the documented RTSP replay URL for an explicit UTC time range.

        This helper only builds a URL. RTSP Digest authentication and opening a
        stream remain the responsibility of an external RTSP client.
        """

        if CapabilityName.STREAM_REPLAY_RTSP not in self._capabilities:
            raise CapabilityError("RTSP replay URL construction is not supported.")

        _validate_host(host)
        _validate_positive_int(channel_id, "channel_id")
        if not isinstance(stream, int) or isinstance(stream, bool) or stream != 1:
            raise ValidationError("Replay stream must be the documented value 1.")
        _validate_replay_time(start_time, "start_time")
        _validate_replay_time(end_time, "end_time")
        if start_time >= end_time:
            raise ValidationError("start_time must be before end_time.")

        return (
            f"rtsp://{host}/replay/{channel_id}/1/avm?"
            f"starttime={start_time}&endtime={end_time}"
        )

    def open_replay(self, stream: RtspStreamInfo) -> None:
        """Remain explicitly unsupported; this SDK does not open RTSP streams."""

        raise NotImplementedError(
            "Opening RTSP replay is not supported; use build_replay_url instead."
        )


def _validate_host(host: str) -> None:
    if not isinstance(host, str) or not host or host != host.strip():
        raise ValidationError("host must be a non-empty hostname or IP address.")
    if any(marker in host for marker in ("://", "/", "@", ":", "?", "#")):
        raise ValidationError(
            "host must not include a scheme, credentials, port, path, query, or fragment."
        )


def _validate_positive_int(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer.")


def _validate_replay_time(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not _REPLAY_TIME_PATTERN.fullmatch(value):
        raise ValidationError(f"{field_name} must use UTC format YYYYMMDDtHHMMSSz.")
    try:
        datetime.strptime(value, _REPLAY_TIME_FORMAT)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be a valid UTC time.") from exc

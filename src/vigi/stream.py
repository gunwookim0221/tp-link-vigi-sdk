"""Stream service placeholders."""

from vigi.models import RtspStreamInfo


class StreamService:
    """Placeholder for documented RTSP stream support."""

    def open_replay(self, stream: RtspStreamInfo) -> None:
        """Open replay through a future documented RTSP strategy."""

        raise NotImplementedError("RTSP replay support is planned for Phase 5.")

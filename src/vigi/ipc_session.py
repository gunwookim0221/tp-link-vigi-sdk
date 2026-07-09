"""Internal IPC session state for standalone camera verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IpcSessionInfo:
    """Authenticated IPC control session state.

    This is intentionally internal and is not exported from ``vigi.__init__``.
    """

    host: str
    port: int
    stok: str = field(repr=False)
    issued_at: datetime | None = None
    username: str | None = field(default=None, repr=False)

    def stok_path(self) -> str:
        """Return the documented IPC post-auth control path."""

        return f"/stok={self.stok}"

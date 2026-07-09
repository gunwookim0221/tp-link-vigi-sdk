"""Internal IPC control request builders."""

from __future__ import annotations

import json
from typing import Any

from vigi.exceptions import CapabilityError
from vigi.ipc_auth import CONTENT_TYPE_JSON
from vigi.ipc_session import IpcSessionInfo
from vigi.transport import Request


GET_STREAM_PORT = "getStreamPort"


class _RedactedPath(str):
    def __repr__(self) -> str:
        return "'/stok=<redacted>'"


def build_ipc_method_request(
    session: IpcSessionInfo, method: str, params: dict[str, Any] | None = None
) -> Request:
    """Build a documented IPC control method request.

    Only ``getStreamPort`` is allowed in this internal verification layer.
    """

    if method != GET_STREAM_PORT:
        raise CapabilityError("Unsupported IPC method for internal verification.")

    payload: dict[str, Any] = {"method": method}
    if params is not None:
        payload["params"] = params
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return Request(
        method="POST",
        path=_RedactedPath(session.stok_path()),
        headers=CONTENT_TYPE_JSON,
        body=body,
    )


def build_get_stream_port_request(session: IpcSessionInfo) -> Request:
    """Build the official IPC getStreamPort request."""

    return build_ipc_method_request(session, GET_STREAM_PORT)

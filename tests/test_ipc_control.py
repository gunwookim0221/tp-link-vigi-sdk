import json

import pytest

from vigi.exceptions import CapabilityError
from vigi.ipc_control import build_get_stream_port_request, build_ipc_method_request
from vigi.ipc_session import IpcSessionInfo


def test_get_stream_port_request_creation() -> None:
    session = IpcSessionInfo(host="camera.local", port=20443, stok="secret-stok")

    request = build_get_stream_port_request(session)

    assert request.method == "POST"
    assert request.path == "/stok=secret-stok"
    assert request.headers == {"Content-Type": "application/json"}
    assert json.loads(request.body or b"{}") == {"method": "getStreamPort"}
    assert "secret-stok" not in repr(request)
    assert "secret-stok" not in repr(session)


def test_ipc_method_builder_only_allows_get_stream_port() -> None:
    session = IpcSessionInfo(host="camera.local", port=20443, stok="secret-stok")

    request = build_ipc_method_request(session, "getStreamPort")

    assert json.loads(request.body or b"{}") == {"method": "getStreamPort"}
    with pytest.raises(CapabilityError, match="Unsupported IPC method"):
        build_ipc_method_request(session, "getDeviceInfo")

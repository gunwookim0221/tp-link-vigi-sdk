import json
import os

import pytest

from vigi.http_transport import HttpTransport
from vigi.ipc_auth import IpcAuthConfig, IpcAuthService
from vigi.ipc_control import build_get_stream_port_request
from vigi.transport import TransportConfig


def _integration_config_available() -> bool:
    return all(
        os.getenv(name)
        for name in ("VIGI_IPC_HOST", "VIGI_IPC_USERNAME", "VIGI_IPC_PASSWORD")
    )


@pytest.mark.skipif(
    not _integration_config_available(),
    reason="VIGI IPC auth integration environment is not configured.",
)
def test_integration_ipc_do_auth_and_get_stream_port() -> None:
    verify_ssl = os.getenv("VIGI_IPC_VERIFY_TLS", "true").lower() not in {
        "0",
        "false",
        "no",
    }
    port = int(os.getenv("VIGI_IPC_PORT", "20443"))
    config = IpcAuthConfig(
        host=os.environ["VIGI_IPC_HOST"],
        username=os.environ["VIGI_IPC_USERNAME"],
        password=os.environ["VIGI_IPC_PASSWORD"],
        port=port,
        verify_tls=verify_ssl,
    )
    transport = HttpTransport(
        TransportConfig(
            base_url=f"https://{config.host}:{config.port}",
            verify_ssl=config.verify_tls,
        )
    )

    session = IpcAuthService(config).authenticate(transport)
    response = transport.send(build_get_stream_port_request(session))

    assert response.status_code == 200
    assert response.body
    payload = json.loads(response.body.decode("utf-8"))
    assert payload["method"] == "getStreamPort"
    assert payload["errCode"] == 0
    assert isinstance(payload["result"]["streamPort"], str)
    assert payload["result"]["streamPort"]

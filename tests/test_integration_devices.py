import os

import pytest

from vigi import AuthConfig, VigiClient
from vigi.types import ChannelStatus


def _integration_config_available() -> bool:
    return all(os.getenv(name) for name in ("VIGI_HOST", "VIGI_USERNAME", "VIGI_PASSWORD"))


@pytest.mark.skipif(
    not _integration_config_available(),
    reason="VIGI device inventory integration environment is not configured.",
)
def test_integration_added_devices_inventory() -> None:
    verify_ssl = os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}
    port = int(os.getenv("VIGI_PORT", "20443"))
    client = VigiClient(
        AuthConfig(
            host=os.environ["VIGI_HOST"],
            username=os.environ["VIGI_USERNAME"],
            password=os.environ["VIGI_PASSWORD"],
            port=port,
            verify_tls=verify_ssl,
        )
    )

    client.login()
    result = client.devices.list_added_devices()

    assert isinstance(result.devices, tuple)
    assert len(result.devices) >= 0
    assert result.error_code == 0
    for device in result.devices:
        assert isinstance(device.channel_id, int)
        assert device.channel_id > 0
        assert isinstance(device.name, str)
        assert isinstance(device.alias, str)
        assert device.online in {ChannelStatus.ONLINE, ChannelStatus.OFFLINE}
        assert isinstance(device.ip_address, str)
        assert isinstance(device.mac_address, str)

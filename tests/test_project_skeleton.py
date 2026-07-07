import pytest

from vigi import (
    AuthConfig,
    AuthenticationError,
    Capability,
    CapabilityError,
    DeviceError,
    DeviceService,
    RecordError,
    RecordService,
    StreamError,
    StreamService,
    VigiClient,
    VigiError,
)


def test_public_classes_import() -> None:
    assert AuthConfig
    assert AuthenticationError
    assert Capability
    assert CapabilityError
    assert DeviceError
    assert DeviceService
    assert RecordError
    assert RecordService
    assert StreamError
    assert StreamService
    assert VigiClient
    assert VigiError


def test_client_wires_placeholder_services() -> None:
    client = VigiClient(AuthConfig(host="nvr.local", username="admin", password="secret"))

    assert isinstance(client.devices, DeviceService)
    assert isinstance(client.records, RecordService)
    assert isinstance(client.stream, StreamService)


def test_placeholder_methods_are_not_implemented() -> None:
    client = VigiClient(AuthConfig(host="nvr.local", username="admin", password="secret"))

    with pytest.raises(NotImplementedError):
        client.auth.authenticate()

    with pytest.raises(NotImplementedError):
        client.devices.list_added_devices()

    with pytest.raises(NotImplementedError):
        client.records.search()

    with pytest.raises(NotImplementedError):
        client.stream.open_replay()

import pytest
from datetime import datetime, timezone

from vigi import (
    AuthConfig,
    AuthenticationError,
    Capability,
    CapabilityError,
    DeviceError,
    DeviceService,
    RecordError,
    RecordSearchQuery,
    RecordService,
    RtspStreamInfo,
    StreamError,
    StreamService,
    StreamType,
    TimeRange,
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
    assert RecordSearchQuery
    assert RecordService
    assert RtspStreamInfo
    assert StreamError
    assert StreamService
    assert StreamType
    assert TimeRange
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
        client.records.search(RecordSearchQuery(channel_id=1, day="20260707"))

    with pytest.raises(NotImplementedError):
        client.stream.open_replay(
            RtspStreamInfo(
                channel_id=1,
                stream_type=StreamType.MAIN,
                time_range=TimeRange(
                    start=datetime(2026, 7, 7, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2026, 7, 7, 1, 0, tzinfo=timezone.utc),
                ),
            )
        )

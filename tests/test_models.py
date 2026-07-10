from datetime import datetime, timezone

import pytest

from vigi import (
    ChannelInfo,
    ChannelStatus,
    DeviceInfo,
    DeviceType,
    NvrInfo,
    RtspStreamInfo,
    StreamType,
    TimeRange,
    ValidationError,
)


def _utc(hour: int) -> datetime:
    return datetime(2026, 7, 7, hour, 0, tzinfo=timezone.utc)


def test_core_models_can_be_created() -> None:
    time_range = TimeRange(start=_utc(0), end=_utc(1))
    device = DeviceInfo(
        device_id="device-1",
        name="Front Door",
        device_type=DeviceType.UNKNOWN,
    )

    nvr = NvrInfo(model="VIGI NVR1008H-8P", hardware_version="V1.20")
    channel = ChannelInfo(channel_id=1, status=ChannelStatus.ONLINE, device=device)
    stream = RtspStreamInfo(channel_id=1, stream_type=StreamType.MAIN, time_range=time_range)

    assert nvr.model == "VIGI NVR1008H-8P"
    assert channel.device == device
    assert stream.stream_type is StreamType.MAIN


def test_time_range_requires_start_before_end() -> None:
    TimeRange(start=_utc(0), end=_utc(1))

    with pytest.raises(ValidationError):
        TimeRange(start=_utc(1), end=_utc(1))

    with pytest.raises(ValidationError):
        TimeRange(start=_utc(2), end=_utc(1))


def test_basic_identifier_validation() -> None:
    with pytest.raises(ValidationError):
        NvrInfo(model="")

    with pytest.raises(ValidationError):
        DeviceInfo(device_id="", name="Camera")

    with pytest.raises(ValidationError):
        ChannelInfo(channel_id=0)

from vigi import (
    AuthMode,
    CapabilityName,
    ChannelStatus,
    DeviceType,
    RecordType,
    StreamType,
)


def test_enum_values_are_importable() -> None:
    assert AuthMode.DIGEST.value == "digest"
    assert AuthMode.BEARER.value == "bearer"
    assert CapabilityName.AUTH_TOKEN.value == "auth.token"
    assert DeviceType.UNKNOWN.value == "unknown"
    assert ChannelStatus.ONLINE.value == "online"
    assert RecordType.UNKNOWN.value == "unknown"
    assert StreamType.MAIN.value == "1"
    assert StreamType.MINOR.value == "2"

import pytest

from vigi.auth import AuthConfig
from vigi.client import VigiClient
from vigi.exceptions import CapabilityError, ValidationError
from vigi.stream import StreamService
from vigi.types import CapabilityName, StreamType
from vigi.models import RtspStreamInfo


def test_build_replay_url_uses_documented_format() -> None:
    url = StreamService().build_replay_url(
        host="192.168.0.7",
        channel_id=1,
        start_time="20260710t000000z",
        end_time="20260710t001000z",
    )

    assert url == (
        "rtsp://192.168.0.7/replay/1/1/avm?starttime=20260710t000000z&endtime=20260710t001000z"
    )


@pytest.mark.parametrize(
    ("stream", "expected_stream"),
    [
        (StreamType.MAIN, "1"),
        (StreamType.MINOR, "2"),
    ],
)
def test_build_live_url_uses_documented_format(stream: StreamType, expected_stream: str) -> None:
    url = StreamService().build_live_url(
        host="nvr.example.invalid",
        channel_id=3,
        stream=stream,
    )

    assert url == f"rtsp://nvr.example.invalid/live/3/{expected_stream}/avm"


@pytest.mark.parametrize("channel_id", [0, -1, "1", True])
def test_build_live_url_rejects_invalid_channel(channel_id: object) -> None:
    with pytest.raises(ValidationError, match="channel_id"):
        StreamService().build_live_url("nvr.local", channel_id)


@pytest.mark.parametrize("stream", ["1", 1, True])
def test_build_live_url_rejects_unsupported_stream_selector(stream: object) -> None:
    with pytest.raises(ValidationError, match="stream"):
        StreamService().build_live_url("nvr.local", 1, stream)


@pytest.mark.parametrize(
    "host",
    [
        "",
        "rtsp://nvr.local",
        "nvr.local/path",
        "admin:password@nvr.local",
        "nvr.local:554",
    ],
)
def test_build_live_url_rejects_host_components(host: str) -> None:
    with pytest.raises(ValidationError):
        StreamService().build_live_url(host, 1)


def test_build_live_url_is_capability_gated_without_network() -> None:
    with pytest.raises(CapabilityError, match="RTSP live"):
        StreamService({CapabilityName.STREAM_REPLAY_RTSP}).build_live_url("nvr.local", 1)


def test_build_live_url_is_enabled_by_default_and_by_client() -> None:
    direct_url = StreamService().build_live_url("nvr.local", 1)
    client_url = VigiClient(
        AuthConfig(
            host="nvr.local",
            port=20443,
            username="admin",
            password="password",
        )
    ).stream.build_live_url("nvr.local", 1)

    assert direct_url == "rtsp://nvr.local/live/1/1/avm"
    assert client_url == direct_url


def test_build_live_url_and_errors_do_not_echo_suspicious_host_content() -> None:
    suspicious_host = "admin:password@nvr.local"
    with pytest.raises(ValidationError) as exc_info:
        StreamService().build_live_url(suspicious_host, 1)

    assert "password" not in str(exc_info.value)
    url = StreamService().build_live_url("nvr.local", 1)
    assert "password" not in url
    assert "token" not in url
    assert "stok" not in url


def test_build_replay_url_allows_hostname() -> None:
    assert (
        StreamService()
        .build_replay_url(
            host="smaniac.iptime.org",
            channel_id=3,
            start_time="20260710t120000z",
            end_time="20260710t121000z",
        )
        .startswith("rtsp://smaniac.iptime.org/replay/3/1/avm?")
    )


@pytest.mark.parametrize("channel_id", [0, -1, "1", True])
def test_build_replay_url_rejects_invalid_channel(channel_id: object) -> None:
    with pytest.raises(ValidationError, match="channel_id"):
        StreamService().build_replay_url(
            "nvr.local", channel_id, "20260710t000000z", "20260710t001000z"
        )


@pytest.mark.parametrize("stream", [0, 2, -1, "1", True])
def test_build_replay_url_rejects_non_main_replay_stream(stream: object) -> None:
    with pytest.raises(ValidationError, match="Replay stream"):
        StreamService().build_replay_url(
            "nvr.local", 1, "20260710t000000z", "20260710t001000z", stream
        )


@pytest.mark.parametrize(
    "start_time",
    [
        "2026-07-10T00:00:00Z",
        "20260710T000000Z",
        "20260710t000000",
        "20260710000000z",
        "20260230t000000z",
    ],
)
def test_build_replay_url_rejects_invalid_start_time(start_time: str) -> None:
    with pytest.raises(ValidationError, match="start_time"):
        StreamService().build_replay_url("nvr.local", 1, start_time, "20260710t001000z")


@pytest.mark.parametrize(
    ("start_time", "end_time"),
    [
        ("20260710t000000z", "20260710t000000z"),
        ("20260710t001000z", "20260710t000000z"),
    ],
)
def test_build_replay_url_requires_increasing_time_range(start_time: str, end_time: str) -> None:
    with pytest.raises(ValidationError, match="start_time must be before"):
        StreamService().build_replay_url("nvr.local", 1, start_time, end_time)


@pytest.mark.parametrize(
    "host",
    [
        "",
        "rtsp://nvr.local",
        "http://nvr.local",
        "nvr.local/path",
        "admin:password@nvr.local",
        "nvr.local:554",
    ],
)
def test_build_replay_url_rejects_host_components(host: str) -> None:
    with pytest.raises(ValidationError):
        StreamService().build_replay_url(host, 1, "20260710t000000z", "20260710t001000z")


def test_build_replay_url_is_capability_gated_without_network() -> None:
    with pytest.raises(CapabilityError, match="RTSP replay"):
        StreamService(capabilities=set()).build_replay_url(
            "nvr.local", 1, "20260710t000000z", "20260710t001000z"
        )


def test_build_replay_url_and_errors_do_not_echo_suspicious_host_content() -> None:
    suspicious_host = "admin:password@nvr.local"
    with pytest.raises(ValidationError) as exc_info:
        StreamService().build_replay_url(suspicious_host, 1, "20260710t000000z", "20260710t001000z")

    assert "password" not in str(exc_info.value)
    url = StreamService({CapabilityName.STREAM_REPLAY_RTSP}).build_replay_url(
        "nvr.local", 1, "20260710t000000z", "20260710t001000z"
    )
    assert "password" not in url
    assert "token" not in url
    assert "stok" not in url


def test_open_replay_remains_unsupported_without_network() -> None:
    with pytest.raises(NotImplementedError, match="not supported"):
        StreamService().open_replay(RtspStreamInfo(channel_id=1, stream_type=StreamType.MAIN))

import os

import pytest

from vigi import AuthConfig, VigiClient


def _integration_config_available() -> bool:
    required = (
        "VIGI_HOST",
        "VIGI_USERNAME",
        "VIGI_PASSWORD",
        "VIGI_RECORDING_CHANNEL_ID",
        "VIGI_RECORDING_START_MONTH",
        "VIGI_RECORDING_END_MONTH",
        "VIGI_RECORDING_DAY",
    )
    return all(os.getenv(name) for name in required)


@pytest.mark.skipif(
    not _integration_config_available(),
    reason="VIGI recording integration environment is not configured.",
)
def test_integration_recording_search_endpoints() -> None:
    verify_ssl = os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}
    port = int(os.getenv("VIGI_PORT", "20443"))
    channel_id = int(os.environ["VIGI_RECORDING_CHANNEL_ID"])
    start_month = os.environ["VIGI_RECORDING_START_MONTH"]
    end_month = os.environ["VIGI_RECORDING_END_MONTH"]
    configured_day = os.environ["VIGI_RECORDING_DAY"]
    start_index = int(os.getenv("VIGI_RECORDING_START_INDEX", "0"))
    end_index = int(os.getenv("VIGI_RECORDING_END_INDEX", "99"))

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
    days = client.records.list_days(channel_id, start_month, end_month)
    process = client.records.get_free_process()
    day = days.days[0].day if days.days else configured_day
    results = client.records.list_results(
        channel_id,
        process.process_id,
        day,
        start_index,
        end_index,
    )

    assert isinstance(days.days, tuple)
    assert days.error_code == 0
    for record_day in days.days:
        assert isinstance(record_day.day, str)
        assert len(record_day.day) == 8
        assert record_day.day.isdigit()

    assert isinstance(process.process_id, int)
    assert process.process_id > 0
    assert process.error_code == 0

    assert isinstance(results.results, tuple)
    assert results.error_code == 0
    for segment in results.results:
        assert isinstance(segment.start_time, str)
        assert isinstance(segment.end_time, str)

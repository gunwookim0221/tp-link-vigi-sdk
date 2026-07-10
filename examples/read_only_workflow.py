"""Run the documented read-only NVR workflow after explicit execution."""

import os

from vigi import AuthConfig, VigiClient, VigiError


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def _verify_tls() -> bool:
    return os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}


def main() -> None:
    """Authenticate, search recording metadata, and build a replay URL."""

    client = VigiClient(
        AuthConfig(
            host=_required_env("VIGI_HOST"),
            port=int(os.getenv("VIGI_PORT", "20443")),
            username=_required_env("VIGI_USERNAME"),
            password=_required_env("VIGI_PASSWORD"),
            verify_tls=_verify_tls(),
        )
    )
    try:
        client.login()
        devices = client.devices.list_added_devices()
        if not devices.devices:
            print("No NVR-managed devices were returned.")
            return

        channel_id = int(os.getenv("VIGI_RECORDING_CHANNEL_ID", devices.devices[0].channel_id))
        days = client.records.list_days(
            channel_id,
            _required_env("VIGI_RECORDING_START_MONTH"),
            _required_env("VIGI_RECORDING_END_MONTH"),
        )
        if not days.days:
            print("No recording days were returned for the selected range.")
            return

        process = client.records.get_free_process()
        day = os.getenv("VIGI_RECORDING_DAY", days.days[0].day)
        results = client.records.list_results(channel_id, process.process_id, day)
        if not results.results:
            print("No recording segments were returned for the selected day.")
            return

        replay_url = client.stream.build_replay_url(
            host=_required_env("VIGI_HOST"),
            channel_id=channel_id,
            start_time=_required_env("VIGI_REPLAY_START_TIME"),
            end_time=_required_env("VIGI_REPLAY_END_TIME"),
        )
    except (VigiError, ValueError) as error:
        print(f"Read-only workflow failed: {error}")
        return

    print(f"Found {len(results.results)} recording segment(s).")
    print(f"Replay URL (not opened): {replay_url}")


if __name__ == "__main__":
    main()

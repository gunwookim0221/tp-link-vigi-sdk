"""Build a documented replay URL without logging in or opening RTSP."""

import os

from vigi import StreamService, VigiError


def main() -> None:
    """Print a replay URL using environment values or safe placeholders."""

    host = os.getenv("VIGI_HOST", "nvr.example.invalid")
    channel_id = int(os.getenv("VIGI_RECORDING_CHANNEL_ID", "1"))
    start_time = os.getenv("VIGI_REPLAY_START_TIME", "20260710t000000z")
    end_time = os.getenv("VIGI_REPLAY_END_TIME", "20260710t001000z")
    try:
        replay_url = StreamService().build_replay_url(
            host=host,
            channel_id=channel_id,
            start_time=start_time,
            end_time=end_time,
        )
    except (VigiError, ValueError) as error:
        print(f"Replay URL could not be built: {error}")
        return

    print(f"Replay URL (not opened): {replay_url}")


if __name__ == "__main__":
    main()

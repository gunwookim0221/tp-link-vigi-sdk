# Usage Guide

## Scope

This guide covers the current documented, read-only NVR SDK workflow:
authentication, device inventory, recording searches, and RTSP replay URL
generation. It does not describe undocumented device behavior.

## Installation

Python 3.10 or later is required. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Configure the shell

Copy `.env.example` for local reference if useful, but do not commit `.env`.
Neither the SDK, the examples, nor the tests automatically load `.env`; export
values in the shell, configure the test runner, or use CI secret configuration.

```powershell
$env:VIGI_HOST = "nvr.example.invalid"
$env:VIGI_PORT = "20443"
$env:VIGI_USERNAME = "admin"
$env:VIGI_PASSWORD = "<your-nvr-password>"
$env:VIGI_VERIFY_SSL = "true"
```

For a POSIX shell, use `export VIGI_HOST=...` and the equivalent assignments
for the remaining variables. Keep credentials and any issued tokens out of
source files, logs, shell history, and commits.

## Authenticate with an NVR

```python
import os

from vigi import AuthConfig, VigiClient


def create_client() -> VigiClient:
    return VigiClient(
        AuthConfig(
            host=os.environ["VIGI_HOST"],
            port=int(os.getenv("VIGI_PORT", "20443")),
            username=os.environ["VIGI_USERNAME"],
            password=os.environ["VIGI_PASSWORD"],
            verify_tls=os.getenv("VIGI_VERIFY_SSL", "true").lower()
            not in {"0", "false", "no"},
        )
    )


client = create_client()
client.login()
```

Client construction is local. `client.login()` is the first operation above
that contacts the NVR.

## List NVR-managed devices and choose a channel

```python
devices = client.devices.list_added_devices()
if not devices.devices:
    print("No NVR-managed devices were returned.")
else:
    for device in devices.devices:
        print(device.channel_id, device.name, device.alias, device.online.value)
```

Use a returned `channel_id` as the `channel_id` argument for recording calls.
An empty device list is a valid response and is not an error by itself.

## Search recording metadata

Set the month range and, if necessary, a specific day:

```powershell
$env:VIGI_RECORDING_CHANNEL_ID = "1"
$env:VIGI_RECORDING_START_MONTH = "202607"
$env:VIGI_RECORDING_END_MONTH = "202607"
$env:VIGI_RECORDING_DAY = "20260710"
```

Call the documented read-only endpoints in this order:

```python
import os

channel_id = int(os.environ["VIGI_RECORDING_CHANNEL_ID"])
days = client.records.list_days(
    channel_id,
    os.environ["VIGI_RECORDING_START_MONTH"],
    os.environ["VIGI_RECORDING_END_MONTH"],
)
if not days.days:
    print("No recording days were returned for the selected range.")
else:
    process = client.records.get_free_process()
    day = os.getenv("VIGI_RECORDING_DAY", days.days[0].day)
    results = client.records.list_results(channel_id, process.process_id, day)
    if not results.results:
        print("No recording segments were returned for the selected day.")
```

An empty recording-day or result list is valid. `RecordSegment.start_time` and
`end_time` remain raw strings from the documented response; the SDK does not
convert them into replay timestamps.

## Build an RTSP replay URL

The helper requires explicit UTC values in `YYYYMMDDtHHMMSSz` format. Provide
them separately instead of converting a returned record segment automatically:

```powershell
$env:VIGI_REPLAY_START_TIME = "20260710t000000z"
$env:VIGI_REPLAY_END_TIME = "20260710t001000z"
```

```python
replay_url = client.stream.build_replay_url(
    host=os.environ["VIGI_HOST"],
    channel_id=channel_id,
    start_time=os.environ["VIGI_REPLAY_START_TIME"],
    end_time=os.environ["VIGI_REPLAY_END_TIME"],
)
print(replay_url)
```

This creates a documented URL only. It does not open RTSP, authenticate to an
RTSP server, receive video, download or export recordings, or save a file.

## Minimal error handling

Catch the common SDK base exception at an application boundary without logging
credentials or session material:

```python
from vigi import VigiError

try:
    client.login()
    devices = client.devices.list_added_devices()
except VigiError as error:
    print(f"VIGI request failed: {error}")
else:
    print(f"Retrieved {len(devices.devices)} device entries.")
```

## Integration tests

Integration tests contact real devices only when the required environment
variables are explicitly set. For example:

```powershell
python -m pytest tests/test_integration_auth.py -v
python -m pytest tests/test_integration_devices.py -v
python -m pytest tests/test_integration_records.py -v
```

The default test command remains hardware-free when no integration variables
are configured:

```powershell
python -m pytest
```

## Unsupported features

Snapshot is unsupported under the current official NVR and IPC documentation.
Export/download, RTSP open and playback, video saving, ffmpeg, image
processing, and CLI support are also outside the current SDK scope.

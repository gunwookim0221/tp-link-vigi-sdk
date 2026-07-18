# TP-Link VIGI SDK

Python SDK for the documented, read-only portions of the
TP-Link VIGI NVR OpenAPI.

## Requirements and Installation

- Python 3.10 or later.

Install the project in an isolated environment from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Quickstart

Set the NVR connection variables in your shell. `.env` is not loaded
automatically by the SDK, tests, or examples.

```powershell
$env:VIGI_HOST = "nvr.example.invalid"
$env:VIGI_PORT = "20443"
$env:VIGI_USERNAME = "admin"
$env:VIGI_PASSWORD = "<your-nvr-password>"
$env:VIGI_VERIFY_SSL = "true"
```

Then authenticate and list NVR-managed devices:

```python
import os

from vigi import AuthConfig, VigiClient

client = VigiClient(
    AuthConfig(
        host=os.environ["VIGI_HOST"],
        port=int(os.getenv("VIGI_PORT", "20443")),
        username=os.environ["VIGI_USERNAME"],
        password=os.environ["VIGI_PASSWORD"],
        verify_tls=os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"},
    )
)
client.login()
devices = client.devices.list_added_devices()
for device in devices.devices:
    print(device.channel_id, device.name, device.alias, device.online.value)
```

`client.login()` and service calls contact the configured NVR. Constructing a
client or importing `vigi` does not make a network request.

## Read-only workflows and examples

The detailed [usage guide](docs/12-usage-guide.md) covers authentication,
device inventory, recording-day and recording-result searches, explicit error
handling, and RTSP live and replay URL construction.

- [List devices](examples/list_devices.py)
- [Read-only recording workflow](examples/read_only_workflow.py)
- [Build a replay URL without logging in](examples/build_replay_url.py)

Examples read environment variables only when their `main()` function runs.
They do not load `.env`, print passwords or tokens, save files, or open RTSP
connections.

## Supported scope

Implemented read-only SDK support includes:

- Documented NVR authentication.
- NVR-managed device inventory with `client.devices.list_added_devices()`.
- Recording-day, free-search-process, and recording-result queries.
- `client.stream.build_live_url(...)` for documented RTSP live URLs.
- `client.stream.build_ipc_live_url(...)` for documented standalone-camera RTSP live URLs.
- `client.stream.build_replay_url(...)` for documented RTSP replay URLs.

The RTSP helpers only build URLs. They do not open RTSP, perform a Digest
handshake, download video, or save video files. Live URLs support main stream
`1` and minor stream `2`; replay requires stream `1` and explicit UTC
`YYYYMMDDtHHMMSSz` times. HTTPS OpenAPI Bearer authentication is separate from
RTSP Digest authentication and is not included in generated URLs.

Unsupported or deferred:

- Snapshot: unsupported because the current official NVR and IPC OpenAPI
  documents do not define a snapshot or capture API.
- Export/download, RTSP playback, video saving, ffmpeg, and image processing.
- CLI: deferred to a separate phase.
- Standalone IPC OpenAPI control APIs.

## Tests

Run the default unit and smoke-test suite:

```powershell
python -m pytest
```

Real-device integration tests are opt-in. Export the required `VIGI_*`
variables in the shell, then run the relevant test explicitly, for example:

```powershell
python -m pytest tests/test_integration_records.py -v
```

See [docs/05-test-strategy.md](docs/05-test-strategy.md) and
[.env.example](.env.example) for the supported local configuration variables.

## Documentation

Start with:

- [Documentation index](docs/00-index.md)
- [API scope](docs/03-api-scope.md)
- [Usage guide](docs/12-usage-guide.md)
- [Implementation checklist](docs/08-implementation-checklist.md)
- [Limitations](docs/10-limitations.md)
- [Roadmap](docs/11-roadmap.md)

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by TP-Link.
TP-Link and VIGI are trademarks of their respective owners. Use this SDK only
with devices and credentials you are authorized to access.

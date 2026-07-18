# Test Strategy

## Goals

- Prove SDK behavior without requiring hardware for every test.
- Keep real-device tests explicit, configurable, and isolated.
- Prevent regressions when TP-Link updates OpenAPI documentation or firmware behavior changes.

## Unit Tests

Unit tests should cover:

- URL/path construction.
- Query parameter encoding.
- Digest response calculation.
- Bearer token header insertion.
- Token refresh decision logic.
- Response model parsing.
- Error mapping from HTTP status and OpenAPI `error_code`.

## Mock Tests

Mock tests should simulate:

- Initial `GET /openapi/token` no-auth challenge.
- Digest-authenticated token response.
- Percent-encoded token values from the device.
- Token refresh response.
- `GET /openapi/added_devices` success and empty responses.
- Documented `error_code` responses.
- Timeout, TLS, and connection failures.

Device inventory mock and unit tests should cover:

- Bearer-authenticated `GET /openapi/added_devices` request construction.
- Official response parsing for `devices` and `error_code`.
- Mapping official `id` to SDK `channel_id`.
- Mapping official `online` values `"0"` and `"1"`.
- Empty `devices` responses.
- Invalid JSON, non-object top-level JSON, missing required fields, invalid field types, invalid `online` values, and non-zero `error_code`.
- Authentication guard behavior before any network call when no Bearer token is available.
- Secret redaction so Bearer tokens, passwords, nonce values, and Digest responses are not emitted in assertion messages or errors.

Recording search mock and unit tests should cover:

- Bearer-authenticated `GET /openapi/record/days` request construction with `channel`, `start`, and `end` query parameters.
- Bearer-authenticated `GET /openapi/record/search/free_process` request construction.
- Bearer-authenticated `GET /openapi/record/search/results` request construction with `channel`, `process`, `day`, `start_index`, and `end_index` query parameters.
- Official response parsing for `days`, `process`, `results`, and `error_code`.
- Empty `days` and empty `results` responses.
- Invalid JSON, non-object top-level JSON, missing required fields, invalid field types, invalid day/month formats, invalid index ranges, non-zero `error_code`, and HTTP non-2xx responses.
- Authentication guard behavior before any network call when no Bearer token is available.
- Secret redaction so Bearer tokens, passwords, nonce values, and Digest responses are not emitted in assertion messages or errors.

Phase 8 RTSP URL helper tests are unit tests only and should cover:

- Documented live URL construction for main and minor stream selectors.
- Documented RTSP replay URL construction and `starttime`, `endtime` query order.
- Host, positive channel, supported live stream selectors, replay stream `1`, UTC time format, and increasing-time-range validation.
- Capability-gated failure before any network operation.
- Redaction of suspicious host content from validation errors and generated URLs.
- Explicitly unsupported `open_replay()` behavior without attempting an RTSP connection.

Phase 8 does not add RTSP-open integration tests, RTSP Digest handshake tests,
video-byte receipt, or video file tests. Real-device RTSP playback is an
opt-in external-client validation and is not exercised by the default suite.

## Phase 10B Examples Smoke Tests

Examples are syntax-compiled and imported by smoke tests. Imports must not
perform login, device requests, recording searches, RTSP connections, or any
other network operation. Each executable example keeps invocation in `main()`
behind an `if __name__ == "__main__":` guard.

The smoke tests do not use real-device configuration and do not execute
example `main()` functions. They verify import safety only; explicit execution
of the read-only examples remains an opt-in real-device action.

## Continuous Integration

GitHub Actions runs Ruff, mypy, the default pytest suite, and the examples
compile smoke test on Python 3.10, 3.11, 3.12, and 3.13. The workflow supplies
no `VIGI_*` configuration, so opt-in real-device integration tests remain
skipped and no NVR or IPC device is contacted.

## Phase 9 Snapshot Review

No snapshot mock, unit, or integration tests are added because the current official NVR and IPC OpenAPI documents do not define a snapshot or capture API.

If TP-Link publishes an official snapshot API, tests must be mock-first and cover the documented method, path or method name, authentication, request schema, and response schema. Image bytes, content type, and file-saving behavior must be tested only when the official response type defines them. Any opt-in integration test must validate in memory only; file saving remains outside SDK core scope.

## Integration Tests

Integration tests require a real VIGI device. NVR-specific tests require a real VIGI NVR; Phase 5 camera verification requires a real C340I with hardware version, firmware version, and test date recorded.

Required configuration should be provided through environment variables or a local ignored config file:

```text
VIGI_HOST
VIGI_PORT
VIGI_USERNAME
VIGI_PASSWORD
VIGI_VERIFY_SSL
VIGI_DEVICE_MODEL
VIGI_FIRMWARE_VERSION
VIGI_RECORDING_CHANNEL_ID
VIGI_RECORDING_START_MONTH
VIGI_RECORDING_END_MONTH
VIGI_RECORDING_DAY
VIGI_RECORDING_START_INDEX
VIGI_RECORDING_END_INDEX
VIGI_REPLAY_START_TIME
VIGI_REPLAY_END_TIME
```

Standalone IPC verification must use a separate environment variable namespace:

```text
VIGI_IPC_HOST
VIGI_IPC_PORT
VIGI_IPC_USERNAME
VIGI_IPC_PASSWORD
VIGI_IPC_VERIFY_TLS
```

`.env.example` documents local placeholder values for these variables, but the
test suite does not auto-load `.env`. Local runs should export variables through
the shell, test runner, or CI secret configuration before invoking pytest.

Example PowerShell IPC verification setup:

```powershell
$env:VIGI_IPC_HOST = "camera.example.invalid"
$env:VIGI_IPC_PORT = "20443"
$env:VIGI_IPC_USERNAME = "admin"
$env:VIGI_IPC_PASSWORD = "<local-camera-password>"
$env:VIGI_IPC_VERIFY_TLS = "false"
python -m pytest tests/test_integration_ipc_auth.py -v
```

Integration tests must:

- Never run by default in normal `pytest`.
- Require an explicit marker such as `pytest -m integration`.
- Avoid mutating NVR settings unless the marker is more specific, such as `device_mutating`.
- Redact credentials and tokens from logs.
- Keep NVR device inventory tests read-only, opt-in, and avoid fixed assertions about the actual number of connected cameras.
- Keep NVR recording search tests read-only, opt-in, and avoid fixed assertions about the actual number of recording segments.
- Allow recording search integration tests to pass with empty recording results when the API is reachable and the response schema is valid.
- Keep IPC real-device tests opt-in, skipped by default, and limited to documented read-only verification such as `doAuth` plus internal `getStreamPort`.

## Device Tests

Device tests should record:

- Model.
- Hardware version.
- Firmware version.
- OpenAPI document version used for expectation.
- Endpoint result.
- Known issue references.

The first device target is `VIGI NVR1008H-8P`.

The Phase 5 shared-layer verification target is `VIGI C340I`. Camera verification must remain opt-in, skipped by default, and separate from NVR-specific integration tests. RTSP/ONVIF verification must be treated separately from HTTPS OpenAPI control API verification.

## Regression Tests

Regression tests should be added for:

- Every fixed authentication failure.
- Every parsing mismatch found against real NVR responses.
- Every documented endpoint added to the SDK.
- Every capability-gating bug.

## Test Markers

Proposed markers:

| Marker | Meaning |
| --- | --- |
| `unit` | No network or hardware. |
| `mock` | Uses mocked HTTP/RTSP behavior. |
| `integration` | Requires a real NVR. |
| `device_readonly` | Real device, read-only operation. |
| `device_mutating` | Real device, changes device state. |
| `rtsp` | Exercises stream URL or RTSP behavior. |

## Related Documents

- [03-api-scope.md](03-api-scope.md)
- [04-architecture.md](04-architecture.md)
- [06-device-matrix.md](06-device-matrix.md)
- [07-codex-instructions.md](07-codex-instructions.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)

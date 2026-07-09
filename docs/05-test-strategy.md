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

## Integration Tests

Integration tests require a real VIGI device. NVR-specific tests require a real VIGI NVR; Phase 5 camera verification requires a real C340I with hardware version, firmware version, and test date recorded.

Required configuration should be provided through environment variables or a local ignored config file:

```text
VIGI_HOST
VIGI_OPENAPI_PORT
VIGI_USERNAME
VIGI_PASSWORD
VIGI_VERIFY_TLS
VIGI_DEVICE_MODEL
VIGI_FIRMWARE_VERSION
```

Standalone IPC verification must use a separate environment variable namespace:

```text
VIGI_IPC_HOST
VIGI_IPC_PORT
VIGI_IPC_USERNAME
VIGI_IPC_PASSWORD
VIGI_IPC_VERIFY_TLS
```

Integration tests must:

- Never run by default in normal `pytest`.
- Require an explicit marker such as `pytest -m integration`.
- Avoid mutating NVR settings unless the marker is more specific, such as `device_mutating`.
- Redact credentials and tokens from logs.
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

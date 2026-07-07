# Architecture

## Architecture Goals

- Keep TP-Link OpenAPI facts separate from SDK implementation choices.
- Support `VIGI NVR1008H-8P` first without blocking other VIGI NVR models.
- Make every network behavior mockable.
- Keep the CLI, integration harness, and AI pipeline as consumers of the SDK.

## Current MVP Architecture

The current MVP is NVR-first.

- `VigiClient` targets the VIGI NVR OpenAPI first.
- Connected VIGI cameras are represented through NVR-managed channels and device records.
- The current target path is VIGI NVR OpenAPI plus NVR-managed channels/cameras.
- Standalone VIGI Camera OpenAPI behavior is not verified by this project yet.
- No standalone camera public client is part of the current SDK architecture.

## Proposed Package Structure

```text
src/vigi/
  __init__.py
  client.py
  auth.py
  transport.py
  capabilities.py
  exceptions.py
  models/
    auth.py
    device.py
    recording.py
    stream.py
  api/
    devices.py
    recordings.py
    streams.py
```

This structure is proposed for Phase 1. It is not implemented in Phase 0.

## Layers

| Layer | Responsibility |
| --- | --- |
| Transport | HTTPS requests, TLS options, timeout policy, request/response logging hooks. |
| Auth | Digest token acquisition, Bearer token injection, token refresh. |
| API Modules | Endpoint-specific request building and response parsing. |
| Client Facade | Stable user-facing SDK entry point. |
| Models | Typed request/response structures. |
| Capabilities | Model/firmware support declarations and runtime feature gating. |

## Capability-Based Design

Capabilities should answer:

- Is this endpoint documented for the target device class?
- Has this endpoint been verified on this model and firmware?
- Is this operation read-only or mutating?
- Does this operation require RTSP instead of HTTPS OpenAPI?

Example capability names:

- `auth.token`
- `device.added_devices`
- `recording.search`
- `stream.live_rtsp`
- `stream.replay_rtsp`
- `snapshot.todo`

## Future Camera Architecture

Standalone VIGI Camera support is a future expansion candidate only. It must not be exposed as public SDK support until a physical standalone VIGI camera is available and integration testing records model, hardware version, firmware version, and test date.

Candidate future public split:

- `VigiNvrClient` for NVR OpenAPI workflows.
- `VigiCameraClient` for direct standalone camera workflows.

Candidate shared common layer:

- Transport.
- Authentication.
- Models.
- Exceptions.
- Capabilities.

Rules for adding standalone camera support:

- Do not infer direct camera endpoints from NVR behavior.
- Do not add direct camera login, snapshot, stream, or settings support without official public documentation and real-device verification.
- Add a new ADR before changing the public client architecture. Suggested title: `ADR-0006 Split NVR and Camera Clients`.

## Fact

- The official reference separates control protocol, event protocol, and stream protocol.
- The control protocol uses HTTPS and JSON payloads.
- Stream access is RTSP.
- Control requests require Bearer authentication after token acquisition.
- RTSP stream authentication is Digest authentication according to the official reference.

## Exception Design

Proposed exception hierarchy:

```text
VigiError
  VigiConnectionError
  VigiTimeoutError
  VigiAuthenticationError
  VigiAuthorizationError
  VigiApiError
  VigiCapabilityError
  VigiResponseError
```

`VigiApiError` should preserve:

- HTTP status code when available.
- TP-Link `error_code` when available.
- Endpoint method and path.
- Sanitized response context.

## Sync and Async Plan

Phase 1 should implement a synchronous SDK first.

Assumption:

- Async support will be added later through a parallel transport implementation or an internal transport protocol abstraction.
- Public data models should be shared between sync and async clients.

## Security Notes

- Never log raw passwords.
- Never log raw access tokens or refresh tokens.
- Treat NVR addresses and device metadata as potentially sensitive.
- Provide explicit TLS verification options; do not silently disable verification.

## Related Documents

- [01-project-plan.md](01-project-plan.md)
- [03-api-scope.md](03-api-scope.md)
- [05-test-strategy.md](05-test-strategy.md)
- [06-device-matrix.md](06-device-matrix.md)
- [docs/adr/README.md](adr/README.md)
- [ADR-0001 Capability-Based Architecture](adr/ADR-0001-capability-based-architecture.md)
- [ADR-0002 Authentication Strategy](adr/ADR-0002-authentication-strategy.md)

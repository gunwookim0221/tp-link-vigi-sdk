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
- `VIGI C340I` is used in Phase 5 for shared-layer verification based on official firmware release notes indicating OpenAPI support.
- C340I IPC `doAuth` and post-auth read-only `getStreamPort` behavior are manually verified, but not implemented in the SDK.
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

## Confirmed Auth Split

NVR OpenAPI and IPC OpenAPI use different documented authentication and request shapes.

| Device class | Auth flow | Post-auth control shape | SDK status |
| --- | --- | --- | --- |
| NVR | `GET /openapi/token` Digest challenge followed by Bearer token. | REST-style `/openapi/...` HTTPS requests with Bearer authorization. | Implemented for the NVR auth layer. |
| IPC standalone camera | `doAuth` HTTPS JSON challenge followed by `stok`. | HTTPS `POST https://device_addr:port/stok=<stok>` with JSON method payloads. | Manually verified on C340I; SDK implementation pending ADR-guided architecture work. |

The existing NVR `AuthService` must not be reused directly for IPC auth. Reusable pieces may include SHA-256 digest helpers, TLS configuration, redaction policy, low-level transport concepts, exceptions, and integration-test harness patterns.

[ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md) records this split before any IPC SDK implementation.

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

Standalone VIGI Camera support is a future expansion candidate only. `VigiClient` remains the only public client while C340I is used for shared-layer verification.

C340I OpenAPI support is officially indicated in TP-Link firmware release notes for `VIGI C340I(UN) V1.20` firmware `2.2.0 Build 250926`. Real-device camera observations must not create public camera APIs until official documentation, verification records, and an ADR justify the split.

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
- Follow [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md) before implementing IPC authentication or transport behavior.
- Add another ADR before changing the public client architecture, introducing an RTSP client dependency, adding a documented snapshot endpoint to the public API, or changing the NVR-first MVP scope.

## Fact

- The official NVR reference separates control protocol, event protocol, and stream protocol.
- NVR control requests require Bearer authentication after token acquisition.
- NVR stream access is RTSP.
- IPC control requests use HTTPS POST JSON method payloads with `stok` after `doAuth`.
- IPC stream access is RTSP-style `MULTITRANS` and stream data uses RTP over TCP according to the IPC document.

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
- [ADR-0006 Separate NVR And IPC Auth Transports](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md)

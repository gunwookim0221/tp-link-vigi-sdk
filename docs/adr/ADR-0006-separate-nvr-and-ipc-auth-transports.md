# ADR-0006: Separate NVR And IPC Auth Transports

## Status

Accepted

## Context

The project originally implemented the documented NVR authentication flow from the official NVR OpenAPI material:

- `GET /openapi/token`
- SHA-256 Digest challenge/response
- Bearer token for post-auth `/openapi/...` requests

Official `VIGI IPC OpenAPI Document_V1.1` documents a different standalone IPC control flow:

- `doAuth` Step 1 uses HTTPS POST JSON and returns a SHA-256 challenge.
- `doAuth` Step 2 posts `params.nonce` and `params.response`.
- Success returns a top-level `stok`.
- Post-auth IPC control requests use `POST https://device_addr:port/stok=<stok>` with JSON method payloads.

Manual C340I verification on `2026-07-10` confirmed:

- Device: `VIGI C340I`
- Hardware: `VIGI C340I 1.20`
- Firmware: `2.2.0 Build 250926 Rel.53599n`
- IPC `doAuth` Step 2 returned `errCode: 0` and a redacted `stok`.
- Post-auth official IPC `getStreamPort` returned `result.streamPort: "554"` and `errCode: 0`.

Secrets, tokens, nonce values, passwords, and digest responses must not be recorded.

## Decision

NVR OpenAPI authentication and IPC OpenAPI authentication must be modeled as separate protocol strategies.

The existing NVR `AuthService` must not be reused directly for IPC authentication because its endpoint shape, token state, and authorization model are NVR-specific.

Allowed shared pieces include:

- SHA-256 digest helper behavior.
- TLS configuration.
- Timeout policy.
- Redaction policy.
- Low-level HTTPS transport concepts.
- Exception and sanitized response handling.
- Integration-test harness patterns.

IPC SDK implementation remains pending. This ADR does not add SDK code, tests, public IPC APIs, `VigiCameraClient`, or `VigiNvrClient`.

## Alternatives

- Reuse NVR `AuthService` for IPC by changing endpoint paths: rejected because IPC uses `doAuth` plus `stok`, not `/openapi/token` plus Bearer.
- Treat IPC method names as REST endpoints: rejected because IPC control requests are JSON method payloads sent to the `stok` URL shape.
- Defer ADR until implementation starts: rejected because the auth split is already confirmed by official IPC documentation and real C340I probe results.

## Consequences

- Architecture documents must distinguish NVR Bearer auth from IPC `stok` auth.
- Future IPC implementation should introduce an IPC-specific auth/session strategy before adding camera APIs.
- Public camera SDK support still requires explicit scope, capability, and client architecture decisions.
- Tests for IPC behavior should be added only when IPC implementation work begins.
- Existing NVR authentication behavior remains valid for NVR scope and is not changed by this ADR.

## Related Documents

- [../02-references.md](../02-references.md)
- [../03-api-scope.md](../03-api-scope.md)
- [../04-architecture.md](../04-architecture.md)
- [../06-device-matrix.md](../06-device-matrix.md)
- [../08-implementation-checklist.md](../08-implementation-checklist.md)
- [../09-history.md](../09-history.md)
- [../10-limitations.md](../10-limitations.md)
- [ADR-0002 Authentication Strategy](ADR-0002-authentication-strategy.md)

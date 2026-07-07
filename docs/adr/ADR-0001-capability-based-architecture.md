# ADR-0001: Capability-Based Architecture

## Status

Accepted

## Context

The MVP targets `TP-Link VIGI NVR1008H-8P`, but the official TP-Link OpenAPI guide and supported-products page cover multiple VIGI NVR models and hardware versions.

The supported-products page says the compatible device list may be updated. Firmware support is also relevant because the OpenAPI guide states that firmware must support OpenAPI.

## Decision

Design the SDK around capabilities instead of hard-coding behavior by model name only.

Capabilities will represent documented and verified support for API groups such as authentication, device inventory, recording search, RTSP live stream, and RTSP replay.

## Alternatives Considered

- Model-only branching: rejected because it does not handle firmware differences cleanly.
- Endpoint-only implementation without capability checks: rejected because it makes unsupported or unverified behavior too easy to call.
- Full dynamic discovery: deferred because no official OpenAPI discovery endpoint has been identified in the public reference.

## Consequences

- Device and firmware validation can evolve without reshaping public SDK methods.
- Integration tests can update the device matrix with verified capabilities.
- Mutating operations can remain blocked unless explicitly capability-gated.
- Capability metadata must be maintained as official documents and device verification evolve.

## Related Documents

- [../01-project-plan.md](../01-project-plan.md)
- [../03-api-scope.md](../03-api-scope.md)
- [../04-architecture.md](../04-architecture.md)
- [../06-device-matrix.md](../06-device-matrix.md)
- [../10-limitations.md](../10-limitations.md)

# Roadmap

## Current State

Completed:

- Phase 0 Documentation Foundation.
- Phase 1 Project Skeleton.
- Phase 2 Core Models and Types.
- Phase 3 Transport and Authentication Foundation.
- Phase 4 OpenAPI Authentication Implementation.
- Phase 4.5 Project Quality and Developer Experience.

Next:

- IPC auth/transport architecture work according to [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md), if standalone IPC SDK support is planned.
- NVR Device Inventory after shared-layer verification.

## v0.1

Goal:

- Establish a documented, testable SDK foundation.

Scope:

- Project documentation and ADR foundation.
- Python package skeleton.
- Core models and types.
- Transport/session boundaries.
- OpenAPI authentication implementation.
- Project quality and developer experience files.

Exit criteria:

- Package imports.
- Authentication mock tests pass.
- Integration authentication scaffold is opt-in and skipped by default.
- README and contributor-facing project files exist.

## v0.2

Goal:

- Validate shared SDK layers against C340I before expanding NVR-specific APIs.

Scope:

- C340I hardware and firmware confirmation.
- `VIGI C340I(UN) V1.20 2.2.0 Build 250926` or later requirement tracking.
- Real-device authentication, transport, session, timeout, TLS, and redaction observations.
- IPC document investigation showing C340I standalone control auth uses `doAuth`, not the NVR `/openapi/token` flow.
- Manual IPC `doAuth` probe confirmation for port `20443`, with `stok` redacted.
- Manual post-auth read-only IPC `getStreamPort` probe confirmation.
- Opt-in real-device IPC integration test confirmation for `doAuth` plus internal `getStreamPort`.
- ADR-0006 documentation of NVR auth and IPC auth separation.
- Malformed/HTTP0.9-like response tracking for the incorrect NVR `GET /openapi/token` request on the IPC control port.
- Camera-specific integration configuration kept opt-in and skipped by default.
- RTSP/ONVIF verification tracked separately from HTTPS OpenAPI control APIs.

Exit criteria:

- C340I verification status is recorded in the device matrix.
- SDK implementation remains blocked until IPC auth/transport architecture work is planned and implemented according to ADR-0006.
- No camera-specific public SDK APIs are exposed.
- Default tests do not require hardware.

## v0.3

Goal:

- Add read-only NVR device inventory after shared-layer verification.

Scope:

- Real-device authentication validation for `VIGI NVR1008H-8P`.
- `GET /openapi/added_devices`.
- Device/channel response parsing.
- Capability gate for `device.added_devices`.
- Mock tests and opt-in device integration scaffold.

Exit criteria:

- Device inventory mock tests pass.
- Real-device verification status is recorded in the device matrix.
- Default tests do not require hardware.

## v0.4

Goal:

- Add recording search support.

Scope:

- `GET /openapi/record/days`.
- `GET /openapi/record/search/free_process`.
- `GET /openapi/record/search/results`.
- Recording models and pagination/index behavior.

Exit criteria:

- Recording mock tests pass.
- Integration tests remain opt-in.

## v0.5

Goal:

- Add replay planning and snapshot decision.

Scope:

- RTSP live/replay URL helpers.
- Replay UTC time formatting.
- Documented replay stream limitation handling.
- Snapshot support decision based only on official documentation.

Exit criteria:

- RTSP URL helper tests pass.
- Snapshot is documented as supported, unsupported, or TODO with official reference.

## v1.0

Goal:

- Stable public SDK API for documented core read-only workflows.

Scope:

- Stable typed public APIs.
- Real-device verification for `VIGI NVR1008H-8P`.
- Updated device matrix.
- Release README and release notes.
- Changelog and semantic version policy.

Exit criteria:

- Public API stability rules are documented.
- Integration tests have been run against the MVP device.
- Release package builds reproducibly.

## Optional Future Phase: Standalone Camera Support

Goal:

- Evaluate direct standalone VIGI Camera public SDK support after verification data is available.

Blocked by:

- C340I real-device verification records with model, hardware version, firmware version, and test date.
- Official IPC documentation review, reproducible IPC `doAuth` verification, and post-auth read-only control verification for direct camera behavior.
- IPC-specific transport/auth strategy implementation according to [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md).
- A new architecture ADR before public client changes if standalone support requires public `VigiCameraClient` or `VigiNvrClient` changes.

Candidate scope:

- Public client split evaluation: `VigiNvrClient` and `VigiCameraClient`.
- Shared common layer reuse: transport, authentication, models, exceptions, and capabilities.
- Direct camera login, snapshot, stream, and settings behavior only if officially documented and verified.

This phase is not part of the current MVP and does not imply current standalone camera support.

## Phase Order

1. Phase 5: C340I Camera Integration Verification. Status: IPC auth and post-auth read-only control integration verified; SDK implementation pending ADR-0006 architecture work.
2. Phase 6: NVR Device Inventory.
3. Phase 7: NVR Recording Search.
4. Phase 8: Replay / Export.
5. Phase 9: Snapshot Support Decision.
6. Phase 10: CLI.
7. Phase 11: Integration Test Harness Hardening.
8. Phase 12: Release.

## Long-Term Plan

- CLI as a thin layer over the SDK.
- More documented OpenAPI endpoint groups.
- Mutating operations only behind explicit capability checks.
- Expanded model and firmware verification matrix.
- Optional standalone VIGI Camera public SDK support after official documentation, physical device verification, and ADR approval.
- Event receiver support if officially documented behavior is sufficient.
- AI pipeline integration using structured SDK outputs.
- Automation platform features after SDK and CLI are stable.

## Related Documents

- [00-index.md](00-index.md)
- [01-project-plan.md](01-project-plan.md)
- [03-api-scope.md](03-api-scope.md)
- [06-device-matrix.md](06-device-matrix.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [10-limitations.md](10-limitations.md)
- [project-philosophy.md](project-philosophy.md)

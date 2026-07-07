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

- Real-device authentication validation for `VIGI NVR1008H-8P`.
- Device Inventory after authentication validation.

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

- Add read-only device inventory after authentication validation.

Scope:

- Real-device authentication validation.
- `GET /openapi/added_devices`.
- Device/channel response parsing.
- Capability gate for `device.added_devices`.
- Mock tests and opt-in device integration scaffold.

Exit criteria:

- Device inventory mock tests pass.
- Real-device verification status is recorded in the device matrix.
- Default tests do not require hardware.

## v0.3

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

## v0.4

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

## Long-Term Plan

- CLI as a thin layer over the SDK.
- More documented OpenAPI endpoint groups.
- Mutating operations only behind explicit capability checks.
- Expanded model and firmware verification matrix.
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

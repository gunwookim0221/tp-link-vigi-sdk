# Roadmap

## v0.1

Goal:

- First documented, testable SDK foundation.

Scope:

- Project skeleton.
- Authentication.
- `GET /openapi/added_devices`.
- Capability metadata.
- Unit and mock tests.

Exit criteria:

- Package imports.
- Authentication mock tests pass.
- Device list mock tests pass.
- MVP device integration plan is documented.

## v0.2

Goal:

- Add recording search support.

Scope:

- `GET /openapi/record/days`.
- `GET /openapi/record/search/free_process`.
- `GET /openapi/record/search/results`.
- Recording models.
- Integration test harness draft.

Exit criteria:

- Recording mock tests pass.
- Read-only integration tests can be run explicitly.

## v0.3

Goal:

- Add RTSP URL helpers and CLI foundation.

Scope:

- Live RTSP URL construction.
- Replay RTSP URL construction.
- RTSP authentication documentation.
- CLI commands for auth check, device list, and recording search.

Exit criteria:

- CLI uses SDK only.
- RTSP URL construction is tested.

## v1.0

Goal:

- Stable public SDK API for documented MVP and core read-only workflows.

Scope:

- Stable typed public APIs.
- Real-device verification for `VIGI NVR1008H-8P`.
- Device matrix update.
- README and release documentation.
- Changelog and semantic version policy.

Exit criteria:

- Public API stability rules are documented.
- Integration tests have been run against the MVP device.
- Release package builds reproducibly.

## Long-Term Plan

- Add more documented OpenAPI endpoint groups.
- Add mutating operations only behind explicit capability checks.
- Expand model and firmware verification matrix.
- Add event receiver support if officially documented behavior is sufficient.
- Add AI pipeline integration using structured SDK outputs.
- Build automation platform features after SDK and CLI are stable.

## Related Documents

- [00-index.md](00-index.md)
- [01-project-plan.md](01-project-plan.md)
- [03-api-scope.md](03-api-scope.md)
- [06-device-matrix.md](06-device-matrix.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [10-limitations.md](10-limitations.md)

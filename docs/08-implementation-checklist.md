# Implementation Checklist

## Phase 0: Documentation

### Goal

Create the project context documents that define scope, architecture, testing, limitations, and roadmap.

### Tasks

- [x] Create `docs/01-project-plan.md`.
- [x] Create `docs/02-references.md`.
- [x] Create `docs/03-api-scope.md`.
- [x] Create `docs/04-architecture.md`.
- [x] Create `docs/05-test-strategy.md`.
- [x] Create `docs/06-device-matrix.md`.
- [x] Create `docs/07-codex-instructions.md`.
- [x] Create `docs/08-implementation-checklist.md`.
- [x] Create `docs/09-history.md`.
- [x] Create `docs/10-limitations.md`.
- [x] Create `docs/11-roadmap.md`.
- [x] Create `docs/00-index.md`.
- [x] Rename initial documents so `00` is reserved for the documentation index.
- [x] Add `.gitattributes` and `.gitignore` for repository hygiene.
- [x] Create `docs/adr/README.md`.
- [x] Create initial ADR documents `ADR-0001` through `ADR-0005`.
- [x] Update Codex instructions to require reading the documentation index first.
- [x] Update history so ADRs own design decisions and history owns progress milestones.

### Exit Criteria

- All documents exist.
- Documentation index exists.
- ADR system exists.
- Official references are linked.
- API facts are separated from assumptions.
- No SDK code is created.
- `README.md` is not created.

## Phase 1: Project Skeleton

### Goal

Create a minimal Python package skeleton without implementing endpoint behavior beyond placeholders required for tests.

### Tasks

- Add `pyproject.toml`.
- Add `src/vigi/` package.
- Add `tests/` layout.
- Configure formatter, linter, and pytest.
- Add project metadata and license after license decision.

### Exit Criteria

- Package imports successfully.
- `pytest` runs.
- No network calls are required.

## Phase 2: Authentication

### Goal

Implement documented token acquisition and refresh.

### Tasks

- Implement no-auth token challenge request flow.
- Implement Digest response generation according to official documentation.
- Implement Bearer token storage and header injection.
- Implement refresh token request.
- Add mock tests for token flows.

### Exit Criteria

- Authentication tests pass with documented examples or structured fixtures.
- Tokens are redacted in logs.
- Authentication errors map to typed exceptions.

## Phase 3: Device

### Goal

Implement read-only channel/device inventory.

### Tasks

- Implement `GET /openapi/added_devices`.
- Define typed device/channel model.
- Add capability flag `device.added_devices`.
- Add mock and integration test plan.

### Exit Criteria

- Mock tests cover online/offline devices.
- Real-device test is documented but not required in default test run.

## Phase 4: Recording

### Goal

Implement documented recording search APIs.

### Tasks

- Implement `GET /openapi/record/days`.
- Implement `GET /openapi/record/search/free_process`.
- Implement `GET /openapi/record/search/results`.
- Model search result time ranges.

### Exit Criteria

- Search process reuse behavior is tested.
- Result pagination/index behavior is tested.

## Phase 5: Replay

### Goal

Support documented RTSP replay URL construction and integration planning.

### Tasks

- Build replay RTSP URL helper.
- Document UTC time conversion.
- Confirm replay stream limitation that replay only supports stream `1`.
- Add RTSP Digest authentication integration notes.

### Exit Criteria

- URL construction tests pass.
- No undocumented replay endpoint is introduced.

## Phase 6: Snapshot

### Goal

Determine whether snapshot is supported by official public documentation.

### Tasks

- Re-check official OpenAPI documentation for snapshot endpoints.
- If no endpoint exists, keep feature as unsupported.
- If TP-Link publishes official support, add endpoint scope and tests.

### Exit Criteria

- Snapshot status is documented as supported, unsupported, or TODO with official reference.

## Phase 7: CLI

### Goal

Provide a thin command-line interface over SDK features.

### Tasks

- Add CLI framework after dependency/license review.
- Add commands for auth check, device list, and recording search.
- Redact secrets in output.

### Exit Criteria

- CLI uses SDK APIs only.
- CLI tests use mocks.

## Phase 8: Integration Test

### Goal

Create a real-device test harness for supported NVRs.

### Tasks

- Add integration config loader.
- Add read-only device test.
- Add recording search test.
- Add device matrix update workflow.

### Exit Criteria

- Integration tests are opt-in.
- Test output records model, firmware, and OpenAPI document version.

## Phase 9: Release

### Goal

Publish the first usable package release.

### Tasks

- Finalize license.
- Add README.
- Add changelog.
- Add release workflow.
- Tag `v0.1.0`.

### Exit Criteria

- Package builds.
- Tests pass.
- Public API is documented.

## Related Documents

- [01-project-plan.md](01-project-plan.md)
- [03-api-scope.md](03-api-scope.md)
- [04-architecture.md](04-architecture.md)
- [05-test-strategy.md](05-test-strategy.md)
- [docs/adr/README.md](adr/README.md)
- [11-roadmap.md](11-roadmap.md)

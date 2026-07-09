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

- [x] Add `pyproject.toml`.
- [x] Add `src/vigi/` package.
- [x] Add `tests/` layout.
- [x] Configure pytest.
- [ ] Configure formatter and linter.
- [x] Add minimal project metadata.
- [ ] Add license after license decision.

### Exit Criteria

- Package imports successfully.
- `pytest` runs.
- No network calls are required.

## Phase 2: Core Models and Types

### Goal

Define the core data models, shared enum types, and minimal validation helpers used by later SDK phases.

### Tasks

- [x] Add core SDK data models.
- [x] Add shared enum types.
- [x] Add minimal validation for time ranges and identifiers.
- [x] Export public model and type symbols.
- [x] Add model and type tests.
- [ ] Implement no-auth token challenge request flow.
- [ ] Implement Digest response generation according to official documentation.
- [ ] Implement Bearer token storage and header injection.
- [ ] Implement refresh token request.
- [ ] Add mock tests for token flows.

### Exit Criteria

- Core models and shared types import successfully.
- Model validation tests pass.
- No network, authentication, device, recording, or RTSP behavior is implemented.

## Phase 3: Transport and Authentication Foundation

### Goal

Define transport and authentication boundaries without implementing OpenAPI calls, Digest authentication, token issuance, or real HTTP behavior.

### Tasks

- [x] Add transport boundary types.
- [x] Add session boundary types.
- [x] Add authentication provider boundary types.
- [x] Wire client to transport and authentication provider dependencies.
- [x] Add import and construction tests for transport/session/auth provider stubs.
- [ ] Implement actual HTTP transport.
- [ ] Implement actual Digest authentication.
- [ ] Implement actual token issuance or refresh.

### Exit Criteria

- Transport, session, and authentication provider structures import successfully.
- Client can be constructed with transport and auth provider placeholders.
- No network, login, token, device, recording, RTSP, or OpenAPI behavior is implemented.

## Phase 4: OpenAPI Authentication Implementation

### Goal

Implement the documented OpenAPI authentication flow only.

### Tasks

- [x] Implement token endpoint request creation.
- [x] Implement SHA-256 Digest response calculation.
- [x] Implement access token response parsing.
- [x] Store Bearer token state in session info.
- [x] Apply Bearer token through session authorization headers.
- [x] Add authentication, response parsing, and client login mock tests.
- [x] Add skipped integration authentication scaffold.
- [ ] Implement device APIs.
- [ ] Implement record search APIs.
- [ ] Implement RTSP replay.

### Exit Criteria

- Authentication unit and mock tests pass.
- Integration authentication test is skipped unless VIGI environment variables are configured.
- No device, recording, RTSP, snapshot, CLI, or undocumented endpoint behavior is implemented.

## Phase 4.5: Project Quality and Developer Experience

### Goal

Improve open-source project quality and contributor experience without adding SDK features.

### Tasks

- [x] Add Work In Progress README.
- [x] Add contributing guide.
- [x] Add changelog.
- [x] Add security policy.
- [x] Add code of conduct.
- [x] Add GitHub issue and pull request templates.
- [x] Add GitHub Actions CI.
- [x] Add project philosophy document.
- [x] Update documentation index and Codex instructions.
- [x] Align roadmap and checklist with actual development order.
- [x] Add optional development quality dependencies.

### Exit Criteria

- Default tests pass.
- CI runs package install, pytest, and compileall.
- No Device, Recording, Replay, Snapshot, CLI, or OpenAPI feature behavior is added.

## Phase 5: Camera Integration Verification

### Goal

Verify shared SDK layers against `VIGI C340I` before expanding NVR-specific APIs, without adding public camera SDK support.

### Tasks

- [ ] Confirm C340I hardware version.
- [ ] Confirm current C340I firmware version.
- [ ] Upgrade to `VIGI C340I(UN) V1.20 2.2.0 Build 250926` or later if applicable.
- [ ] Record test date, hardware version, firmware version, and network mode.
- [ ] Confirm whether C340I appears in the official VIGI OpenAPI supported product list.
- [x] Confirm whether standalone camera OpenAPI uses the same `/openapi/token` Digest flow as NVR OpenAPI.
- [ ] Confirm OpenAPI setting and port on the camera if exposed by firmware/UI.
- [x] Record real-device token challenge behavior.
- [x] Review `VIGI IPC OpenAPI Document_V1.1` for standalone IPC authentication and request format.
- [x] Confirm IPC control authentication uses `doAuth` and not the NVR `/openapi/token` endpoint.
- [x] Confirm IPC control port is obtained through ODP and defaults to `20443`.
- [x] Confirm IPC discovery uses ODP local service port `23001` and Ethernet protocol type `0x7210`.
- [x] Confirm IPC stream protocol is RTSP-style `MULTITRANS` with RTP over TCP and default stream port `554`.
- [x] Manually verify IPC `doAuth` challenge and `stok` response against the real camera.
- [x] Verify IPC SHA-256 `doAuth` response against the real camera.
- [x] Identify a low-risk official IPC post-auth read-only method for manual verification.
- [x] Manually verify official IPC `getStreamPort` after authentication using redacted `stok`.
- [x] Verify IPC `stok` usage against the real camera with an officially documented IPC control method.
- [x] Document IPC-specific auth/transport separation in [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md).
- [x] Add internal IPC auth/session/control request builders according to ADR-0006.
- [x] Keep IPC `getStreamPort` as an internal verification method, not a public SDK API.
- [x] Add mock/unit coverage for IPC `doAuth`, `stok` redaction, and internal `getStreamPort` request building.
- [x] Add opt-in skipped IPC integration scaffold using `VIGI_IPC_*` environment variables.
- [x] Run opt-in C340I IPC integration test and verify `doAuth` plus internal `getStreamPort` succeeds.
- [x] Harden internal IPC `doAuth` parsing with documented errCode constants and strict method, URI, HTTP method, and errCode validation.
- [x] Harden IPC redaction tests so password, nonce, digest response, and `stok` do not appear in repr or sanitized error messages.
- [x] Harden opt-in IPC integration verification to parse `getStreamPort` JSON and confirm method, `errCode: 0`, and `result.streamPort` presence.
- [x] Document that `.env.example` is a placeholder reference and `.env` is not auto-loaded by tests.
- [ ] Keep public camera SDK APIs blocked until a separate public API decision is made.
- [x] Add or confirm camera-specific integration environment variables before running real-device tests.
- [x] Keep all real-device integration tests skipped by default.
- [ ] Verify RTSP/ONVIF separately from HTTPS OpenAPI control APIs.
- [ ] Do not implement undocumented snapshot, device-info, or camera-control endpoints.
- [ ] Do not implement camera-specific endpoints from malformed or undocumented responses.
- [ ] Document camera-to-NVR shared-layer reuse points.
- [x] Treat IPC-specific transport/auth as an ADR candidate before any implementation.
- [ ] Decide whether ADR is needed before adding camera-specific public APIs.

### Exit Criteria

- C340I verification facts are recorded with model, hardware version, firmware version, and test date.
- Shared and non-shared authentication, transport, session, error-handling, and integration-test harness observations are documented.
- No camera-specific public SDK APIs are added.
- Device matrix is updated with verification status.

## Phase 6: NVR Device Inventory

### Goal

Implement read-only channel/device inventory after real-device authentication validation.

### Tasks

- [x] Validate authentication against `VIGI NVR1008H-8P`.
- [ ] Implement `GET /openapi/added_devices`.
- [ ] Parse documented device/channel fields.
- [ ] Add capability flag `device.added_devices`.
- [ ] Add mock tests.
- [ ] Add opt-in integration test scaffold.

### Exit Criteria

- Device inventory mock tests pass.
- Integration tests remain opt-in.
- Device matrix is updated with verification status.

## Phase 7: NVR Recording Search

### Goal

Implement documented recording search APIs.

### Tasks

- [ ] Implement `GET /openapi/record/days`.
- [ ] Implement `GET /openapi/record/search/free_process`.
- [ ] Implement `GET /openapi/record/search/results`.
- [ ] Model search process reuse.
- [ ] Add mock tests.

### Exit Criteria

- Search process reuse behavior is tested.
- Result pagination/index behavior is tested.
- Integration tests remain opt-in.

## Phase 8: Replay / Export

### Goal

Support documented RTSP replay URL construction and integration planning.

### Tasks

- [ ] Build replay RTSP URL helper.
- [ ] Document UTC time conversion.
- [ ] Confirm replay stream limitation that replay only supports stream `1`.
- [ ] Add RTSP Digest authentication integration notes.

### Exit Criteria

- URL construction tests pass.
- No undocumented replay endpoint is introduced.

## Phase 9: Snapshot Support Decision

### Goal

Determine whether snapshot is supported by official public documentation.

### Tasks

- [ ] Re-check official OpenAPI documentation for snapshot endpoints.
- [ ] If no endpoint exists, keep feature as unsupported.
- [ ] If TP-Link publishes official support, add endpoint scope and tests.

### Exit Criteria

- Snapshot status is documented as supported, unsupported, or TODO with official reference.

## Phase 10: CLI

### Goal

Provide a thin command-line interface over SDK features.

### Tasks

- [ ] Add CLI framework after dependency/license review.
- [ ] Add commands for auth check, device list, and recording search.
- [ ] Redact secrets in output.

### Exit Criteria

- CLI uses SDK APIs only.
- CLI tests use mocks.

## Phase 11: Integration Test Harness Hardening

### Goal

Harden the real-device test harness for supported NVRs and verification devices.

### Tasks

- [ ] Add integration config loader.
- [ ] Add read-only device test.
- [ ] Add recording search test.
- [ ] Add device matrix update workflow.

### Exit Criteria

- Integration tests are opt-in.
- Test output records model, firmware, and OpenAPI document version.

## Phase 12: Release

### Goal

Publish the first usable package release.

### Tasks

- [ ] Finalize license.
- [ ] Convert README from WIP to release-ready.
- [ ] Add release workflow.
- [ ] Tag `v0.1.0`.

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

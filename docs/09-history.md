# History

## Purpose

This document records project progress, documentation milestones, release milestones, and notable implementation progress.

Important design decisions are managed as ADRs under [docs/adr/](adr/). Do not use this file as the primary location for architecture decisions.

## History Rules

- Add entries in reverse chronological order.
- Keep entries concise and factual.
- Link related ADRs when a milestone depends on a design decision.
- Do not delete historical entries to make the project history look cleaner.
- If a design direction changes, add a new ADR instead of rewriting old ADR history.

## Entries

### 2026-07-10: Phase 7 NVR Recording Search Integration Passed

Status: Completed

Summary:

- Recorded successful remote NVR OpenAPI read-only recording search verification against the Chuncheon VIGI NVR.
- Confirmed Bearer-authenticated `GET /openapi/record/days`, `GET /openapi/record/search/free_process`, and `GET /openapi/record/search/results` succeed after documented NVR auth.
- Recorded successful SDK integration test command `python -m pytest tests/test_integration_records.py -v`.
- Recorded test result `tests/test_integration_records.py::test_integration_recording_search_endpoints PASSED`; `1 passed`.
- Verified `client.records.list_days(...)`, `client.records.get_free_process()`, and `client.records.list_results(...)` against the real NVR for Phase 7 scope.
- Verified `RecordDaysResponse`, `RecordSearchProcessResponse`, and `RecordSearchResultsResponse` against the real NVR for the documented response shapes.
- Noted pytest cache warning from `.pytest_cache` permissions while preserving the test pass result.
- Confirmed replay, export, download, snapshot, RTSP, ffmpeg, and video extraction remain out of scope.
- Did not record password, nonce, Digest response, access token, `stok`, or Authorization header values.

### 2026-07-10: Phase 7 NVR Recording Search Implemented

Status: Completed

Summary:

- Implemented documented NVR read-only recording search endpoint wrappers for `GET /openapi/record/days`, `GET /openapi/record/search/free_process`, and `GET /openapi/record/search/results`.
- Added typed `RecordDay`, `RecordDaysResponse`, `RecordSearchProcessResponse`, `RecordSegment`, and `RecordSearchResultsResponse` models using official fields only.
- Added Bearer-authenticated `RecordService` methods for listing recording days, getting a free process, and listing recording result segments.
- Wired `VigiClient.records` through the existing authenticated session and transport.
- Added mock/unit coverage for request construction, response parsing, empty results, malformed responses, API errors, index validation, auth guard behavior, and redaction.
- Added opt-in NVR recording integration test scaffold using explicit `VIGI_RECORDING_*` environment variables.
- Did not add replay, export, download, snapshot, RTSP, ffmpeg, video file storage, IPC public APIs, `VigiCameraClient`, or `VigiNvrClient`.
- Phase 7 real-device verification is recorded separately in the integration-pass history entry.

### 2026-07-10: NVR Device Inventory Integration Passed

Status: Completed

Summary:

- Recorded successful remote NVR OpenAPI read-only inventory verification against the Chuncheon VIGI NVR.
- Confirmed Bearer-authenticated `GET /openapi/added_devices` succeeds after documented NVR auth.
- Recorded successful SDK integration test command `python -m pytest tests/test_integration_devices.py -v`.
- Recorded test result `tests/test_integration_devices.py::test_integration_added_devices_inventory PASSED`; `1 passed`.
- Verified `client.devices.list_added_devices()` and `AddedDevicesResponse` against the real NVR for Phase 6 scope.
- Noted pytest cache warning from `.pytest_cache` permissions while preserving the test pass result.
- Did not record password, nonce, Digest response, access token, or Authorization header values.

### 2026-07-10: Phase 6 NVR Device Inventory Implemented

Status: Completed

Summary:

- Implemented documented NVR `GET /openapi/added_devices` support using Bearer authentication.
- Added typed `AddedDevice` and `AddedDevicesResponse` models using official fields only.
- Added response parsing for `devices`, `error_code`, official channel `id`, and `online` values `"0"` and `"1"`.
- Wired `VigiClient.devices.list_added_devices()` through the existing authenticated session and transport.
- Added mock/unit coverage for request construction, success parsing, empty responses, malformed responses, API errors, auth guard behavior, and redaction.
- Added opt-in NVR device inventory integration test scaffold using `VIGI_HOST`, `VIGI_PORT`, `VIGI_USERNAME`, `VIGI_PASSWORD`, and `VIGI_VERIFY_SSL`.
- Did not add recording search, replay, export, snapshot, RTSP, IPC public APIs, `VigiCameraClient`, or `VigiNvrClient`.
- Phase 6 real-device verification is recorded separately in the integration-pass history entry.

### 2026-07-10: NVR Remote Auth Integration Passed

Status: Completed

Summary:

- Recorded successful remote NVR OpenAPI authentication verification against the Chuncheon VIGI NVR through DDNS plus ipTIME port forwarding.
- Confirmed the documented NVR `GET /openapi/token` Digest challenge over external port `20443`.
- Recorded successful SDK integration test command `python -m pytest tests/test_integration_auth.py -v`.
- Recorded test result `tests/test_integration_auth.py::test_integration_openapi_authentication PASSED`; `1 passed`.
- Noted pytest cache warning from `.pytest_cache` permissions while preserving the test pass result.
- Did not record password, nonce, Digest response, or issued token values.

### 2026-07-10: IPC Internal Hardening Completed

Status: Completed

Summary:

- Added documented IPC auth errCode constants for success and authentication-required challenge responses.
- Hardened internal IPC `doAuth` challenge and success parsing for method, URI, HTTP method, errCode type, and malformed or empty responses.
- Expanded redaction tests so password, nonce, digest response, and `stok` stay out of repr and sanitized exception messages.
- Hardened the opt-in C340I IPC integration scaffold to parse `getStreamPort` JSON and verify method, `errCode: 0`, and `result.streamPort` presence without pinning the stream port value.
- Documented that `.env.example` is a placeholder reference and tests do not auto-load `.env`.
- Kept public SDK exports, public camera clients, snapshot, device-info, and RTSP behavior unchanged.

### 2026-07-10: C340I IPC Integration Test Passed

Status: Completed

Summary:

- Recorded successful opt-in real-device IPC integration test against `VIGI C340I`.
- Test command: `python -m pytest tests/test_integration_ipc_auth.py -v`.
- Test result: `tests/test_integration_ipc_auth.py::test_integration_ipc_do_auth_and_get_stream_port PASSED`; `1 passed`.
- Verified `doAuth` Step 1 challenge, `doAuth` Step 2 `stok` issuance, and post-auth internal `getStreamPort`.
- Confirmed `getStreamPort` returned stream port `554`.
- Noted pytest cache warning from `.pytest_cache` permissions while preserving the test pass result.
- Did not record password, nonce, digest response, or raw `stok`.

### 2026-07-10: Internal IPC Auth Foundation Added

Status: Completed

Summary:

- Added ADR-0006-based internal IPC session, `doAuth`, and control request builders.
- Kept IPC `getStreamPort` as an internal verification method, not a public SDK API.
- Added mock/unit coverage for IPC `doAuth` request parsing, digest response use, redaction, error paths, and `getStreamPort` request building.
- Added opt-in IPC integration scaffold guarded by `VIGI_IPC_*` environment variables and skipped by default.
- Did not add public camera clients, public IPC exports, snapshot, device-info, or RTSP behavior.

### 2026-07-10: C340I IPC Post-Auth Probe Succeeded

Status: Completed

Summary:

- Recorded manual C340I IPC post-auth `getStreamPort` success against `192.168.1.213:20443`.
- Confirmed `getStreamPort` returned `result.streamPort: "554"` and `errCode: 0` with redacted `stok`.
- Confirmed C340I IPC OpenAPI works through `doAuth` plus `stok`, not the NVR `/openapi/token` plus Bearer-token flow.
- Added [ADR-0006 Separate NVR And IPC Auth Transports](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md).
- Kept SDK implementation and public camera client work out of scope.

### 2026-07-10: C340I IPC doAuth Success Recorded

Status: Completed

Summary:

- Recorded manual C340I IPC `doAuth` Step 1 challenge success against `192.168.1.213:20443`.
- Recorded manual C340I IPC `doAuth` Step 2 success with documented `params.nonce` and `params.response` schema.
- Confirmed success response shape as top-level `stok` with `errCode: 0`; the actual `stok` value is redacted and must not be documented.
- Identified official IPC `getStreamPort` as the next low-risk post-auth read-only control probe.
- Kept SDK implementation blocked pending post-auth read-only control verification and IPC auth/transport ADR review.

### 2026-07-10: IPC OpenAPI Document V1.1 Analyzed

Status: Completed

Summary:

- Reviewed official `VIGI IPC OpenAPI Document_V1.1` linked from the C340I download page.
- Confirmed IPC control authentication uses `doAuth` and `stok`, not the NVR `GET /openapi/token` Bearer-token flow.
- Recorded IPC control request format as HTTPS POST JSON on the default ODP-discovered control port `20443`.
- Recorded IPC discovery as ODP local service port `23001` with Ethernet protocol type `0x7210`.
- Recorded IPC stream behavior as RTSP-style `MULTITRANS` with RTP over TCP and default stream port `554`.
- Reframed the C340I malformed `/openapi/token` response as a likely request-format mismatch rather than a valid SDK behavior.
- Kept SDK implementation blocked pending reproducible IPC `doAuth` verification and IPC-specific auth/transport design review.

### 2026-07-10: C340I OpenAPI Token Flow Observation Recorded

Status: Completed

Summary:

- Recorded C340I real-device OpenAPI observation.
- Confirmed C340I hardware version `VIGI C340I 1.20` and firmware version `2.2.0 Build 250926 Rel.53599n`.
- Confirmed OpenAPI Web UI setting and open TCP port `20443` after enabling OpenAPI and rebooting.
- Recorded malformed/HTTP0.9-like response from `/openapi/token` on port `20443`.
- Kept SDK implementation blocked pending official or reproducible token flow confirmation.

### 2026-07-08: Phase 5 C340I Verification Realigned

Status: Completed

Summary:

- Reframed Phase 5 as C340I Camera Integration Verification.
- Added C340I as a next verification target based on official firmware release notes indicating VIGI OpenAPI support.
- Kept MVP scope NVR-first and deferred camera-specific public APIs pending real-device verification and ADR.

### 2026-07-08: Standalone Camera Future Architecture Documented

Status: Completed

Summary:

- Clarified that the current MVP remains NVR-first and targets VIGI NVR OpenAPI with NVR-managed channels/cameras.
- Documented standalone VIGI Camera support as a future expansion candidate only.
- Recorded that standalone camera public APIs require physical camera verification and a new ADR before implementation.

### 2026-07-07: Phase 4.5 Project Quality And Developer Experience Added

Status: Completed

Summary:

- Added WIP README, contributing guide, changelog, security policy, code of conduct, GitHub templates, and CI workflow.
- Added project philosophy as a design principles document.
- Realigned roadmap and checklist to the actual post-authentication order: Device, Recording, Replay, Snapshot.

### 2026-07-07: Phase 4 OpenAPI Authentication Implemented

Status: Completed

Summary:

- Implemented documented token endpoint request, SHA-256 Digest response, token response parsing, and Bearer session state.
- Added urllib-based HTTP transport without adding runtime dependencies.
- Added mock authentication tests and a skipped real-device integration auth scaffold.

### 2026-07-07: Phase 3 Transport And Authentication Foundation Created

Status: Completed

Summary:

- Added transport, session, and authentication provider boundary objects.
- Wired the client to transport and auth provider placeholders without HTTP or login behavior.
- Added construction tests for transport/session/auth stubs with no network access.

### 2026-07-07: Phase 2 Core Models And Types Created

Status: Completed

Summary:

- Added core SDK data models for NVR, devices, channels, recording metadata, time ranges, and RTSP stream metadata.
- Added shared enum types for auth mode, capabilities, device/channel state, recording type, and stream type.
- Added validation-focused tests without HTTP, authentication, device, record search, or RTSP behavior.

### 2026-07-07: Phase 1 Project Skeleton Created

Status: Completed

Summary:

- Added minimal `src` layout Python package skeleton for `vigi`.
- Added import-only skeleton tests without network, authentication, device, record, or RTSP behavior.
- Added `pyproject.toml` with Python 3.10+ and pytest configuration.

### 2026-07-07: Repository Management Files Added

Status: Completed

Summary:

- Added `.gitattributes` to standardize text files on LF and mark binary assets explicitly.
- Added `.gitignore` for Python build, cache, environment, and IDE artifacts.
- Left `.agents/` unignored because its role is still ambiguous for repository operations.

### 2026-07-07: Documentation Index And ADR System Added

Status: Completed

Summary:

- Added [00-index.md](00-index.md) as the documentation entry point.
- Renumbered the document set so the index owns `00`.
- Added ADR management under [docs/adr/](adr/).
- Moved important design-decision tracking out of history and into ADR files.
- Updated Codex workflow instructions and documentation checklist.

Related ADRs:

- [ADR-0001 Capability-Based Architecture](adr/ADR-0001-capability-based-architecture.md)
- [ADR-0002 Authentication Strategy](adr/ADR-0002-authentication-strategy.md)
- [ADR-0003 Record Search Flow](adr/ADR-0003-record-search-flow.md)
- [ADR-0004 RTSP Replay Strategy](adr/ADR-0004-rtsp-replay-strategy.md)
- [ADR-0005 Testing And Integration Strategy](adr/ADR-0005-testing-and-integration-strategy.md)

### 2026-07-07: Initial Project Context Created

Status: Completed

Summary:

- Created the initial project documentation set.
- Established official TP-Link documentation as the source of API facts.
- Defined MVP focus on `VIGI NVR1008H-8P`.
- Deferred SDK code and README creation to later phases.

## Related Documents

- [00-index.md](00-index.md)
- [01-project-plan.md](01-project-plan.md)
- [07-codex-instructions.md](07-codex-instructions.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [docs/adr/README.md](adr/README.md)

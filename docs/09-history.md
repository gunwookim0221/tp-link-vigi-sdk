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

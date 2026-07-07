# vigi-python Project Plan

## Purpose

`vigi-python` is an open-source Python SDK project for TP-Link VIGI NVR OpenAPI.

This document defines the project plan. [00-index.md](00-index.md) is the documentation entry point and should be read first.

If another project document conflicts with this file, update the conflicting document or record the decision in a new ADR under [docs/adr/](adr/).

## Fact

- TP-Link publishes a VIGI NVR OpenAPI guide for calling NVR API interfaces from third-party software.
- The official OpenAPI guide says the OpenAPI function must be enabled in the NVR web interface under `Settings > Network > Openapi`.
- The official OpenAPI guide says the default OpenAPI port is `20443`.
- The official OpenAPI reference PDF identifies the OpenAPI document version as `V1.0` with `Initial release`.
- The official OpenAPI reference PDF defines three OpenAPI areas: control protocol, event protocol, and stream protocol.
- The official OpenAPI reference PDF says VIGI NVR uses RTSP as the stream protocol.

## Vision

Build a maintainable Python foundation that can grow in this order:

1. Python SDK
2. CLI
3. Integration Test Harness
4. AI Pipeline
5. Automation Platform

The SDK must stay centered on the public TP-Link VIGI NVR OpenAPI and must avoid behavior that depends on undocumented reverse engineering.

## MVP

The MVP targets `TP-Link VIGI NVR1008H-8P`.

The first implementation milestone should provide:

- Authentication token acquisition and refresh.
- Read-only device/channel inventory through documented OpenAPI endpoints.
- Capability metadata describing which API groups are supported by the target NVR and firmware.
- A testable transport layer that can run against mocks before it runs against hardware.

## Assumption

- `VIGI NVR1008H-8P` support will be validated against a real device during integration testing.
- Other VIGI NVR models will be added through capability declarations instead of model-specific branching.
- The public OpenAPI surface may change after document version `V1.0`; the project must keep endpoint metadata easy to update.

## Development Principles

- Treat official TP-Link documents as factual sources.
- Treat non-official material as background only, never as normative API truth.
- Mark missing or unverified details as `TODO` or `Assumption`.
- Keep public SDK APIs typed and testable.
- Prefer stable, minimal abstractions over broad framework code.
- Avoid breaking changes before `v1.0` unless the documented API proves the old behavior wrong.
- Record architectural decisions as ADRs under [docs/adr/](adr/).

## Proposed Repository Structure

```text
vigi-python/
  docs/
    00-index.md
    01-project-plan.md
    02-references.md
    03-api-scope.md
    04-architecture.md
    05-test-strategy.md
    06-device-matrix.md
    07-codex-instructions.md
    08-implementation-checklist.md
    09-history.md
    10-limitations.md
    11-roadmap.md
    adr/
      README.md
  src/
    vigi/
      client.py
      auth.py
      transport.py
      capabilities.py
      models/
      api/
  tests/
    unit/
    mock/
    integration/
  pyproject.toml
```

`src/`, `tests/`, and `pyproject.toml` are proposed for later phases. They are not created in Phase 0.

## Expansion Direction

- CLI should be a thin layer over the SDK, not a separate implementation.
- Integration tests should use explicit device configuration and never assume a public network.
- AI Pipeline work should consume SDK outputs through structured types, not by scraping CLI text.
- Automation Platform work should be deferred until the SDK, CLI, and integration tests are stable.

## Related Documents

- [02-references.md](02-references.md)
- [03-api-scope.md](03-api-scope.md)
- [04-architecture.md](04-architecture.md)
- [docs/adr/README.md](adr/README.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [11-roadmap.md](11-roadmap.md)

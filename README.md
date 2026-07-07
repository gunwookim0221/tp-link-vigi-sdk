# TP-Link VIGI SDK

Work in progress Python SDK for TP-Link VIGI NVR OpenAPI.

## Current Status

This project is in early development. It has project documentation, package skeleton, core models/types, transport/authentication foundations, and documented OpenAPI authentication support.

No real VIGI NVR device has been verified yet. Device APIs, recording search, replay, snapshot, CLI, and release documentation are not ready.

## Project Goals

- Provide a typed Python SDK for TP-Link VIGI NVR OpenAPI.
- Use only official TP-Link public OpenAPI documentation as API authority.
- Support `TP-Link VIGI NVR1008H-8P` as the MVP target.
- Grow toward CLI, integration test harness, AI pipeline, and automation platform layers.

## Current Support Scope

Implemented:

- Importable `vigi` package.
- Core SDK data models and enum types.
- Transport and session boundaries.
- OpenAPI authentication flow based on official token endpoint documentation.
- Mock/unit tests and skipped integration auth scaffold.

Not implemented:

- Device inventory API.
- Recording search API.
- RTSP replay support.
- Snapshot support.
- CLI.
- Release-ready public API.

## Supported Device

MVP target:

- `TP-Link VIGI NVR1008H-8P`

Verification status:

- TODO: real-device validation is not recorded yet.

## Project Structure

```text
docs/        Project context, scope, roadmap, ADRs
src/vigi/    Python package
tests/       Unit, mock, and skipped integration scaffolds
```

## Documentation

Start with:

- [docs/00-index.md](docs/00-index.md)
- [docs/project-philosophy.md](docs/project-philosophy.md)
- [docs/08-implementation-checklist.md](docs/08-implementation-checklist.md)
- [docs/11-roadmap.md](docs/11-roadmap.md)
- [docs/adr/README.md](docs/adr/README.md)

## Development Progress

- Phase 0: Documentation Foundation - complete
- Phase 1: Project Skeleton - complete
- Phase 2: Core Models and Types - complete
- Phase 3: Transport and Authentication Foundation - complete
- Phase 4: OpenAPI Authentication Implementation - complete
- Phase 4.5: Project Quality and Developer Experience - complete
- Next feature phase: Device Inventory after real-device authentication validation

## License

TODO: license has not been selected yet.

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by TP-Link. TP-Link and VIGI are trademarks of their respective owners. Use this SDK only with devices and credentials you are authorized to access.

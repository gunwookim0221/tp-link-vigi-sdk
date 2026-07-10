# Changelog

All notable changes to this project will be documented in this file.

This project follows the structure of Keep a Changelog and is not released yet.

## [Unreleased]

### Added

- Phase 0 Documentation Foundation.
- Phase 1 Project Skeleton with `src` layout and pytest setup.
- Phase 2 Core Models and Types.
- Phase 3 Transport and Authentication Foundation.
- Phase 4 OpenAPI Authentication Implementation.
- Phase 4.5 Project Quality and Developer Experience work.
- Phase 8 RTSP replay URL helper with capability gating, explicit UTC replay-time validation, and replay stream `1` enforcement.

### Changed

- Roadmap and implementation checklist aligned to the actual development order.
- Phase 8 re-scoped from replay/export to RTSP replay URL generation because official export/download endpoints are not documented.

### Security

- Credentials and tokens are treated as sensitive and excluded from repr where applicable.

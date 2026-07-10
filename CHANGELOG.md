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
- Phase 10B usage guide, opt-in read-only examples, and example import-safety smoke tests.

### Changed

- Roadmap and implementation checklist aligned to the actual development order.
- Phase 8 re-scoped from replay/export to RTSP replay URL generation because official export/download endpoints are not documented.
- README now documents installation, shell-based environment configuration, a minimal device-inventory quickstart, and current unsupported scope.

### Security

- Credentials and tokens are treated as sensitive and excluded from repr where applicable.
- Examples read credentials from the shell only when explicitly executed and do not print passwords or tokens.

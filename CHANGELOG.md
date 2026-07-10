# Changelog

All notable changes to this project will be documented in this file.

This project follows the structure of Keep a Changelog and is not released yet.

## [Unreleased]

### Changed

- Prepared the package and user-facing documentation for the `0.1.0rc1` release candidate.

## [0.1.0rc1] - 2026-07-10

### Added

- Phase 0 Documentation Foundation.
- Phase 1 Project Skeleton with `src` layout and pytest setup.
- Phase 2 Core Models and Types.
- Phase 3 Transport and Authentication Foundation.
- Phase 4 OpenAPI Authentication Implementation.
- Phase 4.5 Project Quality and Developer Experience work.
- Phase 5 C340I IPC verification and the documented NVR/IPC authentication-transport separation.
- Phase 6 NVR device inventory with `client.devices.list_added_devices()`.
- Phase 7 NVR recording-day and recording-result search APIs.
- Phase 8 RTSP replay URL helper with capability gating, explicit UTC replay-time validation, and replay stream `1` enforcement.
- Phase 9 snapshot support review; snapshot remains unsupported under current official NVR and IPC documentation.
- Phase 10B usage guide, opt-in read-only examples, and example import-safety smoke tests.
- MIT `LICENSE` for open-source distribution.

### Changed

- Updated runtime package version references from `0.0.0` to `0.1.0rc1`.
- GitHub Actions CI now runs Ruff, mypy, pytest, and examples compile smoke checks on Python 3.10 through 3.13.
- Project metadata now includes release-oriented README, license, author, keyword, classifier, and project URL fields.
- Roadmap and implementation checklist aligned to the actual development order.
- Phase 8 re-scoped from replay/export to RTSP replay URL generation because official export/download endpoints are not documented.
- README now documents installation, shell-based environment configuration, a minimal device-inventory quickstart, and current unsupported scope.

### Security

- Credentials and tokens are treated as sensitive and excluded from repr where applicable.
- Examples read credentials from the shell only when explicitly executed and do not print passwords or tokens.

# Project Philosophy

## Purpose

This document defines the engineering principles for `tp-link-vigi-sdk`.

## Project Principles

### Official OpenAPI First

Official TP-Link public documentation is the only source for API facts. Undocumented endpoints and reverse-engineered behavior are excluded.

### Documentation Driven Development

Project documents are the SSOT. Update scope, architecture, limitations, checklist, and history as part of meaningful changes.

### Capability Based Design

Model and firmware support must be represented through capabilities. Avoid hard-coded assumptions that only work for one device.

### Type Safety

Public SDK surfaces should be typed. Data models should be explicit and stable.

### Minimal Dependencies

Prefer the Python standard library unless an external dependency clearly improves correctness, security, or maintainability.

### Mock First

Unit and mock tests come before hardware assumptions. Default tests must not require a VIGI NVR.

### Integration Test Before Feature Expansion

Real-device verification should happen before expanding device-specific functionality beyond documented and mocked behavior.

### ADR Driven Architecture

Important design decisions belong in ADRs. Do not rewrite old ADRs to hide historical decisions.

### Clean Public API

Keep the public API small, predictable, and documented. Avoid exposing implementation details unless they are intentional extension points.

### Backward Compatibility

Avoid breaking public APIs before a documented reason exists. Record breaking decisions before implementing them.

## Related Documents

- [00-index.md](00-index.md)
- [04-architecture.md](04-architecture.md)
- [07-codex-instructions.md](07-codex-instructions.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [adr/README.md](adr/README.md)

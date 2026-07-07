# ADR-0005: Testing And Integration Strategy

## Status

Accepted

## Context

The SDK must be useful without requiring every contributor to own a VIGI NVR. At the same time, real-device verification matters because firmware and model support can vary.

The official documents define API behavior, but project verification requires model, hardware version, firmware version, and test date.

## Decision

Use a layered testing strategy:

- Unit tests for pure logic.
- Mock tests for documented HTTP and RTSP flows.
- Opt-in integration tests for real NVR devices.
- Device matrix updates after real-device verification.

Integration tests must not run by default and must redact credentials and tokens.

## Alternatives Considered

- Require hardware for all tests: rejected because it blocks normal development and CI.
- Rely only on mocks: rejected because real firmware behavior still needs verification.
- Run mutating device tests by default: rejected because it can change user hardware state unexpectedly.

## Consequences

- Test markers must separate unit, mock, integration, read-only device, mutating device, and RTSP tests.
- Integration configuration must be explicit.
- Device verification results must update [../06-device-matrix.md](../06-device-matrix.md).
- Regression tests must be added when real-device behavior differs from assumptions.

## Related Documents

- [../05-test-strategy.md](../05-test-strategy.md)
- [../06-device-matrix.md](../06-device-matrix.md)
- [../07-codex-instructions.md](../07-codex-instructions.md)
- [../08-implementation-checklist.md](../08-implementation-checklist.md)
- [../09-history.md](../09-history.md)

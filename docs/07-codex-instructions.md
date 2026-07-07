# Codex Instructions

## Role

Codex must read [00-index.md](00-index.md) before every task.

Codex should treat the document set as the project SSOT before making code changes.

## Required Rules

- Use only public TP-Link OpenAPI documentation for API facts.
- Read [../README.md](../README.md), [project-philosophy.md](project-philosophy.md), [docs/adr/README.md](adr/README.md), and [08-implementation-checklist.md](08-implementation-checklist.md) before implementation work.
- Do not copy reverse-engineered code or undocumented endpoint behavior.
- Before implementation, read the task-specific documents listed in [00-index.md](00-index.md).
- Update architecture, API scope, test strategy, and limitations documents before implementing changes that affect those areas.
- Add type hints to every public Python API when implementation starts.
- Prefer testable code with small transport seams.
- Add or update `pytest` tests for SDK behavior.
- Do not introduce breaking changes without documenting the reason in a new ADR under [docs/adr/](adr/).
- Keep new documents consistent with existing docs.
- Mark unknowns as `TODO` or `Assumption`.

## Source Authority

| Source type | Allowed use |
| --- | --- |
| Official TP-Link OpenAPI reference | API facts and endpoint behavior. |
| Official TP-Link FAQ/support pages | Setup, compatibility, and operational facts. |
| GitHub projects | Non-authoritative reference for project structure only after license review. |
| Device observations | Project verification facts only when model, hardware, firmware, and test date are recorded. |
| Reverse engineering | Not allowed. |

## Implementation Rules For Later Phases

- Keep transport replaceable for tests.
- Redact credentials and tokens in logs.
- Keep mutating device operations capability-gated.
- Avoid global mutable client state.
- Prefer explicit timeouts.
- Do not silently disable TLS verification.
- Keep CLI behavior thin over SDK behavior.
- Keep runtime dependencies minimal. Add development-only dependencies only when they improve project quality and remain optional.

## Workflow

Use the workflow defined by [00-index.md](00-index.md):

1. Read docs.
2. Plan.
3. Update docs if needed.
4. Implement.
5. Test.
6. Update checklist/history.
7. Report.

## Documentation Rules

- Update [02-references.md](02-references.md) first when official documents change.
- Update [03-api-scope.md](03-api-scope.md) when endpoints are added, removed, or reclassified.
- Update [04-architecture.md](04-architecture.md) before implementing architecture changes.
- Update [05-test-strategy.md](05-test-strategy.md) before changing test categories or integration-test behavior.
- Update [06-device-matrix.md](06-device-matrix.md) after real-device verification.
- Update [10-limitations.md](10-limitations.md) when a limitation is added, removed, or validated.
- Update [08-implementation-checklist.md](08-implementation-checklist.md) and [09-history.md](09-history.md) when work is completed.
- Update [../README.md](../README.md) when project state or supported scope changes.
- Update [../CHANGELOG.md](../CHANGELOG.md) for notable project changes.
- Update [project-philosophy.md](project-philosophy.md) only when the project principles intentionally change.
- Add a new ADR under [docs/adr/](adr/) when a design decision changes. Do not rewrite old ADRs to replace the decision history.

## Related Documents

- [00-index.md](00-index.md)
- [../README.md](../README.md)
- [project-philosophy.md](project-philosophy.md)
- [01-project-plan.md](01-project-plan.md)
- [02-references.md](02-references.md)
- [03-api-scope.md](03-api-scope.md)
- [05-test-strategy.md](05-test-strategy.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [docs/adr/README.md](adr/README.md)
- [../CONTRIBUTING.md](../CONTRIBUTING.md)

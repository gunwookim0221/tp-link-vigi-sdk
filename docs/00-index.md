# Documentation Index

## Purpose

This is the entry point for the `vigi-python` project documentation.

Every Codex task must start by reading this document before planning, editing, or implementing.

## Always Read

Read these documents before every task:

- [../README.md](../README.md)
- [00-index.md](00-index.md)
- [project-philosophy.md](project-philosophy.md)
- [01-project-plan.md](01-project-plan.md)
- [02-references.md](02-references.md)
- [07-codex-instructions.md](07-codex-instructions.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [12-usage-guide.md](12-usage-guide.md)
- [docs/adr/README.md](adr/README.md)

## Task-Specific Documents

Read these documents when the task touches the listed area:

| Task area | Read |
| --- | --- |
| API endpoint scope, official API behavior, support status | [03-api-scope.md](03-api-scope.md), [02-references.md](02-references.md) |
| SDK structure, layers, capabilities, exceptions | [04-architecture.md](04-architecture.md), [docs/adr/README.md](adr/README.md) |
| Testing, integration tests, real-device validation | [05-test-strategy.md](05-test-strategy.md), [06-device-matrix.md](06-device-matrix.md) |
| Device model, firmware, known issues | [06-device-matrix.md](06-device-matrix.md), [10-limitations.md](10-limitations.md) |
| Roadmap or release planning | [11-roadmap.md](11-roadmap.md), [08-implementation-checklist.md](08-implementation-checklist.md) |
| Design decisions | [docs/adr/README.md](adr/README.md), [docs/adr/](adr/) |
| Project progress or milestones | [09-history.md](09-history.md) |
| Contributor or project operations | [../CONTRIBUTING.md](../CONTRIBUTING.md), [../CHANGELOG.md](../CHANGELOG.md), [../SECURITY.md](../SECURITY.md) |
| SDK installation, examples, and read-only workflow | [12-usage-guide.md](12-usage-guide.md), [../README.md](../README.md), [../examples/](../examples/) |

## Workflow

Use this workflow for all implementation and documentation tasks:

1. Read docs.
2. Plan.
3. Update docs if needed.
4. Implement.
5. Test.
6. Update checklist/history.
7. Report.

For documentation-only tasks, the `Implement` step means applying the requested documentation edits. Do not create SDK code unless the task explicitly asks for implementation.

## Update Rules

- Update [02-references.md](02-references.md) first when official TP-Link documentation changes.
- Update [03-api-scope.md](03-api-scope.md) before implementing newly scoped API behavior.
- Update [04-architecture.md](04-architecture.md) before implementing architecture changes.
- Update [05-test-strategy.md](05-test-strategy.md) before changing test categories or integration-test rules.
- Update [10-limitations.md](10-limitations.md) when a known limitation is added, removed, or validated.
- Update [08-implementation-checklist.md](08-implementation-checklist.md) when phase tasks are completed or re-scoped.
- Update [09-history.md](09-history.md) for project milestones and progress notes.
- Update [../CHANGELOG.md](../CHANGELOG.md) for notable project changes.
- Keep [../README.md](../README.md) aligned with the current project state.
- Add a new ADR under [docs/adr/](adr/) when an important design decision changes. Do not overwrite old ADRs to hide history.

## Source Authority

- Official TP-Link public documentation is the only source for API facts.
- Device observations must include model, hardware version, firmware version, and test date before they become project verification facts.
- Unverified details must be marked `TODO` or `Assumption`.

## Related Documents

- [01-project-plan.md](01-project-plan.md)
- [02-references.md](02-references.md)
- [project-philosophy.md](project-philosophy.md)
- [07-codex-instructions.md](07-codex-instructions.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [09-history.md](09-history.md)
- [12-usage-guide.md](12-usage-guide.md)
- [../README.md](../README.md)
- [../CONTRIBUTING.md](../CONTRIBUTING.md)
- [../CHANGELOG.md](../CHANGELOG.md)

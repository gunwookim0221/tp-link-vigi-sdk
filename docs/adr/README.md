# Architecture Decision Records

## Purpose

Architecture Decision Records (ADRs) capture important design decisions for `vigi-python`.

Use ADRs when a decision affects project architecture, public SDK behavior, API support strategy, testing strategy, security posture, or long-term maintainability.

## Rules

- ADRs are cumulative project history.
- Do not delete ADRs.
- Do not overwrite old ADRs to hide or replace past decisions.
- If a decision changes, add a new ADR that supersedes or amends the older one.
- Keep ADRs focused on one decision.
- Mark unknown or unverified details as `TODO` or `Assumption`.
- Official TP-Link public documentation remains the only source for API facts.

## Naming

Use this file name pattern:

```text
ADR-0000-short-kebab-case-title.md
```

## Template

```markdown
# ADR-0000: Title

## Status

Accepted | Proposed | Superseded

## Context

What problem or constraint forced this decision?

## Decision

What decision was made?

## Alternatives

What alternatives were considered?

## Consequences

What changes because of this decision?

## Related Documents

- [../00-index.md](../00-index.md)
```

## ADR Index

- [ADR-0001 Capability-Based Architecture](ADR-0001-capability-based-architecture.md)
- [ADR-0002 Authentication Strategy](ADR-0002-authentication-strategy.md)
- [ADR-0003 Record Search Flow](ADR-0003-record-search-flow.md)
- [ADR-0004 RTSP Replay Strategy](ADR-0004-rtsp-replay-strategy.md)
- [ADR-0005 Testing And Integration Strategy](ADR-0005-testing-and-integration-strategy.md)
- [ADR-0006 Separate NVR And IPC Auth Transports](ADR-0006-separate-nvr-and-ipc-auth-transports.md)

## Related Documents

- [../00-index.md](../00-index.md)
- [../01-project-plan.md](../01-project-plan.md)
- [../04-architecture.md](../04-architecture.md)
- [../07-codex-instructions.md](../07-codex-instructions.md)
- [../09-history.md](../09-history.md)

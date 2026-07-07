# Contributing

## Development Workflow

1. Read [docs/00-index.md](docs/00-index.md).
2. Read [docs/project-philosophy.md](docs/project-philosophy.md).
3. Check [docs/08-implementation-checklist.md](docs/08-implementation-checklist.md).
4. Keep changes scoped to the active phase.
5. Run tests before submitting a pull request.

## Branch Strategy

- `main` should remain stable.
- Use short feature branches, for example `feature/device-inventory` or `docs/roadmap-update`.
- Keep pull requests focused on one concern.

## Commit Convention

Use concise imperative commit messages:

```text
Add OpenAPI authentication tests
Update roadmap for device inventory phase
Fix token response parsing error handling
```

## Testing

Run the default local checks:

```bash
python -m pytest
python -m compileall src tests
```

Integration tests must be opt-in and must not require hardware in the default test run.

## Documentation Rule

- Update docs before or with behavior changes.
- Treat official TP-Link public documentation as the only API fact source.
- Mark unknowns as `TODO` or `Assumption`.
- Keep README content aligned with the current development state.

## ADR Rule

- Add an ADR for important architecture decisions.
- Do not delete or rewrite old ADRs to hide history.
- If a decision changes, add a new ADR that supersedes or amends the old one.

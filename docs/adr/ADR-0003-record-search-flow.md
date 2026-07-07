# ADR-0003: Record Search Flow

## Status

Accepted

## Context

The official OpenAPI reference documents recording APIs:

- `GET /openapi/record/days`
- `GET /openapi/record/search/free_process`
- `GET /openapi/record/search/results`

The reference states that a new search needs a free process ID and that search result ranges use `start_index` and `end_index`.

## Decision

Model recording search as a multi-step SDK workflow rather than as isolated low-level calls only.

The SDK should still expose behavior that can be tested per endpoint, but user-facing recording search should guide callers through:

1. Get days with recording.
2. Get a free search process.
3. Fetch indexed search results for a channel and day.

## Alternatives Considered

- Expose only raw endpoint wrappers: rejected for the public SDK because it would force each user to rediscover the required process-ID flow.
- Hide all process details completely: deferred because integration testing must verify process reuse and pagination behavior against real devices.
- Implement replay without recording search: rejected because replay URL construction needs valid start/end time ranges for useful workflows.

## Consequences

- Recording models must represent days, process IDs, and time ranges.
- Tests must cover process ID handling and index range behavior.
- Integration tests should validate the flow on a real NVR before marking it verified.
- The SDK must avoid inventing recording behavior beyond the official documented fields.

## Related Documents

- [../03-api-scope.md](../03-api-scope.md)
- [../04-architecture.md](../04-architecture.md)
- [../05-test-strategy.md](../05-test-strategy.md)
- [../08-implementation-checklist.md](../08-implementation-checklist.md)
- [../10-limitations.md](../10-limitations.md)

# ADR-0004: RTSP Replay Strategy

## Status

Accepted

## Context

The V1.0-era official OpenAPI reference used for this decision documented the
stream interface as RTSP and the SDK helper was constrained to replay stream
`1`. The reviewed V1.4 reference documents live and replay RTSP URL formats
with stream `1` or `2`. The SDK still supports URL construction for stream `1`
only pending compatibility verification.

The OpenAPI control interface is HTTPS JSON, while stream playback uses RTSP Digest authentication.

## Decision

Treat RTSP replay as a stream capability separate from HTTPS control APIs.

The SDK should first provide documented URL construction and authentication guidance. A full RTSP client implementation is deferred until the project confirms dependency, license, and integration-test requirements.

## Alternatives Considered

- Implement a full RTSP client in the MVP: rejected because the initial MVP should focus on authentication, device inventory, and documented control APIs.
- Treat RTSP URLs as ordinary HTTPS API endpoints: rejected because the official reference defines RTSP as a separate stream interface.
- Support undocumented snapshot or replay endpoints: rejected because they are not official public OpenAPI facts.

## Consequences

- Replay helpers must use UTC time formatting documented by TP-Link.
- Replay stream selection must enforce or clearly document the official stream `1` limitation.
- RTSP tests can start with URL construction before real stream playback tests are added.
- Any future RTSP client dependency requires license and integration-test review.

## Related Documents

- [../02-references.md](../02-references.md)
- [../03-api-scope.md](../03-api-scope.md)
- [../04-architecture.md](../04-architecture.md)
- [../05-test-strategy.md](../05-test-strategy.md)
- [../10-limitations.md](../10-limitations.md)

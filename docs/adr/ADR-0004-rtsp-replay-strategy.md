# ADR-0004: RTSP Replay Strategy

## Status

Accepted

## Context

The official OpenAPI reference says the stream interface is RTSP. It documents live and replay RTSP URL formats and says replay currently supports stream `1`.

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

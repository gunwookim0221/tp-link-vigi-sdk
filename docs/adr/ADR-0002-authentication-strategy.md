# ADR-0002: Authentication Strategy

## Status

Accepted

## Context

The official OpenAPI reference documents `GET /openapi/token` for token acquisition. The flow starts with a no-auth request that returns Digest authentication parameters, then a Digest-authenticated request returns `token_type`, `expires_in`, `access_token`, and `refresh_token`.

The official reference says control requests require Bearer authentication except token acquisition.

## Decision

Implement authentication as a dedicated SDK layer.

The authentication layer will:

- Perform the documented Digest token acquisition flow.
- Store Bearer token state behind the client.
- Refresh tokens through the documented refresh-token request.
- Redact passwords, access tokens, and refresh tokens from logs and exceptions.

## Alternatives Considered

- Ask users to manually pass Bearer tokens: rejected because it makes the SDK harder to use and bypasses documented refresh behavior.
- Embed authentication inside each API method: rejected because it duplicates state handling and error behavior.
- Use undocumented login APIs: rejected because the project only uses public TP-Link OpenAPI documentation.

## Consequences

- API modules can depend on an authenticated transport.
- Authentication failures can map to dedicated exceptions.
- Tests must cover Digest challenge parsing, response generation, token refresh, and redaction.
- TLS verification policy must remain explicit and must not be silently disabled.

## Related Documents

- [../02-references.md](../02-references.md)
- [../03-api-scope.md](../03-api-scope.md)
- [../04-architecture.md](../04-architecture.md)
- [../05-test-strategy.md](../05-test-strategy.md)
- [../10-limitations.md](../10-limitations.md)

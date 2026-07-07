# Security Policy

## Reporting a Vulnerability

Please report suspected security issues privately by opening a GitHub security advisory if available, or by contacting the project maintainer through the repository owner profile.

Do not publish exploit details in public issues before the maintainer has had a reasonable chance to review the report.

## Credential Policy

- Do not commit real NVR hostnames, usernames, passwords, access tokens, refresh tokens, or Authorization headers.
- Use environment variables for integration tests.
- Keep integration test output free of secrets.
- Redact credentials and tokens in logs, repr output, and error messages.

## Responsible Disclosure

When reporting a vulnerability, include:

- Affected component.
- Reproduction steps.
- Expected impact.
- Suggested mitigation if known.

The project will prioritize issues involving credential exposure, authentication bypass, unsafe TLS defaults, or unintended device state changes.

## Device Safety

Integration tests must be opt-in. Mutating device operations must never run by default.

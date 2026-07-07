# References

## Official References

These are the only factual API authorities for this project.

| Source | URL | Status | Notes |
| --- | --- | --- | --- |
| TP-Link VIGI OpenAPI Guide | https://www.tp-link.com/us/support/faq/4797/ | Official | Updated `2025-11-20`; describes enabling OpenAPI, default port, Digest token flow, and example API calls. |
| Supported Products | https://www.tp-link.com/us/vigi-open-api/product-list/ | Official | States that listed and higher hardware versions of listed models are supported, latest firmware should be installed, and the list may be updated. |
| Official OpenAPI Reference PDF | https://static-community.tp-link.com/attach/14/2/2026/f4faddd9dbc246e3adbcc969ae457737.pdf | Official | `VIGI NVR Open API Document`, version `V1.0`, `Initial release`. |
| RTSP / Web Access Guide Provided For This Project | https://www.tp-link.com/us/support/faq/4933/ | Official | The linked page title is `How do I log in to the web management page of VIGI IPC and NVR`, updated `2026-01-30`; it is useful for web access and device IP discovery, not a dedicated RTSP API reference. |

## Official OpenAPI Version

| Item | Value |
| --- | --- |
| Document title | `VIGI NVR Open API Document` |
| Version | `V1.0` |
| Update history | `Initial release` |
| Verified date for this project context | `2026-07-07` |

## Fact

- The OpenAPI control interface supports HTTPS only.
- The OpenAPI Discovery Protocol port is documented as `20443`.
- Control requests require Bearer authentication except token acquisition.
- Token acquisition uses `GET /openapi/token` with Digest authentication.
- Token refresh uses `GET /openapi/token?grant_type=refresh_token&refresh_token=...`.
- The official reference says the stream interface is RTSP and supports live and replay URLs.

## GitHub Reference Projects

No GitHub project is accepted as a factual source for API behavior.

TODO:

- Identify useful GitHub projects only for packaging, test layout, CLI ergonomics, and documentation style.
- Record each candidate with license, maintenance state, and why it is non-authoritative for TP-Link API behavior.

## License References

TODO:

- Select the project license before publishing SDK code.
- Confirm compatibility for planned dependencies such as HTTP client, CLI framework, and test tools.
- Add links to official license texts after selection.

## Document Update Management

When TP-Link updates official documentation:

1. Update this reference table first.
2. Record the observed change in [09-history.md](09-history.md).
3. Update API scope in [03-api-scope.md](03-api-scope.md).
4. Update device support in [06-device-matrix.md](06-device-matrix.md).
5. Update implementation phases in [08-implementation-checklist.md](08-implementation-checklist.md) if required.
6. Add a new ADR under [docs/adr/](adr/) if the official change affects a design decision.

## Related Documents

- [00-index.md](00-index.md)
- [01-project-plan.md](01-project-plan.md)
- [03-api-scope.md](03-api-scope.md)
- [06-device-matrix.md](06-device-matrix.md)
- [09-history.md](09-history.md)
- [10-limitations.md](10-limitations.md)

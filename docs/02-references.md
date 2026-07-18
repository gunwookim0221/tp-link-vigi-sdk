# References

## Official References

These are the only factual API authorities for this project.

| Source | URL | Status | Notes |
| --- | --- | --- | --- |
| TP-Link VIGI OpenAPI Guide | https://www.tp-link.com/us/support/faq/4797/ | Official | Updated `2025-11-20`; describes enabling OpenAPI, default port, Digest token flow, and example API calls. |
| Supported Products | https://www.tp-link.com/us/vigi-open-api/product-list/ | Official | States that listed and higher hardware versions of listed models are supported, latest firmware should be installed, and the list may be updated. `VIGI C340I` was not identified in the fetched page text during the `2026-07-10` review. |
| Official OpenAPI Reference PDF | https://static-community.tp-link.com/attach/14/2/2026/f4faddd9dbc246e3adbcc969ae457737.pdf | Official | `VIGI NVR Open API Document`, version `V1.0`, `Initial release`. |
| NVR RTSP Server Guide | https://www.tp-link.com/pt/support/faq/4677/ | Official | Documents the NVR live URL `rtsp://<IP>/live/<channel>/<stream>/avm`, main/minor stream selectors, and separate NVR-credential RTSP authentication. |
| RTSP / Web Access Guide Provided For This Project | https://www.tp-link.com/us/support/faq/4933/ | Official | The linked page title is `How do I log in to the web management page of VIGI IPC and NVR`, updated `2026-01-30`; it is useful for web access and device IP discovery, not a dedicated RTSP API reference. |
| TP-Link VIGI C340I Firmware Release Note | https://static.tp-link.com/upload/firmware/2025/202511/20251104/Release%20Note%20VIGI%20C340I%28UN%29%201.2_2.2.0%20Build%20250926.pdf | Official firmware release note | `VIGI C340I(UN) V1.20 2.2.0 Build 250926`, release date `2025-11-04`, indicates added support for `VIGI OpenAPI`. |
| TP-Link VIGI C340I Download Page | https://www.tp-link.com/us/support/download/vigi-c340i/ | Official product support page | Lists `VIGI C340I V1.20` and a standalone `VIGI IPC OpenAPI Document_V1.1` under manuals. |
| VIGI IPC OpenAPI Document_V1.1 | https://www.tp-link.com/us/document/127722/ | Official standalone IPC OpenAPI document | Describes IPC discovery, control, stream, and `doAuth` authentication flows. Control authentication does not use the NVR `/openapi/token` endpoint. |
| TP-Link VIGI Wired Camera User Guide | https://www.tp-link.com/uk/document/20556/ | Official product user guide | Documents `Settings > Network Settings > Openapi` for camera web UI integration setup, but does not define the token endpoint flow. |

## Official NVR OpenAPI Version

| Item | Value |
| --- | --- |
| Document title | `VIGI NVR Open API Document` |
| Version | `V1.0` |
| Update history | `Initial release` |
| Verified date for this project context | `2026-07-07` |

## Fact

- The NVR OpenAPI control interface supports HTTPS only.
- The NVR OpenAPI guide documents the default OpenAPI control port as `20443`.
- NVR control requests require Bearer authentication except token acquisition.
- NVR token acquisition uses `GET /openapi/token` with Digest authentication.
- NVR token refresh uses `GET /openapi/token?grant_type=refresh_token&refresh_token=...`.
- The NVR official reference says the stream interface is RTSP and supports live and replay URLs.
- The official NVR RTSP guide documents the live URL as `rtsp://<IP>/live/<channel>/<stream>/avm`; stream `1` is main and stream `2` is minor.
- RTSP authentication uses the NVR username and password through the RTSP server's configured Digest algorithm; it is separate from HTTPS OpenAPI Bearer authentication.
- C340I OpenAPI support is officially indicated in TP-Link firmware release notes for `VIGI C340I(UN) V1.20` firmware `2.2.0 Build 250926`.
- Actual C340I endpoint behavior must still be verified on the user's hardware and firmware before SDK support is claimed.
- C340I hardware version and installed firmware version must be recorded before device observations become project verification facts.
- The C340I download page identifies a standalone `VIGI IPC OpenAPI Document_V1.1`.
- The VIGI Wired Camera User Guide documents the camera Web UI OpenAPI setting under `Settings > Network Settings > Openapi`.

## Official IPC OpenAPI Facts

Review date: `2026-07-10`.

- `VIGI IPC OpenAPI Document_V1.1` defines three IPC OpenAPI parts: discovery protocol, control protocol, and stream protocol.
- IPC discovery uses OpenAPI Discovery Protocol. The document states local service port `23001` and Ethernet protocol type `0x7210`.
- IPC control requests use HTTPS `POST https://device_addr:port/stok=xx HTTP/1.1` with a JSON body such as `{"method":"xx","params":{...}}`.
- IPC control interface port is obtained through ODP and defaults to `20443`.
- IPC control authentication uses `Method: doAuth`, not `GET /openapi/token`.
- IPC `doAuth` step 1 posts `{"method":"doAuth","params":null}` to `https://device_addr:port` and receives `authenticate` fields plus `errCode: -10020`.
- IPC `doAuth` step 2 posts the returned nonce and calculated response to `https://device_addr:port`; success returns `stok` and `errCode: 0`.
- IPC `doAuth` SHA-256 response calculation is documented as `A1 = SHA256(admin:realm:password)`, `A2 = SHA256(method:uri)`, and `response = SHA256(A1:nonce:A2)`.
- IPC stream requests use RTSP-style `MULTITRANS rtsp://ip/multitrans RTSP/1.0` with JSON content; stream data uses RTP over TCP.
- IPC stream interface port corresponds to RTSP, defaults to `554`, and is available through `getStreamPort`.
- IPC Digest Authentication in section `2.2.2` is documented for establishing OpenAPI stream connections, not for IPC control `doAuth`.

## Official Document Review Notes

Review date: `2026-07-10`.

- The `VIGI NVR Open API Document` V1.0 does not document a snapshot or capture endpoint. Its multipart mention describes NVR event-push formatting, not a snapshot response.
- `VIGI IPC OpenAPI Document_V1.1` does not document a snapshot or capture method. There is no official basis for an IPC `stok`-based snapshot request or response shape.
- The NVR OpenAPI FAQ documents `GET /openapi/token`, no-auth Digest challenge acquisition, SHA-256 Digest response calculation, Bearer token usage, and default OpenAPI port `20443`.
- The VIGI OpenAPI supported product list page documents the support policy for listed and higher hardware versions and latest firmware, but `VIGI C340I` was not found in the fetched page text during this review.
- The C340I firmware release note for `VIGI C340I(UN) V1.20 2.2.0 Build 250926` documents added support for `VIGI OpenAPI`.
- The standalone camera OpenAPI document is `VIGI IPC OpenAPI Document_V1.1` and is linked from the official C340I download page.
- The NVR OpenAPI FAQ and IPC OpenAPI document describe different authentication/request flows.
- `GET /openapi/token` is documented for the NVR flow, but it was not identified in the IPC control authentication flow.
- C340I standalone verification must use the IPC document flow, starting with a manual `doAuth` probe, before any SDK implementation is considered.

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

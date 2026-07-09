# API Scope

## Scope Rules

- Supported APIs must be present in the official TP-Link OpenAPI reference PDF or official TP-Link FAQ pages.
- APIs not found in official documents must be marked `TODO` or excluded.
- Endpoint behavior must be implemented from documented request/response fields only.
- Model-specific behavior must be represented through capabilities.

## Official API Groups

| Group | Official endpoints | MVP status |
| --- | --- | --- |
| Authentication | `GET /openapi/token` | Phase 4 NVR flow only |
| Channel Management | `GET /openapi/added_devices` | Phase 6 |
| Video | `GET /openapi/resolution`, `GET /openapi/valid_resolutions`, `POST /openapi/resolution`, `GET /openapi/bitrate`, `GET /openapi/bitrate_capability`, `POST /openapi/bitrate` | Later SDK phase |
| Time | `GET /openapi/timing_mode`, `PUT /openapi/timing_mode`, `GET /openapi/ntp`, `PUT /openapi/ntp` | Later SDK phase |
| Audio | `GET /openapi/audio/output/sound`, `GET /openapi/audio/input/sound`, `POST /openapi/audio/output/sound`, `POST /openapi/audio/input/sound` | Later SDK phase |
| Disk | `GET /openapi/disks`, `GET /openapi/esata_disks`, `POST /openapi/smartctl_process`, `GET /openapi/smartctl_process/capability`, `POST /openapi/smartctl_process/test`, `GET /openapi/smartctl_process/schedule`, `GET /openapi/smartctl_process/attribute` | Later SDK phase |
| PoE | `GET /openapi/poe/info`, `POST /openapi/poe/info`, `GET /openapi/poe/link_mode`, `POST /openapi/poe/link_mode`, `GET /openapi/poe/status`, `GET /openapi/poe/link_status` | Later SDK phase |
| Event | `GET /openapi/event_server`, `POST /openapi/event_server`, `POST /openapi/event_server/delete_server` | Later SDK phase |
| Recording | `GET /openapi/record/days`, `GET /openapi/record/search/free_process`, `GET /openapi/record/search/results` | Phase 7 |
| System | `POST /openapi/systemctl` | Excluded from MVP write path |
| Stream | RTSP live URL and replay URL | Phase 8 planning |

## MVP Supported API

The MVP should support:

- `GET /openapi/token`
- `GET /openapi/token?grant_type=refresh_token&refresh_token=...`
- `GET /openapi/added_devices`
- Capability discovery from static project metadata and optional device probes.

The MVP authentication endpoints above are NVR OpenAPI endpoints. They must not be applied to standalone IPC cameras unless an official IPC document explicitly documents the same endpoint for IPC control authentication.

## Device Mode Scope

| Mode | Current scope | Project status |
| --- | --- | --- |
| NVR Mode | VIGI NVR OpenAPI and NVR-managed channels/cameras. | Current MVP target path. |
| Standalone Camera Mode | Direct standalone VIGI IPC OpenAPI behavior. | C340I is a Phase 5 shared-layer verification target based on official firmware release notes and `VIGI IPC OpenAPI Document_V1.1`; public camera SDK support is not yet in scope. |

The current public API scope is NVR-first. Connected cameras are in scope only when represented by documented NVR OpenAPI responses, such as NVR-managed channels or added devices.

Standalone camera direct login, snapshot, stream, settings, and other direct camera APIs are out of current MVP scope. C340I OpenAPI support is indicated by official firmware release notes, but endpoint behavior still requires physical standalone camera integration testing against the IPC OpenAPI document. Public camera SDK support requires official documentation or release-note coverage, verification records, and a new architecture ADR.

## Standalone IPC Scope Notes

`VIGI IPC OpenAPI Document_V1.1` does not describe IPC control authentication as the NVR `GET /openapi/token` Bearer-token flow. It describes IPC control authentication through `Method: doAuth`:

- Step 1: `POST https://device_addr:port` with JSON `{"method":"doAuth","params":null}`.
- Step 2: `POST https://device_addr:port` with returned `nonce` and calculated `response`.
- Success returns `stok`.
- Subsequent IPC control requests use HTTPS `POST https://device_addr:port/stok=xx` with JSON method payloads.

The IPC control protocol is HTTP/1.1 over HTTPS with JSON bodies, but it is not a REST endpoint family like the NVR `/openapi/...` paths. Existing endpoint-oriented urllib transport may be reusable at the low level, but the NVR `AuthService` and `/openapi/token` request builder are not directly reusable for IPC control authentication without a separate IPC protocol/auth design.

### C340I Post-Auth Probe Result

Manual C340I probing has confirmed IPC `doAuth` Step 1 challenge, Step 2 `stok` issuance, and post-auth read-only control access through `getStreamPort`. The actual `stok`, password, nonce-derived response, and other secrets must not be recorded in project documents.

The verified low-risk official IPC control method is `getStreamPort`:

- Official IPC section: `4.12.1 getStreamPort`.
- Purpose: get the stream protocol port.
- Request: `NULL`.
- Example request body: `{"method":"getStreamPort"}`.
- Verified success shape: top-level `method`, `errCode: 0`, and `result.streamPort` value `"554"`.
- Call URL shape: `POST https://device_addr:20443/stok=<stok>`.

This method confirms that C340I IPC OpenAPI works after `doAuth`, while also confirming that IPC control auth is not compatible with the NVR `/openapi/token` plus Bearer-token flow. SDK implementation remains out of scope until the auth/transport split in [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md) is followed.

## Supported Soon

Phase 7:

- `GET /openapi/record/days`
- `GET /openapi/record/search/free_process`
- `GET /openapi/record/search/results`

Phase 5:

- C340I Camera Integration Verification for shared authentication, transport, session, error-handling, and integration-test harness behavior.

Phase 6:

- `GET /openapi/added_devices`

Phase 8:

- RTSP live URL construction.
- RTSP replay URL construction.
- RTSP Digest authentication integration plan.

Phase 9:

- Snapshot support is `TODO` because no snapshot OpenAPI endpoint was identified in the official reference PDF during Phase 0.

## Excluded From MVP

- Mutating video settings.
- Mutating audio settings.
- Mutating PoE settings.
- Event server write/delete operations.
- `POST /openapi/systemctl` reboot behavior.
- Disk SMART test start operations.
- GUI automation.
- Undocumented web UI APIs.
- Direct standalone VIGI Camera APIs.
- Applying the NVR `/openapi/token` flow to standalone IPC cameras without official IPC documentation.
- Treating IPC control method names as REST endpoints.

## API Stability

| Level | Meaning |
| --- | --- |
| `documented` | Endpoint appears in official OpenAPI reference PDF. |
| `verified` | Endpoint has been exercised against a real supported NVR and covered by integration tests. |
| `capability-gated` | Endpoint is documented but enabled only when the target model/firmware capability says it is available. |
| `todo` | Desired feature is not yet mapped to an official endpoint. |

## Version Policy

- Project API metadata starts at official OpenAPI document `V1.0`.
- If TP-Link publishes a newer OpenAPI document, keep the old metadata until a compatibility review is complete.
- SDK public API versions must not imply support for undocumented TP-Link endpoints.

## Related Documents

- [02-references.md](02-references.md)
- [04-architecture.md](04-architecture.md)
- [05-test-strategy.md](05-test-strategy.md)
- [08-implementation-checklist.md](08-implementation-checklist.md)
- [10-limitations.md](10-limitations.md)

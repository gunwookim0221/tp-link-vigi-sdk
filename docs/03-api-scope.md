# API Scope

## Scope Rules

- Supported APIs must be present in the official TP-Link OpenAPI reference PDF or official TP-Link FAQ pages.
- APIs not found in official documents must be marked `TODO` or excluded.
- Endpoint behavior must be implemented from documented request/response fields only.
- Model-specific behavior must be represented through capabilities.

## Official API Groups

| Group | Official endpoints | MVP status |
| --- | --- | --- |
| Authentication | `GET /openapi/token` | Phase 2 |
| Channel Management | `GET /openapi/added_devices` | Phase 3 |
| Video | `GET /openapi/resolution`, `GET /openapi/valid_resolutions`, `POST /openapi/resolution`, `GET /openapi/bitrate`, `GET /openapi/bitrate_capability`, `POST /openapi/bitrate` | Later SDK phase |
| Time | `GET /openapi/timing_mode`, `PUT /openapi/timing_mode`, `GET /openapi/ntp`, `PUT /openapi/ntp` | Later SDK phase |
| Audio | `GET /openapi/audio/output/sound`, `GET /openapi/audio/input/sound`, `POST /openapi/audio/output/sound`, `POST /openapi/audio/input/sound` | Later SDK phase |
| Disk | `GET /openapi/disks`, `GET /openapi/esata_disks`, `POST /openapi/smartctl_process`, `GET /openapi/smartctl_process/capability`, `POST /openapi/smartctl_process/test`, `GET /openapi/smartctl_process/schedule`, `GET /openapi/smartctl_process/attribute` | Later SDK phase |
| PoE | `GET /openapi/poe/info`, `POST /openapi/poe/info`, `GET /openapi/poe/link_mode`, `POST /openapi/poe/link_mode`, `GET /openapi/poe/status`, `GET /openapi/poe/link_status` | Later SDK phase |
| Event | `GET /openapi/event_server`, `POST /openapi/event_server`, `POST /openapi/event_server/delete_server` | Later SDK phase |
| Recording | `GET /openapi/record/days`, `GET /openapi/record/search/free_process`, `GET /openapi/record/search/results` | Phase 4 |
| System | `POST /openapi/systemctl` | Excluded from MVP write path |
| Stream | RTSP live URL and replay URL | Phase 5 planning |

## MVP Supported API

The MVP should support:

- `GET /openapi/token`
- `GET /openapi/token?grant_type=refresh_token&refresh_token=...`
- `GET /openapi/added_devices`
- Capability discovery from static project metadata and optional device probes.

## Supported Soon

Phase 4:

- `GET /openapi/record/days`
- `GET /openapi/record/search/free_process`
- `GET /openapi/record/search/results`

Phase 5:

- RTSP live URL construction.
- RTSP replay URL construction.
- RTSP Digest authentication integration plan.

Phase 6:

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

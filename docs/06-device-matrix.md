# Device Matrix

## Policy

This matrix tracks project verification status. Official TP-Link support status must be checked through the official supported products page and model support pages.

## Fact

- The official OpenAPI guide lists `VIGI NVR1008H-8P( V1.20 )` in the article applicability list.
- The supported products page says listed and higher hardware versions of listed models are supported by VIGI Open API.
- The supported products page says latest firmware should be installed.
- TP-Link states that product availability varies by region and that the compatible device list may be updated.
- TP-Link firmware release notes for `VIGI C340I(UN) V1.20 2.2.0 Build 250926` indicate added support for `VIGI OpenAPI`.

## MVP Device

| Model | Hardware version | Firmware | OpenAPI status | Project verification | Known issues |
| --- | --- | --- | --- | --- | --- |
| VIGI NVR1008H-8P | `V1.20` from official guide applicability list | TODO | Official guide applicability list includes this model/version | Remote OpenAPI auth, read-only `GET /openapi/added_devices`, and read-only recording search integration verified | TODO |

## Verification Devices

| Model | Type | Role | Hardware | Firmware | OpenAPI status | Verification status | Purpose |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VIGI C340I | Standalone Camera | Verification Target | `VIGI C340I 1.20` | `2.2.0 Build 250926 Rel.53599n` | Firmware release note indicates OpenAPI support; Web UI exposes OpenAPI setting; IPC OpenAPI document applies | IPC `doAuth` Step 1/2 and post-auth read-only `getStreamPort` verified by real-device integration test | Validate IPC auth/transport assumptions separately before any camera SDK expansion |
| VIGI NVR1008H-8P | NVR | MVP Target | `V1.20` from official guide applicability list / TODO confirm actual hardware | TODO confirm | Official NVR OpenAPI target | Remote `/openapi/token` Digest challenge, SDK auth integration test, read-only `/openapi/added_devices` integration test, and read-only recording search integration test verified | Validate replay and export |

## NVR Remote Auth Observation

Observation date: `2026-07-10`.

| Item | Observation |
| --- | --- |
| Target | Chuncheon VIGI NVR |
| Access path | DDNS plus ipTIME port forwarding |
| Host | `smaniac.iptime.org` |
| External port | `20443` |
| OpenAPI endpoint | `GET /openapi/token` |
| Digest challenge | Confirmed through the remote NVR OpenAPI endpoint |
| SDK integration test | `python -m pytest tests/test_integration_auth.py -v` passed `tests/test_integration_auth.py::test_integration_openapi_authentication`; `1 passed` |
| Integration test note | Pytest cache warning occurred due to `.pytest_cache` permission, but the real-device auth test passed |

Current conclusion:

- Remote NVR OpenAPI auth against `GET /openapi/token` is verified through the SDK integration scaffold.
- The NVR documented Digest challenge flow works over DDNS and forwarded external port `20443`.
- Secret material such as password, nonce, Digest response, and issued token must remain redacted.
- Phase 6 can proceed to NVR read-only inventory work because NVR auth validation is no longer the gating item.

## NVR Device Inventory Observation

Observation date: `2026-07-10`.

| Item | Observation |
| --- | --- |
| Target | Chuncheon VIGI NVR |
| Access path | DDNS plus ipTIME port forwarding |
| OpenAPI endpoint | `GET /openapi/added_devices` |
| Authentication shape | NVR auth succeeded first, then Bearer-authenticated inventory request succeeded |
| SDK public method | `client.devices.list_added_devices()` succeeded |
| SDK response type | `AddedDevicesResponse` verified |
| Inventory result | Connected added-device inventory returned successfully |
| Integration test | `python -m pytest tests/test_integration_devices.py -v` passed `tests/test_integration_devices.py::test_integration_added_devices_inventory`; `1 passed` |
| Integration test note | Pytest cache warning occurred due to `.pytest_cache` permission, but the real-device inventory test passed |

Current conclusion:

- Remote NVR OpenAPI read-only inventory against `GET /openapi/added_devices` is verified through the SDK integration scaffold.
- `client.devices.list_added_devices()` is verified against the real NVR for the documented response shape.
- `AddedDevicesResponse` is verified by real-device integration for Phase 6 scope.
- Phase 6 is complete and Phase 7 recording search can proceed.

## NVR Recording Search Observation

Observation date: `2026-07-10`.

| Item | Observation |
| --- | --- |
| Target | Chuncheon VIGI NVR |
| Access path | DDNS plus ipTIME port forwarding |
| OpenAPI endpoints | `GET /openapi/record/days`, `GET /openapi/record/search/free_process`, `GET /openapi/record/search/results` |
| Authentication shape | NVR auth succeeded first, then Bearer-authenticated recording search requests succeeded |
| SDK public methods | `client.records.list_days(...)`, `client.records.get_free_process()`, and `client.records.list_results(...)` succeeded |
| SDK response types | `RecordDaysResponse`, `RecordSearchProcessResponse`, and `RecordSearchResultsResponse` verified |
| Search result | Read-only recording day lookup, process lookup, and segment listing returned successfully |
| Integration test | `python -m pytest tests/test_integration_records.py -v` passed `tests/test_integration_records.py::test_integration_recording_search_endpoints`; `1 passed` |
| Integration test note | Pytest cache warning occurred due to `.pytest_cache` permission, but the real-device recording search test passed |

Current conclusion:

- Remote NVR OpenAPI read-only recording search against the documented Phase 7 endpoints is verified through the SDK integration scaffold.
- `client.records.list_days(...)`, `client.records.get_free_process()`, and `client.records.list_results(...)` are verified against the real NVR for the documented response shapes.
- `RecordDaysResponse`, `RecordSearchProcessResponse`, and `RecordSearchResultsResponse` are verified by real-device integration for Phase 7 scope.
- Replay, export, download, snapshot, RTSP, ffmpeg, and video extraction remain out of scope for this verification.
- Phase 7 is complete and Phase 8 replay/export planning can proceed.

## C340I Real-Device Observation

Observation date: `2026-07-10`.

| Item | Observation |
| --- | --- |
| Device | `VIGI C340I` |
| Hardware version | `VIGI C340I 1.20` |
| Firmware version | `2.2.0 Build 250926 Rel.53599n` |
| IP address | Local lab device, `192.168.1.213` |
| OpenAPI UI setting | Exists under `Network Settings > Openapi` |
| OpenAPI state | Enabled, applied, and device rebooted |
| TCP `20443` | Open after enabling OpenAPI |
| `GET https://192.168.1.213:20443/openapi/token` | `curl` reported `Received HTTP/0.9 when not allowed`; Postman reported malformed response parse error |
| `GET https://192.168.1.213/openapi/token` | `HTTP/1.1 404 Not Found` |
| `GET http://192.168.1.213/openapi/token` | `HTTP/1.1 302` redirect to `https://192.168.1.213:443` |
| IPC `doAuth` Step 1 | `POST https://192.168.1.213:20443` with `{"method":"doAuth","params":null}` returned `authenticate` fields and `errCode: -10020` challenge |
| IPC `doAuth` Step 2 | `POST https://192.168.1.213:20443` with `params.nonce` and `params.response` returned `stok` and `errCode: 0`; `stok` redacted |
| IPC post-auth read-only method | Official IPC `getStreamPort`, request body `{"method":"getStreamPort"}`, URL `POST https://192.168.1.213:20443/stok=<redacted>`, returned `result.streamPort: "554"` and `errCode: 0` |
| IPC integration test | `python -m pytest tests/test_integration_ipc_auth.py -v` passed `tests/test_integration_ipc_auth.py::test_integration_ipc_do_auth_and_get_stream_port`; `1 passed` |
| IPC integration test note | Pytest cache warning occurred due to `.pytest_cache` permission, but the real-device test passed |

Current conclusion:

- C340I OpenAPI support is indicated by official firmware release notes and the Web UI exposes an OpenAPI setting.
- `VIGI IPC OpenAPI Document_V1.1` does not document IPC control authentication as `GET /openapi/token`.
- The malformed/HTTP0.9-like response from `GET /openapi/token` on port `20443` is consistent with applying the wrong NVR REST endpoint shape to an IPC control port that expects IPC HTTPS POST JSON requests.
- The malformed response must not be interpreted as a successful authentication response.
- IPC `doAuth` has now been manually verified through Step 2 `stok` issuance.
- IPC post-auth read-only control has now been manually verified through official `getStreamPort`.
- IPC `doAuth` and post-auth `getStreamPort` are now verified by the opt-in real-device integration test.
- C340I IPC OpenAPI works, but it is not compatible with the NVR `/openapi/token` plus Bearer-token flow.
- SDK implementation remains pending architecture work documented in [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md).

## Support Modes

| Mode | Scope | Verification status | Notes |
| --- | --- | --- | --- |
| NVR Mode | VIGI NVR OpenAPI and NVR-managed channels/cameras. | Remote auth integration, read-only `GET /openapi/added_devices` inventory integration, and read-only recording search integration are verified for the MVP NVR. | MVP starts with `VIGI NVR1008H-8P`; replay/export remains the next validation target. |
| Standalone Camera Mode | Direct standalone VIGI IPC OpenAPI behavior. | C340I lab verification and opt-in integration test confirmed IPC `doAuth`, `stok`, and post-auth `getStreamPort`; NVR `/openapi/token` is not the IPC control auth flow. | Verified for IPC-specific auth/transport analysis only; not a supported public SDK device. |

## Candidate Devices From Official OpenAPI Guide Applicability List

These models appear in the official OpenAPI guide applicability list. Project support is not implied until tested.

| Model | Hardware version text from official guide | Project status |
| --- | --- | --- |
| VIGI NVR1008H | `V2.20` | TODO |
| VIGI NVR4064H | `V1` | TODO |
| VIGI NVR4032H | `V1` | TODO |
| VIGI NVR1004H | `V1` | TODO |
| VIGI NVR4016H | `V1` | TODO |
| VIGI NVR1008H-8MP | `V1.20` | TODO |
| VIGI NVR1016H | `V1.20` | TODO |
| VIGI NVR2008H-8MP | `V1 V2` | TODO |
| VIGI NVR2016H-16P | `V1 V2` | TODO |
| VIGI NVR1008H-8P | `V1.20` | MVP target |
| VIGI NVR1004H-4P | `V1` | TODO |
| VIGI NVR2016H | `V1.20 V2` | TODO |
| VIGI NVR1104H-4P | `V1` | TODO |
| VIGI NVR2016H-16MP | `V1 V2` | TODO |
| VIGI NVR1108H-W | `V1` | TODO |

## Verification States

| State | Meaning |
| --- | --- |
| `official-listed` | Listed in official TP-Link source. |
| `lab-planned` | A project maintainer plans to test the device. |
| `readonly-verified` | Read-only OpenAPI calls pass against hardware. |
| `mutating-verified` | Mutating OpenAPI calls pass against hardware. |
| `rtsp-verified` | Live/replay stream behavior is verified. |
| `unsupported` | Official or project verification says the device should not be supported. |

## Related Documents

- [02-references.md](02-references.md)
- [03-api-scope.md](03-api-scope.md)
- [05-test-strategy.md](05-test-strategy.md)
- [10-limitations.md](10-limitations.md)
- [11-roadmap.md](11-roadmap.md)

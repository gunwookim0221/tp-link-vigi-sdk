# VIGI NVR OpenAPI V1.0 to V1.4 Delta

## Scope and baseline

This is a compatibility analysis, not an implementation plan disguised as an
API client. The authoritative V1.4 source is the local PDF registered in
[the V1.4 reference record](nvr-openapi-v1.4-reference.md). The V1.0 side is
the repository's current documented baseline and current SDK surface. The
analysis does not assume that a V1.4 endpoint works on every NVR firmware.

Status meanings:

- `UNCHANGED`: the repository baseline and V1.4 describe the same relevant
  contract, or the V1.4 update history records no change to that area.
- `CHANGED`: V1.4 changes a documented contract or exposes a compatibility
  difference from the repository baseline.
- `NEW`: the V1.4 update history identifies a new interface, or V1.4 adds an
  interface absent from the repository baseline with sufficient version
  evidence.
- `REMOVED`: the V1.4 document removes an area that was in the baseline.
- `UNKNOWN / NOT ENOUGH EVIDENCE`: the PDF or repository baseline does not
  establish the introduction/removal history or an exact compatibility fact.

Current SDK support means implemented runtime behavior, not merely a capability
enum or a mention in an older document. Current real-device verification in the
repository predates this V1.4 review unless explicitly stated otherwise.

## Area classification

| API area | V1.0 -> V1.4 | V1.4 evidence | Current SDK status |
| --- | --- | --- | --- |
| Authentication/token flow | `CHANGED` | V1.1 changes the Digest response algorithm to SHA-256; V1.4 documents the token and refresh examples | Token acquisition and refresh exist; refresh Bearer behavior and SHA-256 compatibility are unit/contract tested, with real-NVR verification pending |
| Digest algorithm | `CHANGED` | V1.1 explicitly corrects the response algorithm to SHA-256; V1.4 challenge example says `algorithm="SHA-256"` | SHA-256 helper exists; device re-verification is pending |
| Module/capability discovery | `NEW` | V1.3 adds `GET /openapi/module_list` | Implemented as `CapabilityService.list_modules()`; unit/contract tested, real-NVR verification pending |
| Channel management | `CHANGED` | V1.3 updates add, remove, scan, and adds snapshot; V1.4 adds RTSP-device addition | `GET /openapi/added_devices` and current snapshot are implemented; other channel APIs remain deferred |
| Snapshot | `NEW` | V1.3 adds `GET /openapi/snapshot` with JPEG response | Implemented as in-memory `SnapshotImage.data`; unit/contract tested, real-NVR verification pending |
| RTSP-device add flow | `NEW` | V1.4 adds `POST /openapi/add_device_rtsp` | Not implemented |
| Recording search | `UNCHANGED` | V1.4 documents the same three read-only search endpoints and fields | Implemented and real-device verified for the repository's existing scope |
| Recording control | `NEW` | V1.2 adds `POST /openapi/record_control` | Not implemented |
| Video | `UNCHANGED` | No video change is listed in the V1.4 update history | Not implemented |
| Audio sound controls | `UNCHANGED` | Existing input/output sound GET and POST interfaces remain documented | Not implemented |
| Audio capability discovery | `NEW` | V1.4 adds channel and NVR audio capability GET interfaces | Not implemented |
| Disk | `UNCHANGED` | No disk change is listed in the V1.4 update history | Not implemented |
| PoE | `UNCHANGED` | No PoE change is listed in the V1.4 update history | Not implemented |
| Event server settings | `UNCHANGED` | GET/POST/delete server interfaces remain documented; the PDF has an example-path inconsistency | Not implemented |
| Event message subtype catalog | `CHANGED` | V1.1 and V1.3 update history add event subtypes | No event receiver or event model is implemented |
| Live RTSP | `UNCHANGED` | V1.4 retains the RTSP live URL and Digest-authenticated stream interface | No live URL or RTSP client implementation |
| Replay RTSP | `CHANGED` | V1.4 documents stream `1` or `2`; the repository helper enforces stream `1` | Replay URL helper exists for stream `1` only |
| Replay time semantics | `UNCHANGED` | V1.4 retains UTC `YYYYMMDDtHHMMSSz` query values | Explicit UTC strings are validated; record timestamps are not converted |
| PTZ | `NEW` | V1.3 adds the PTZ interface family | Not implemented |
| PTZ capability surface | `CHANGED` | V1.4 updates per-channel capability and adds the batch capability interface | Not implemented |
| Disarming and active defense | `UNKNOWN / NOT ENOUGH EVIDENCE` | V1.4 contains sections `4.12` and `4.13`, but its update history does not establish when they were introduced | Not implemented |
| Alarm output | `NEW` | V1.4 update history says to add the alarm-output interface and update alarm fields; section numbering is inconsistent | Not implemented |
| System control | `UNCHANGED` | `POST /openapi/systemctl` remains documented | Intentionally excluded from current SDK write scope |
| Removed APIs | `UNKNOWN / NOT ENOUGH EVIDENCE` | The V1.4 PDF does not provide a removal list | No removal claim is made |

All control-interface requests below are HTTPS JSON requests unless the row says
RTSP or event push. The V1.4 transaction section says every request takes a
token except token acquisition; this means Bearer authentication is expected
for the documented control calls, subject to real-device verification.

## Authentication and token compatibility

### `CHANGED` - `GET /openapi/token` and refresh

| Item | V1.4 contract and SDK comparison |
| --- | --- |
| Method and form | `GET /openapi/token`; initial no-auth request receives HTTP 401 and a Digest challenge. A second `GET` carries a Digest `Authorization` header. Refresh uses `GET /openapi/token?grant_type=refresh_token&refresh_token=...`. |
| Authentication | Initial challenge: no authentication. Token acquisition: Digest. Control requests: Bearer. The V1.4 refresh example also shows `Authorization: Bearer access_token`. |
| Key request fields | Digest `username`, `nonce`, `realm`, and `response`; refresh query fields `grant_type=refresh_token` and `refresh_token`. The PDF does not define an alternate token endpoint. |
| Key response fields | `token_type` (`bearer`), `expires_in` seconds, `access_token`, and `refresh_token`. The PDF says percent-encoded token JSON values must be decoded before putting the access token in a header. |
| Version evidence | V1.1 changes the response algorithm to SHA-256. The token path and token response are documented in the V1.4 revision. |
| Current SDK support | `AuthService` implements the two-step NVR token flow, parses/de-encodes tokens, stores the current access token, and sends the documented Bearer header for refresh when a token is supplied or retained. |
| Likely SDK impact | The minimal refresh-header correction and SHA-256 compatibility coverage are implemented. Preserve token parsing, refresh state, and redaction regressions while awaiting real-NVR verification. |
| State effect | Session-establishing/authentication operation; it does not change NVR configuration. |
| Real-device verification | Required against a V1.4-capable NVR, including initial challenge, refresh with the documented header, percent-encoded tokens, expiry, and error behavior. |

### Digest semantics: `CHANGED`

The V1.4 PDF explicitly states that the response uses SHA-256 and shows a
Digest challenge with `algorithm="SHA-256"`, realm `TP-LINK NVR`, nonce, and
`url="/openapi/token"`. It does not provide a full HA1/HA2 formula in the
reviewed authentication text. The current SDK calculates SHA-256 values for
`username:realm:password`, `METHOD:uri`, and the nonce combination in
`src/vigi/crypto.py`; that implementation must be verified against the V1.4
device rather than treated as newly established by this PDF alone.

## New and changed control interfaces

### `NEW` - `GET /openapi/module_list` (V1.3)

- Authentication: Bearer after token acquisition; no request parameters are
  documented.
- Response: `module_list` array of objects with `name` and numeric `version`,
  plus numeric `error_code`. The example names channel management, video, time,
  audio, disk, PoE, event, recording, system, PTZ, alarm device, active
  defense, and alarm output.
- Current SDK: `CapabilityService.list_modules()` is supported with typed
  module/version entries; unknown module names are preserved as strings and
  static capability metadata is not substituted for device discovery.
- Impact: the read-only discovery model is implemented without treating an
  advertised module as proof that every method works.
- Verification: real NVR required to compare module names/versions and endpoint
  reachability; this remains pending.

### `CHANGED` - channel management (V1.3) and `NEW` RTSP addition (V1.4)

| Interface | Request and response contract | Current SDK / impact | State and verification |
| --- | --- | --- | --- |
| `GET /openapi/added_devices` | No parameters. Response `devices[]` fields: `id`, `name`, `alias`, `online`, `ip`, `mac`; top-level `error_code`. | Already implemented as `DeviceService.list_added_devices()` with `id` mapped to `channel_id` and string `online` values. | Read-only; existing real-device verification should be retained and repeated for V1.4 if needed. |
| `POST /openapi/add_device` | JSON: `username`, `password`, `connect_prot` (`TP-LINK` or `ONVIF`), `ip`, `port`; response `error_code`. | Not implemented. Add-device credentials and protocol selection require a mutating service boundary. | Mutating; real NVR plus camera fixture required. Version V1.3. |
| `POST /openapi/remove_device` | JSON: `channel`; response `error_code`. | Not implemented. | Mutating; real-device verification required. Version V1.3. |
| `GET /openapi/device_scan` | No parameters. Response `devices[]` fields: `ip`, `name`, `connect_prot` (`TP-LINK`, `ONVIF`, or `RTSP`), `port`, `mac`, `model`; top-level `error_code`. | Not implemented. | Read-only but network/environment dependent; real-device verification required. Version V1.3. |
| `GET /openapi/snapshot` | Query `channel`; response is a JPEG file. No JSON field schema or content-type details beyond the JPEG response are established. | Implemented as `SnapshotService.get_snapshot(channel_id)` returning raw `SnapshotImage.data` bytes in memory. No file API or historical-frame model is added. | Read-only; unit/contract tested, but real NVR/channel verification remains required. Version V1.3. |
| `POST /openapi/add_device_rtsp` | JSON: `username`, `password`, `rtsp_url_main`; response `error_code`. The PDF explains the URL contains IP, RTSP port, and resource path. | Not implemented. | Mutating and credential-bearing; real NVR plus RTSP-device verification required. Version V1.4. |

### `NEW` - `POST /openapi/record_control` (V1.2)

- Authentication: Bearer control request.
- Request: JSON `channel` and `enable`, whose documented values are `auto` or
  `off`.
- Response: numeric `error_code`.
- Current SDK: recording search is implemented, but recording control is not.
- Impact: a separate explicitly mutating method; do not conflate it with the
  read-only search service.
- Verification: real NVR required; this changes recording behavior.

### `NEW` - audio capability discovery (V1.4)

| Interface | Contract | Current SDK / state |
| --- | --- | --- |
| `GET /openapi/audio/channel_capability` | Query `channel`; response `speaker_enable`, `microphone_enable` numeric `0` or `1`, plus `error_code`. | Not implemented. Read-only capability model; real camera/channel verification required. |
| `GET /openapi/audio/capability` | No parameters; response NVR-level `speaker_enable`, `microphone_enable` numeric `0` or `1`, plus `error_code`. | Not implemented. Read-only capability model; real NVR verification required. |

The existing audio input/output sound GET and POST interfaces remain documented
without a V1.4 update-history change. The GETs are read-only; the POSTs are
mutating. None are implemented by the current SDK.

### `CHANGED` - event protocol subtype catalog (V1.1 and V1.3)

- Protocol form: NVR pushes `POST /event_message` to a configured server as
  `multipart/form-data`; the JSON event part contains device identity and
  `messages[]` with `type`, `sub_type[]`, `localtime`, and optional channel,
  channel name, PoE port, disk, RAID, alarm output, or alarm input fields.
- Authentication: the PDF does not document authentication for the outbound
  event push; mark this unknown rather than assuming Bearer or Digest.
- Version evidence: V1.1 and V1.3 add event subtypes. The endpoint settings
  themselves remain the V1.0-style GET/POST/delete server operations.
- Current SDK: no event receiver, event server service, or subtype model.
- Impact: preserve the multipart boundary and optional JPEG distinction; map
  only subtypes established by a future reviewed appendix extraction.
- State and verification: inbound/outbound event handling is stateful and
  network-dependent; real NVR and an event receiver are required.

The PDF's event-server add example uses `POST /openapi/event_server/new_server`
while its method/path table says `POST /openapi/event_server`. This internal
inconsistency is recorded as a verification risk; no SDK path should be chosen
from the example alone.

### `NEW` / `CHANGED` - PTZ (V1.3 and V1.4)

All PTZ interfaces are Bearer-authenticated HTTPS JSON control requests. The
V1.4 document says `Version 1` for these interfaces.

| Interface | Key request fields | Key response fields | SDK status and operation |
| --- | --- | --- | --- |
| `GET /openapi/ptz/capability` | Query `channel`. | Per-channel `pan_tilt_supported`, `zoom_supported`, `preset_supported`, `preset_number_max`, `tour_number_max`, `pattern_number_max`, `aperture_supported`, `focus_supported`, `calibrate_supported`, `diagonal_motion_supported`; V1.4 example also includes tour/pattern flags and x/y/z/move/tour-stay ranges; `error_code`. | Not implemented. Read-only capability. V1.3 PTZ interface, changed in V1.4 with pan/tilt capability. |
| `POST /openapi/ptz/move` | JSON `channel`, numeric `direction`, string `speed`. | `error_code`. | Not implemented. Mutating movement; V1.3; real device required. |
| `GET /openapi/ptz/park` | Query `channel`. | `action_mode`, `park_time`, `action_id`, `enabled`, `error_code`. | Not implemented. Read-only; V1.3; real device required. |
| `POST /openapi/ptz/park` | JSON `channel`, `action_mode` (`preset` or `tour`), `park_time`, `action_id`, `enabled` (`0` or `1`). | `error_code`. | Not implemented. Mutating; V1.3; real device required. |
| `GET /openapi/ptz/preset` | Query `channel`. | `preset[]` with `preset_id`, `read_only`, `name`; `error_code`. | Not implemented. Read-only; V1.3; real device required. |
| `GET /openapi/ptz/tour` | Query `channel`. | `tour[]` with `tour_id`, `preset_count`, `name`, `preset_id[]`, `time[]`, `speed[]`; `error_code`. | Not implemented. Read-only; V1.3; real device required. |
| `GET /openapi/ptz/target_track` | Query `channel`. | `enabled`, `people_enabled` (`on` or `off`), `error_code`. | Not implemented. Read-only; V1.3; real device required. |
| `POST /openapi/ptz/target_track` | JSON `channel`, `enabled`, `people_enabled` (`on` or `off`). | `error_code`. | Not implemented. Mutating; V1.3; real device required. |
| `GET /openapi/ptz/batch_capability` | No parameters. | `capability[]` keyed by `id`; fields include pan/tilt, zoom, preset, tour, pattern, aperture, focus, calibration, diagonal-motion flags, numeric maxima/ranges, and tour-stay limits; `error_code`. | Not implemented. Read-only capability; V1.4; real NVR verification required. |

The PDF does not establish a safe generic PTZ direction enum beyond the numeric
`direction` field, so an implementation must not invent one.

### `NEW` with ambiguity - alarm output (V1.4)

The V1.4 update history says "Add 4.15 Alarm Output Interface" and separately
says to update `4.14.1` and `4.14.2` with `alarm_type`. The body places alarm
output under `4.14` and the directory numbering does not match the update note.
The following is therefore mapped to V1.4 with the numbering ambiguity retained.

| Interface | Key request/response fields | Current SDK / operation |
| --- | --- | --- |
| `GET /openapi/alarm_output/nvr_alarm` | No request fields. Response `alarm_output_info[]` with `device_id`, `delay_time` (`5`, `10`, `30`, `60`, `120`, `300`, `600` seconds), `enabled` (`on`/`off`), `alarm_name`, and V1.4 `alarm_type` (`NO`/`NC`); `error_code`. | Not implemented. Read-only; real NVR verification required. |
| `POST /openapi/alarm_output/nvr_alarm` | JSON `device_id`, `alarm_name`, `delay_time`, `enabled`, `alarm_type`; response `error_code`. | Not implemented. Mutating output configuration; real NVR required. |
| `GET /openapi/alarm_output/ipc_alarm` | Query `channel`; response `alarm_name`, `delay_time`, `enabled`, `error_code`. | Not implemented. Read-only; real channel required. |
| `POST /openapi/alarm_output/ipc_alarm` | JSON `channel`, `alarm_name`, `delay_time`, `enabled`; response `error_code`. | Not implemented. Mutating; real device required. |
| `POST /openapi/alarm_output/nvr_manual_alarm` | JSON `device_id`, `action` (`start` or `stop`); response `timer`, `error_code`. | Not implemented. Mutating/physical output; real NVR required. |
| `POST /openapi/alarm_output/ipc_manual_alarm` | JSON `channel`, `action` (`start` or `stop`); response `timer`, `error_code`. | Not implemented. Mutating/physical output; real device required. |
| `GET /openapi/alarm_output/batch_get_ipc_alarm` | No request fields. Response `alarm_output[]` with `channel`, `alarm_name`, `delay_time`, `enabled`, `manual_alarm_out_supported`; `error_code`. | Not implemented. Read-only capability/configuration; real NVR required. |

### `UNKNOWN / NOT ENOUGH EVIDENCE` - disarming and active defense

V1.4 documents these interfaces, but its update history does not say whether
they were introduced in V1.0, V1.1, V1.2, V1.3, or V1.4, and the repository's
V1.0 scope did not register them. They must remain explicitly unmapped rather
than being called V1.4 additions:

- `GET`/`POST /openapi/alarm_device/alarm_mode`: `device_id` and
  `alarm_mode` (`alarm`/`disarming`); POST mutates state.
- `GET`/`POST /openapi/active_defense/arm_status`: `channel` and
  `arm_status`; POST mutates state.

The PDF documents these as Bearer-authenticated control calls, but the SDK does
not implement them and real-device verification is required.

## Unchanged or not-yet-implemented areas

These areas have no V1.4 update-history change relevant to the current baseline.
They remain documented contracts, not SDK support claims:

- **Video (`UNCHANGED`)**: GET/POST resolution and bitrate interfaces under
  `/openapi/resolution`, `/openapi/valid_resolutions`, `/openapi/bitrate`, and
  `/openapi/bitrate_capability`. GETs are read-only; POSTs mutate channel
  settings. The SDK implements none of them.
- **Audio sound (`UNCHANGED`)**: GET/POST input and output sound interfaces.
  GETs are read-only; POSTs mutate audio settings. The SDK implements none.
- **Disk (`UNCHANGED`)**: GET `/openapi/disks`, GET
  `/openapi/esata_disks`, POST/GET SMART-process interfaces. Disk reads are
  read-only; SMART process start/stop and SMART tests are mutating or
  hardware-affecting. The SDK implements none.
- **PoE (`UNCHANGED`)**: GET/POST `/openapi/poe/info`, GET/POST
  `/openapi/poe/link_mode`, and GET `/openapi/poe/status` and
  `/openapi/poe/link_status`. GETs are read-only; POSTs change power/link
  settings. The SDK implements none.
- **Recording search (`UNCHANGED`)**: GET `/openapi/record/days`, GET
  `/openapi/record/search/free_process`, and GET
  `/openapi/record/search/results`; current `RecordService` supports the
  documented query and response fields only.
- **System control (`UNCHANGED`)**: POST `/openapi/systemctl` with `action`
  `reset` or `reboot`, returning `error_code`. It is mutating and excluded from
  current SDK scope.

## RTSP live, replay, and time semantics

### `UNCHANGED` protocol with a `CHANGED` stream-selector compatibility point

The V1.4 stream interface is RTSP over TCP or UDP. It documents live and replay
methods, Digest authentication, and these URL forms:

- Live: `rtsp://<IP>/live/<channel>/<stream>/avm`
- Replay: `rtsp://<IP>/replay/<channel>/<stream>/avm?starttime=<starttime>&endtime=<endtime>`

V1.4 says `stream` is `1` or `2` (`1` main, `2` minor). Replay times are UTC
strings in `YYYYMMDDtHHMMSSz`; the `z` is the zero-UTC-offset designator.

For the changed replay selector, the documented protocol form is RTSP
`DESCRIBE`/`SETUP`/`PLAY` and related methods against the live or replay URL;
authentication is RTSP Digest, not the HTTPS Bearer token. The URL inputs are
NVR IP, channel, stream, and, for replay, `starttime` and `endtime`. The update
history does not establish when stream `2` became available, so its exact
introduction version is `UNKNOWN / NOT ENOUGH EVIDENCE`. The operation is
stream playback (read-only from the NVR configuration perspective), but a full
RTSP client and real-device verification are still required.

The current SDK only builds replay URLs, forces stream `1`, and does not open
RTSP or perform the RTSP Digest handshake. It has no live URL builder. The V1.4
stream `2` documentation is therefore a compatibility gap to verify and plan,
not permission to change the runtime in this documentation task.

The V1.4 `talk` section documents an audio session command and raw G.711
mu-law audio over an RTSP interleaved TCP channel. It is not part of the current
SDK and requires real-device and protocol-level verification.

## Next implementation boundary

The first read-only implementation increment is complete at the unit/contract
level:

1. The auth layer now sends the documented refresh Bearer header and retains
   the current access token; SHA-256 and refresh regressions are covered.
2. Module/capability discovery is implemented only from the documented
   module-list contract, with unknown modules tolerated and no implied endpoint
   support.
3. Snapshot is implemented only as an in-memory JPEG response; no file or
   historical-image model is added.
4. Preserve regression coverage for token acquisition, refresh, `added_devices`,
   recording search, replay URL construction, and existing RTSP/replay
   validation.

Real-NVR verification of this increment remains the next boundary. Mutating,
hardware-dependent, and broader V1.4 API families remain deferred.

Later, separately gated work may cover recording control, add/remove devices,
RTSP-device addition, PTZ movement/control, audio writes, alarm/output writes,
system control, and other state-changing or hardware-dependent APIs. No API in
those later groups is implemented by this task.

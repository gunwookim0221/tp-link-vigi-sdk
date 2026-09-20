# VIGI NVR OpenAPI V1.4 Compatibility Verification

Verification date: `2026-09-20`

This report records a read-only verification run against the configured real
NVR using the repository's existing `.env` configuration. Secrets, host data,
tokens, RTSP credentials, and device identifiers are intentionally omitted.
The target model and firmware were not safely discoverable through the existing
SDK responses or configuration metadata. The official applicability entry for
`VIGI NVR1008H-8P (V1.20)` remains a documentation reference, not a claim about
the redacted verification target.

The authoritative contract source was the local official
[VIGI NVR Open API V1.4 PDF](nvr-openapi-v1.4-reference.md). The verification
used only authenticated GET/read flows, the existing recording-search tests,
and the opt-in sanitized harness in
[`tests/test_integration_v14_readonly.py`](../../tests/test_integration_v14_readonly.py).

## Results

| API group / operation | Result | Verification scope | Evidence and limitation |
| --- | --- | --- | --- |
| Initial Digest-to-Bearer authentication | PASS | NVR-verified | Token acquisition and an authenticated request succeeded; token values were not printed. |
| Refresh-token flow | UNSUPPORTED | NVR-verified | The NVR returned the SDK's API-error path; no refresh token or response body was exposed. |
| Module discovery | PASS | NVR-verified | `module_list` parsed successfully with 12 entries; names and numeric versions were retained without capability inference. |
| Snapshot | PASS | NVR-verified | One existing channel returned non-empty JPEG bytes accepted by the SDK parser. No image was persisted. |
| Added-device inventory | PASS | NVR-verified | `added_devices` parsed successfully with 3 entries; identifiers and addresses were not published. |
| Recording search | PASS | NVR-verified | Existing read-only record-days, free-process, and results integration test passed. |
| Live RTSP URL construction | PASS | Contract/SDK verified only | Main and minor URL builders succeeded. The SDK has no RTSP client/open check, so no NVR stream connection was attempted. |
| Replay RTSP URL construction | PASS | Contract/SDK verified only | Replay URL construction and configured UTC time formatting succeeded. No replay connection or media operation was attempted. |
| PTZ per-channel capability | UNSUPPORTED | NVR-verified | The endpoint returned the SDK API-error path for the selected channel. |
| PTZ batch capability | FAIL (DOCUMENTATION_DEVICE_DEVIATION) | NVR-verified | HTTP succeeded, but each returned entry exposed only `id` and `pan_tilt_supported`; the V1.4 contract documents additional fields, so the strict parser correctly rejected the response. |
| Audio NVR/channel capability and input/output reads | PASS | NVR-verified | NVR capability, channel capability, output sound, and input sound read calls all parsed successfully. |
| NVR alarm-output read | UNSUPPORTED | NVR-verified | The endpoint returned the SDK API-error path. |
| IPC alarm-output read | UNSUPPORTED | NVR-verified | The selected-channel endpoint returned the SDK API-error path. |
| Batch IPC alarm-output read | PASS | NVR-verified | Batch response parsed successfully. |

`UNSUPPORTED` above means the documented call reached the NVR but returned the
SDK's API-error result; it is not a claim that every firmware version rejects
the endpoint. The PTZ batch result is classified as
`DOCUMENTATION_DEVICE_DEVIATION`, not an SDK parser defect: the device omitted
documented fields without a documented partial-item representation. No runtime
change was made; the parser remains contract-safe and rejects the deviation.

## PTZ batch RCA

The authoritative V1.4 section `4.11.9` documents `GET
/openapi/ptz/batch_capability` with no request fields. The top-level response is
a `capability` array plus numeric `error_code`. The documented per-item fields
include `id`, `pan_tilt_supported`, `zoom_supported`, `preset_supported`,
`preset_number_max`, `tour_number_max`, `pattern_number_max`,
`aperture_supported`, `focus_supported`, `calibrate_supported`, and
`diagonal_motion_supported`; the example also contains tour/pattern flags and
numeric range/stay-time fields. The PDF does not state that these fields are
optional, permit omitted fields for unsupported channels, or define a partial
item schema.

The sanitized live response was: HTTP `200`; top-level keys
`capability`/`error_code`; `error_code` type integer; 8 capability items; every
item had only `id` (integer) and `pan_tilt_supported` (string), with the
observed flag value `"0"`. Because this is materially outside the documented
shape, the RCA classification is **DOCUMENTATION_DEVICE_DEVIATION**.

The focused regression test preserves this boundary: fully populated and empty
documented batch responses continue to parse, while the observed partial item
continues to raise a response-shape error. The final PTZ batch status is
therefore vendor-deviation / not fully verified, rather than silently accepting
undocumented data.

## Explicit verification boundary

The following were intentionally not exercised against hardware:

- recording-control writes; device scan/add/remove/add-RTSP operations;
- PTZ movement, park writes, tracking writes, or any preset/tour mutation;
- audio input/output writes;
- alarm configuration or manual start/stop control;
- system, reboot, disk, PoE, video-setting, time/NTP, and event-server writes;
- RTSP live/replay opening, authentication, media export, or download.

Preset/tour listings, PTZ park reads, and target-tracking reads were also not
called because this phase restricted PTZ verification to capability endpoints.
They remain contract-tested only. No device-level verification is claimed for
any camera based solely on NVR inventory or NVR-side capability responses.

## Validation

The existing authentication, inventory, and recording integration tests plus
the read-only V1.4 harness completed with `4 passed`. The focused PTZ Phase 3B
tests also pass. The harness reported the statuses above and emitted no secret
values. The only pytest warning was a pre-existing inability to write
`.pytest_cache` in the workspace; it did not affect test execution.

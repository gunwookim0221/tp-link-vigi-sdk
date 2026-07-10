# Limitations

## Current Known Limitations

- The SDK builds documented RTSP replay URLs only; it does not open, play, authenticate to, download from, or save RTSP streams.
- RTSP Digest handshake, ffmpeg integration, export/download endpoints, and video-file handling are unsupported.
- NVR device inventory is implemented and verified for the documented `GET /openapi/added_devices` schema.
- Phase 7 recording search is implemented and verified for the documented read-only search endpoints and does not retrieve, export, download, or store video files.
- Recording result `start_time` and `end_time` values are preserved as raw timestamp strings because the official recording search schema does not define a timezone conversion rule for those fields.
- `RecordSegment.start_time` and `end_time` are not automatically converted to replay URL times; callers must provide explicit UTC `YYYYMMDDtHHMMSSz` strings to the replay URL helper.
- Recording search models do not include fields that are absent from the official schema, such as recording ID, segment ID, file ID, size, duration, or record type.
- Firmware version for the MVP device is TODO.
- Snapshot is unsupported under the current official NVR OpenAPI V1.0 and IPC OpenAPI V1.1 documentation: no NVR snapshot endpoint or IPC snapshot method is documented.
- The supplied examples are opt-in scripts, not a CLI, and require explicit shell environment configuration; `.env` is not auto-loaded.
- Replay URL examples require caller-provided UTC time strings and do not convert `RecordSegment` timestamps.
- The project has not selected a license yet.
- C340I OpenAPI support is indicated by official firmware release notes and the device Web UI exposes an OpenAPI setting. IPC `doAuth` and post-auth read-only `getStreamPort` are manually verified, but SDK support is not implemented.
- Standalone VIGI Camera public SDK APIs are not exposed yet.

## OpenAPI Limitations From Official References

- OpenAPI must be enabled in the NVR web interface before use.
- The NVR OpenAPI guide documents the default OpenAPI control port as `20443`; deployments may change this port.
- The NVR control interface requests are HTTPS only.
- NVR control requests require Bearer token authentication except token acquisition.
- The NVR official stream interface is RTSP, not an HTTPS JSON endpoint.
- `VIGI IPC OpenAPI Document_V1.1` documents IPC control requests as HTTPS `POST https://device_addr:port/stok=xx` with JSON method payloads.
- The IPC control port is obtained through ODP and defaults to `20443`.
- IPC discovery uses ODP local service port `23001` and Ethernet protocol type `0x7210`.
- IPC stream requests are RTSP-style `MULTITRANS` requests and stream data uses RTP over TCP.
- RTSP replay URL documentation says replay only supports stream `1` now.
- Recording search provides time ranges that may later be used for replay planning, but the replay stream itself is RTSP and is outside Phase 7.
- Supported products and firmware requirements may change.

## Firmware Dependency

Fact:

- The official OpenAPI guide says the NVR firmware must support OpenAPI.
- The supported products page says latest firmware should be installed.
- TP-Link firmware release notes indicate `VIGI C340I(UN) V1.20 2.2.0 Build 250926` added support for `VIGI OpenAPI`.
- The official C340I download page lists a standalone `VIGI IPC OpenAPI Document_V1.1`.

TODO:

- Record exact firmware version used for MVP validation.
- Implement no IPC SDK behavior until ADR-0006 architecture work is explicitly planned.
- Record firmware-specific deviations if discovered during integration testing.

## Unsupported Features

Currently unsupported:

- GUI automation.
- Undocumented web UI endpoints.
- NVR or IPC snapshot implementation until TP-Link publishes an official request and response contract.
- RTSP frame capture as a substitute for a snapshot API.
- ffmpeg integration, image processing, and snapshot file saving.
- Private or undocumented snapshot URL usage.
- CLI support; it remains deferred to a separate phase.
- Mutating device settings in MVP.
- Event receiver service implementation.
- Full RTSP client implementation.
- Camera-specific public SDK APIs.
- Direct standalone camera snapshot.
- Direct standalone camera stream handling as an OpenAPI control API.
- Direct standalone camera settings APIs.

## Standalone Camera Limitations

Standalone VIGI Camera support is outside the current MVP.

Fact:

- The current MVP is NVR-first and targets VIGI NVR OpenAPI plus NVR-managed channels/cameras.
- VIGI C340I OpenAPI support is indicated by official firmware release notes for `V1.20` firmware `2.2.0 Build 250926`.

Current limits:

- This project treats C340I as an integration verification target for IPC auth/transport architecture, not as a supported public SDK device.
- `VIGI IPC OpenAPI Document_V1.1` does not document IPC control authentication as `GET /openapi/token`.
- Real-device verification currently shows that the NVR endpoint `GET /openapi/token` on port `20443` does not return the expected HTTP/1.1 `401` Digest challenge.
- `curl` reported an HTTP/0.9-like response from `https://192.168.1.213:20443/openapi/token`; Postman reported a malformed response parse error.
- This malformed response is plausibly explained by an IPC control request-format mismatch, because the IPC document expects HTTPS POST JSON `doAuth` or `stok` control requests rather than an NVR REST-style token path.
- The malformed response is not evidence of successful authentication and must not be used as an SDK behavior contract.
- Camera-specific public SDK APIs are not exposed yet.
- Standalone camera endpoint coverage remains limited to officially documented behavior and verified device observations.
- RTSP/ONVIF access is verified separately from HTTPS OpenAPI control APIs.
- The existing NVR `AuthService` `/openapi/token` flow is not directly reusable for IPC control authentication.
- Low-level HTTPS request handling, SHA-256 digest helpers, TLS options, error handling, and log redaction may be reusable, but IPC needs a separate protocol/auth review before implementation.
- IPC `doAuth` Step 2 has issued a `stok` on the real C340I using the documented `params.nonce` and `params.response` schema; the token value must remain redacted.
- Official IPC `getStreamPort`, called as `POST https://device_addr:20443/stok=<stok>` with body `{"method":"getStreamPort"}`, returned `result.streamPort: "554"` and `errCode: 0` on the real C340I.
- Until ADR-0006 architecture work is implemented, camera-specific SDK APIs remain unsupported.
- Public camera SDK APIs must not be added until official documentation, verification records, and an ADR justify the scope expansion.
- IPC-specific transport/auth separation is recorded in [ADR-0006](adr/ADR-0006-separate-nvr-and-ipc-auth-transports.md). Adding public camera support may still require another ADR if it changes the public client architecture.

## Assumptions To Validate

- `VIGI NVR1008H-8P` exposes all MVP endpoints after OpenAPI is enabled.
- Token refresh behavior follows the official reference on target firmware.
- `GET /openapi/added_devices` response fields match the official schema on target firmware.
- The ADR-0006 IPC auth/transport separation can be implemented without exposing public camera SDK APIs.

## Related Documents

- [02-references.md](02-references.md)
- [03-api-scope.md](03-api-scope.md)
- [05-test-strategy.md](05-test-strategy.md)
- [06-device-matrix.md](06-device-matrix.md)
- [11-roadmap.md](11-roadmap.md)

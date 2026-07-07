# Limitations

## Current Known Limitations

- No SDK code exists yet.
- No real `VIGI NVR1008H-8P` verification has been recorded yet.
- Firmware version for the MVP device is TODO.
- Snapshot support is TODO because no snapshot endpoint was identified in the official OpenAPI reference PDF during Phase 0.
- The project has not selected a license yet.
- Standalone VIGI Camera APIs are not verified.

## OpenAPI Limitations From Official References

- OpenAPI must be enabled in the NVR web interface before use.
- The official guide documents the default OpenAPI port as `20443`; deployments may change this port.
- Control interface requests are HTTPS only.
- Control requests require Bearer token authentication except token acquisition.
- The official stream interface is RTSP, not an HTTPS JSON endpoint.
- RTSP replay URL documentation says replay only supports stream `1` now.
- Supported products and firmware requirements may change.

## Firmware Dependency

Fact:

- The official OpenAPI guide says the NVR firmware must support OpenAPI.
- The supported products page says latest firmware should be installed.

TODO:

- Record exact firmware version used for MVP validation.
- Record firmware-specific deviations if discovered during integration testing.

## Unsupported Features

Currently unsupported:

- GUI automation.
- Undocumented web UI endpoints.
- Snapshot endpoint implementation.
- Mutating device settings in MVP.
- Event receiver service implementation.
- Full RTSP client implementation.
- Direct standalone camera login.
- Direct standalone camera snapshot.
- Direct standalone camera stream handling.
- Direct standalone camera settings APIs.

## Standalone Camera Limitations

Standalone VIGI Camera support is outside the current MVP.

Fact:

- The current MVP is NVR-first and targets VIGI NVR OpenAPI plus NVR-managed channels/cameras.

Current limits:

- Standalone camera APIs have not been verified by this project.
- Direct camera login, snapshot, stream, and settings workflows are out of scope for the current MVP.
- Public camera SDK APIs must not be added until a physical standalone VIGI camera is available for integration testing.
- Adding camera support requires a new ADR, such as `ADR-0006 Split NVR and Camera Clients`.

## Assumptions To Validate

- `VIGI NVR1008H-8P` exposes all MVP endpoints after OpenAPI is enabled.
- Token refresh behavior follows the official reference on target firmware.
- `GET /openapi/added_devices` response fields match the official schema on target firmware.

## Related Documents

- [02-references.md](02-references.md)
- [03-api-scope.md](03-api-scope.md)
- [05-test-strategy.md](05-test-strategy.md)
- [06-device-matrix.md](06-device-matrix.md)
- [11-roadmap.md](11-roadmap.md)

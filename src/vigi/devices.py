"""Device service placeholders."""

from vigi.models import DeviceInfo


class DeviceService:
    """Placeholder for documented device/channel inventory APIs."""

    def list_added_devices(self) -> list[DeviceInfo]:
        """List devices through a future documented OpenAPI implementation."""

        raise NotImplementedError("Device inventory is planned for Phase 3.")

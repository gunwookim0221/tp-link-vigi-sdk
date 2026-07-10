"""List NVR-managed devices after explicit login."""

import os

from vigi import AuthConfig, VigiClient, VigiError


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def _verify_tls() -> bool:
    return os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}


def main() -> None:
    """Authenticate and print non-sensitive device inventory fields."""

    client = VigiClient(
        AuthConfig(
            host=_required_env("VIGI_HOST"),
            port=int(os.getenv("VIGI_PORT", "20443")),
            username=_required_env("VIGI_USERNAME"),
            password=_required_env("VIGI_PASSWORD"),
            verify_tls=_verify_tls(),
        )
    )
    try:
        client.login()
        response = client.devices.list_added_devices()
    except VigiError as error:
        print(f"Device inventory request failed: {error}")
        return

    if not response.devices:
        print("No NVR-managed devices were returned.")
        return

    for device in response.devices:
        print(
            f"channel={device.channel_id} name={device.name!r} "
            f"alias={device.alias!r} status={device.online.value}"
        )


if __name__ == "__main__":
    main()

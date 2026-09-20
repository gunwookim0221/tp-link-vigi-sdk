"""Opt-in, read-only V1.4 compatibility checks for a configured NVR.

This test deliberately reports only sanitized status labels and aggregate counts.
It must be run with the existing NVR environment variables in the process; the
repository does not load ``.env`` automatically.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest

from vigi import AuthConfig, VigiClient
from vigi.exceptions import (
    AuthenticationError,
    CapabilityError,
    ConnectionError,
    TimeoutError,
    TransportError,
    VigiApiError,
    VigiResponseError,
)
from vigi.types import StreamType


def _integration_config_available() -> bool:
    return all(os.getenv(name) for name in ("VIGI_HOST", "VIGI_USERNAME", "VIGI_PASSWORD"))


def _build_client() -> VigiClient:
    verify_ssl = os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}
    port = int(os.getenv("VIGI_PORT", "20443"))
    return VigiClient(
        AuthConfig(
            host=os.environ["VIGI_HOST"],
            username=os.environ["VIGI_USERNAME"],
            password=os.environ["VIGI_PASSWORD"],
            port=port,
            verify_tls=verify_ssl,
        )
    )


def _failure_status(exc: BaseException) -> str:
    if isinstance(exc, (VigiApiError, CapabilityError)):
        return "UNSUPPORTED"
    if isinstance(exc, VigiResponseError):
        return "FAIL(response-shape)"
    if isinstance(exc, (ConnectionError, TimeoutError, TransportError)):
        return "FAIL(transport)"
    if isinstance(exc, AuthenticationError):
        return "FAIL(authentication)"
    return "FAIL"


def _report(name: str, status: str, detail: str = "") -> None:
    suffix = f" {detail}" if detail else ""
    print(f"PHASE4 {name} {status}{suffix}")


def _call(name: str, operation: Callable[[], Any]) -> Any | None:
    try:
        result = operation()
    except Exception as exc:  # noqa: BLE001 - classify without exposing exception text.
        _report(name, _failure_status(exc), type(exc).__name__)
        return None
    _report(name, "PASS")
    return result


@pytest.mark.skipif(
    not _integration_config_available(),
    reason="VIGI NVR integration environment is not configured.",
)
def test_integration_v14_readonly_compatibility() -> None:
    client = _build_client()

    try:
        client.login()
    except Exception as exc:  # noqa: BLE001 - do not print authentication details.
        _report("authentication", _failure_status(exc), type(exc).__name__)
        pytest.fail("VIGI NVR authentication failed; see the sanitized status above.")
    _report("authentication", "PASS")

    session_info = client.session.info
    refresh_token = session_info.refresh_token
    access_token = session_info.access_token
    if refresh_token and access_token:
        refreshed = _call(
            "authentication_refresh",
            lambda: client.auth.refresh(
                refresh_token,
                transport=client.transport,
                access_token=access_token,
            ),
        )
        if refreshed is not None:
            assert refreshed.session_info.authenticated is True
            assert refreshed.session_info.access_token
    else:
        _report("authentication_refresh", "NOT_TESTED", "no_refresh_token")

    modules = _call("module_discovery", client.capabilities.list_modules)
    if modules is not None:
        assert modules.error_code == 0
        assert all(module.name and isinstance(module.version, int) for module in modules.modules)
        _report("module_discovery_shape", "PASS", f"count={len(modules.modules)}")

    inventory = _call("added_devices", client.devices.list_added_devices)
    channel_id: int | None = None
    if inventory is not None:
        assert inventory.error_code == 0
        assert isinstance(inventory.devices, tuple)
        for device in inventory.devices:
            assert device.channel_id > 0
            assert device.name is not None
            assert device.alias is not None
        _report("added_devices_shape", "PASS", f"count={len(inventory.devices)}")
        if inventory.devices:
            channel_id = inventory.devices[0].channel_id
    if channel_id is None:
        _report("channel_dependent_read_only", "NOT_TESTED", "no_added_channel")

    if channel_id is not None:
        snapshot = _call("snapshot", lambda: client.snapshots.get_snapshot(channel_id))
        if snapshot is not None:
            assert snapshot.data.startswith(b"\xff\xd8")
            assert snapshot.data.endswith(b"\xff\xd9")
            assert snapshot.data
            _report("snapshot_shape", "PASS", f"bytes={len(snapshot.data)}")

        _call("ptz_capability", lambda: client.ptz.get_capability(channel_id))
        _call("audio_channel_capability", lambda: client.audio.get_channel_capability(channel_id))
        _call("audio_output_read", lambda: client.audio.get_output_sound(channel_id))
        _call("audio_input_read", lambda: client.audio.get_input_sound(channel_id))
        _call("alarm_ipc_read", lambda: client.alarm_outputs.get_ipc_alarm(channel_id))

        start_time = os.getenv("VIGI_REPLAY_START_TIME")
        end_time = os.getenv("VIGI_REPLAY_END_TIME")
        recording_day = os.getenv("VIGI_RECORDING_DAY")
        if not (start_time and end_time) and recording_day:
            start_time = f"{recording_day}t000000z"
            end_time = f"{recording_day}t235959z"
        if start_time and end_time:
            try:
                client.stream.build_replay_url(
                    client.auth_config.host,
                    channel_id,
                    start_time,
                    end_time,
                )
            except Exception as exc:  # noqa: BLE001 - sanitized status only.
                _report("replay_rtsp_url", _failure_status(exc), type(exc).__name__)
            else:
                _report("replay_rtsp_url", "PASS", "construction_only")
        else:
            _report("replay_rtsp_url", "NOT_TESTED", "replay_times_unconfigured")

        try:
            client.stream.build_live_url(client.auth_config.host, channel_id, StreamType.MAIN)
            client.stream.build_live_url(client.auth_config.host, channel_id, StreamType.MINOR)
        except Exception as exc:  # noqa: BLE001 - sanitized status only.
            _report("live_rtsp_url", _failure_status(exc), type(exc).__name__)
        else:
            _report("live_rtsp_url", "PASS", "construction_only")

    _call("ptz_batch_capability", client.ptz.get_batch_capability)
    _call("audio_capability", client.audio.get_capability)
    _call("alarm_nvr_read", client.alarm_outputs.get_nvr_alarm)
    _call("alarm_batch_ipc_read", client.alarm_outputs.get_batch_ipc_alarm)

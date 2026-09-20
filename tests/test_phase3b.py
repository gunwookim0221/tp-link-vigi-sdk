import json

import pytest

from vigi import (
    AlarmAction,
    AlarmDelayTime,
    AlarmEnabled,
    AlarmType,
    AudioToggle,
    AuthConfig,
    AuthMode,
    PtzParkActionMode,
    PtzTargetTrackMode,
    SessionInfo,
    VigiClient,
)
from vigi.alarm import (
    BATCH_IPC_ALARM_PATH,
    IPC_ALARM_PATH,
    IPC_MANUAL_ALARM_PATH,
    NVR_ALARM_PATH,
    NVR_MANUAL_ALARM_PATH,
    build_batch_ipc_alarm_request,
    build_ipc_alarm_get_request,
    build_ipc_alarm_set_request,
    build_ipc_manual_alarm_request,
    build_nvr_alarm_get_request,
    build_nvr_alarm_set_request,
    build_nvr_manual_alarm_request,
    parse_batch_ipc_alarm_response,
    parse_alarm_manual_response,
    parse_ipc_alarm_response,
    parse_nvr_alarm_response,
)
from vigi.audio import (
    AUDIO_CAPABILITY_PATH,
    AUDIO_CHANNEL_CAPABILITY_PATH,
    AUDIO_INPUT_SOUND_PATH,
    AUDIO_OUTPUT_SOUND_PATH,
    build_audio_capability_request,
    build_audio_channel_capability_request,
    build_audio_input_sound_get_request,
    build_audio_input_sound_set_request,
    build_audio_output_sound_get_request,
    build_audio_output_sound_set_request,
    parse_audio_capability_response,
    parse_audio_channel_capability_response,
    parse_audio_control_response,
    parse_audio_input_sound_response,
    parse_audio_output_sound_response,
)
from vigi.exceptions import AuthenticationError, ValidationError, VigiApiError, VigiResponseError
from vigi.ptz import (
    PTZ_BATCH_CAPABILITY_PATH,
    PTZ_CAPABILITY_PATH,
    PTZ_MOVE_PATH,
    PTZ_PARK_PATH,
    PTZ_PRESET_PATH,
    PTZ_TARGET_TRACK_PATH,
    PTZ_TOUR_PATH,
    build_ptz_batch_capability_request,
    build_ptz_capability_request,
    build_ptz_move_request,
    build_ptz_park_get_request,
    build_ptz_park_set_request,
    build_ptz_preset_request,
    build_ptz_target_track_get_request,
    build_ptz_target_track_set_request,
    build_ptz_tour_request,
    parse_ptz_batch_capability_response,
    parse_ptz_capability_response,
    parse_ptz_preset_response,
    parse_ptz_park_response,
    parse_ptz_tour_response,
    parse_target_tracking_response,
)
from vigi.transport import Request, Response, Transport, TransportConfig


class FakeTransport(Transport):
    def __init__(self, responses: list[Response]) -> None:
        super().__init__(TransportConfig(base_url="https://nvr.local:20443"))
        self.responses = responses
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return self.responses.pop(0)


def _bearer_client(responses: list[Response]) -> tuple[VigiClient, FakeTransport]:
    transport = FakeTransport(responses)
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )
    client.session.info = SessionInfo(
        authenticated=True,
        auth_mode=AuthMode.BEARER,
        token_type="bearer",
        access_token="secret-token",
    )
    return client, transport


def _ptz_capability_payload(**overrides: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "pan_tilt_supported": "1",
        "zoom_supported": "0",
        "preset_supported": "1",
        "preset_number_max": "300",
        "tour_number_max": "8",
        "pattern_number_max": "4",
        "tour_spots_number_max": "8",
        "tour_supported": "1",
        "pattern_supported": "0",
        "aperture_supported": "0",
        "focus_supported": "0",
        "calibrate_supported": "1",
        "diagonal_motion_supported": "0",
        "x_min": "-1.000000",
        "x_max": "1.000000",
        "y_min": "-1.000000",
        "y_max": "1.000000",
        "z_min": "0.000000",
        "z_max": "0.000000",
        "move_min": "0.000000",
        "move_max": "0.000000",
        "tour_stay_time_max": "3600000",
        "tour_stay_time_min": "60000",
        "error_code": 0,
    }
    payload.update(overrides)
    return payload


def test_ptz_request_builders_use_documented_paths_and_payloads() -> None:
    headers = {"Authorization": "Bearer secret-token"}

    assert (
        build_ptz_capability_request(headers, channel_id=2).path
        == f"{PTZ_CAPABILITY_PATH}?channel=2"
    )
    assert build_ptz_batch_capability_request(headers).path == PTZ_BATCH_CAPABILITY_PATH
    move = build_ptz_move_request(headers, channel_id=2, direction=0, speed="0.6")
    assert move.path == PTZ_MOVE_PATH
    assert json.loads(move.body or b"") == {"channel": 2, "direction": 0, "speed": "0.6"}
    park_get = build_ptz_park_get_request(headers, channel_id=2)
    assert park_get.path == f"{PTZ_PARK_PATH}?channel=2"
    park_set = build_ptz_park_set_request(
        headers,
        channel_id=2,
        action_mode=PtzParkActionMode.TOUR,
        park_time=6,
        action_id=2,
        enabled=1,
    )
    assert json.loads(park_set.body or b"") == {
        "action_mode": "tour",
        "park_time": 6,
        "action_id": 2,
        "enabled": 1,
        "channel": 2,
    }
    assert build_ptz_preset_request(headers, channel_id=2).path == f"{PTZ_PRESET_PATH}?channel=2"
    assert build_ptz_tour_request(headers, channel_id=2).path == f"{PTZ_TOUR_PATH}?channel=2"
    assert (
        build_ptz_target_track_get_request(headers, channel_id=2).path
        == f"{PTZ_TARGET_TRACK_PATH}?channel=2"
    )
    tracking = build_ptz_target_track_set_request(
        headers,
        channel_id=2,
        enabled=PtzTargetTrackMode.ON,
        people_enabled=PtzTargetTrackMode.OFF,
    )
    assert json.loads(tracking.body or b"") == {
        "channel": 2,
        "enabled": "on",
        "people_enabled": "off",
    }
    assert move.headers == {
        "Authorization": "Bearer secret-token",
        "Content-Type": "application/json",
    }
    assert "secret-token" not in repr(move)


def test_ptz_parsers_cover_capability_presets_tours_tracking_and_empty_batch() -> None:
    capability = parse_ptz_capability_response(
        Response(status_code=200, body=json.dumps(_ptz_capability_payload()).encode()),
        channel_id=2,
    )
    assert capability.channel_id == 2
    park = parse_ptz_park_response(
        Response(
            status_code=200,
            body=b'{"action_mode":"preset","park_time":5,"action_id":2,"enabled":0,"error_code":0}',
        )
    )
    assert park.settings.action_mode is PtzParkActionMode.PRESET
    assert capability.capability.pan_tilt_supported == "1"
    assert (
        parse_ptz_batch_capability_response(
            Response(status_code=200, body=b'{"capability": [], "error_code": 0}')
        ).capabilities
        == ()
    )
    batch_payload = _ptz_capability_payload(id=2)
    batch = parse_ptz_batch_capability_response(
        Response(
            status_code=200,
            body=json.dumps({"capability": [batch_payload], "error_code": 0}).encode(),
        )
    )
    assert batch.capabilities[0].channel_id == 2

    presets = parse_ptz_preset_response(
        Response(
            status_code=200,
            body=b'{"preset":[{"preset_id":1,"read_only":0,"name":"Preset1"}],"error_code":0}',
        )
    )
    assert presets.presets[0].preset_id == 1
    tours = parse_ptz_tour_response(
        Response(
            status_code=200,
            body=json.dumps(
                {
                    "tour": [
                        {
                            "tour_id": 1,
                            "preset_count": 2,
                            "name": "Patrol%20Path1",
                            "preset_id": ["1", "2"],
                            "time": ["60", "60"],
                            "speed": ["0", "0"],
                        },
                        {"tour_id": 2, "preset_count": 0},
                    ],
                    "error_code": 0,
                }
            ).encode(),
        )
    )
    assert tours.tours[0].preset_ids == ("1", "2")
    assert tours.tours[1].name is None
    tracking = parse_target_tracking_response(
        Response(
            status_code=200,
            body=b'{"enabled":"off","people_enabled":"on","error_code":0}',
        )
    )
    assert tracking.settings.enabled is PtzTargetTrackMode.OFF
    assert tracking.settings.people_enabled is PtzTargetTrackMode.ON


@pytest.mark.parametrize(
    "builder",
    [
        lambda h: build_ptz_move_request(h, channel_id=1, direction="left", speed="0.6"),
        lambda h: build_ptz_move_request(h, channel_id=1, direction=0, speed=0.6),
        lambda h: build_ptz_park_set_request(
            h,
            channel_id=1,
            action_mode="tour",
            park_time=6,
            action_id=2,
            enabled=1,
        ),
        lambda h: build_ptz_target_track_set_request(
            h,
            channel_id=1,
            enabled="on",
            people_enabled=PtzTargetTrackMode.ON,
        ),
    ],
)
def test_ptz_builders_reject_values_outside_documented_types(builder) -> None:
    with pytest.raises(ValidationError):
        builder({"Authorization": "Bearer token"})


def test_audio_requests_parsers_and_exact_ranges() -> None:
    headers = {"Authorization": "Bearer secret-token"}
    assert build_audio_output_sound_get_request(headers, channel_id=1).path == (
        f"{AUDIO_OUTPUT_SOUND_PATH}?channel=1"
    )
    assert build_audio_input_sound_get_request(headers, channel_id=1).path == (
        f"{AUDIO_INPUT_SOUND_PATH}?channel=1"
    )
    assert build_audio_channel_capability_request(headers, channel_id=1).path == (
        f"{AUDIO_CHANNEL_CAPABILITY_PATH}?channel=1"
    )
    assert build_audio_capability_request(headers).path == AUDIO_CAPABILITY_PATH
    output_set = build_audio_output_sound_set_request(
        headers, channel_id=1, mute=AudioToggle.OFF, volume=100, system_volume=0
    )
    assert json.loads(output_set.body or b"") == {
        "mute": "off",
        "volume": 100,
        "system_volume": 0,
        "channel": 1,
    }
    input_set = build_audio_input_sound_set_request(
        headers,
        channel_id=1,
        mute=AudioToggle.ON,
        volume=50,
        noise_cancelling=AudioToggle.OFF,
    )
    assert json.loads(input_set.body or b"") == {
        "mute": "on",
        "volume": 50,
        "noise_cancelling": "off",
        "channel": 1,
    }
    output = parse_audio_output_sound_response(
        Response(
            status_code=200, body=b'{"mute":"on","volume":60,"system_volume":60,"error_code":0}'
        )
    )
    assert output.settings.mute is AudioToggle.ON
    input_sound = parse_audio_input_sound_response(
        Response(
            status_code=200,
            body=b'{"mute":"off","volume":50,"noise_cancelling":"off","error_code":0}',
        )
    )
    assert input_sound.settings.volume == 50
    channel_capability = parse_audio_channel_capability_response(
        Response(
            status_code=200, body=b'{"speaker_enable":1,"microphone_enable":0,"error_code":0}'
        ),
        1,
    )
    assert channel_capability.capability.microphone_enabled == 0
    nvr_capability = parse_audio_capability_response(
        Response(status_code=200, body=b'{"speaker_enable":0,"microphone_enable":1,"error_code":0}')
    )
    assert nvr_capability.capability.speaker_enabled == 0
    control = parse_audio_control_response(
        Response(status_code=200, body=b'{"sub_code":0,"error_code":0}')
    )
    assert control.sub_code == 0

    with pytest.raises(ValidationError):
        build_audio_output_sound_set_request(
            headers, channel_id=1, mute=AudioToggle.OFF, volume=101, system_volume=0
        )
    with pytest.raises(VigiResponseError):
        parse_audio_capability_response(
            Response(
                status_code=200, body=b'{"speaker_enable":2,"microphone_enable":1,"error_code":0}'
            )
        )


def test_alarm_requests_parsers_and_exact_control_payloads() -> None:
    headers = {"Authorization": "Bearer secret-token"}
    assert build_nvr_alarm_get_request(headers).path == NVR_ALARM_PATH
    nvr_set = build_nvr_alarm_set_request(
        headers,
        device_id=1,
        alarm_name="A1",
        delay_time=AlarmDelayTime.SIX_HUNDRED,
        enabled=AlarmEnabled.ON,
        alarm_type=AlarmType.NORMALLY_CLOSED,
    )
    assert json.loads(nvr_set.body or b"") == {
        "device_id": 1,
        "alarm_name": "A1",
        "delay_time": "600",
        "enabled": "on",
        "alarm_type": "NC",
    }
    assert build_ipc_alarm_get_request(headers, channel_id=1).path == f"{IPC_ALARM_PATH}?channel=1"
    ipc_set = build_ipc_alarm_set_request(
        headers,
        channel_id=1,
        alarm_name="A1",
        delay_time=AlarmDelayTime.FIVE,
        enabled=AlarmEnabled.OFF,
    )
    assert json.loads(ipc_set.body or b"") == {
        "channel": 1,
        "alarm_name": "A1",
        "delay_time": "5",
        "enabled": "off",
    }
    nvr_manual = build_nvr_manual_alarm_request(headers, device_id=1, action=AlarmAction.START)
    assert nvr_manual.path == NVR_MANUAL_ALARM_PATH
    assert json.loads(nvr_manual.body or b"") == {"device_id": 1, "action": "start"}
    ipc_manual = build_ipc_manual_alarm_request(headers, channel_id=1, action=AlarmAction.STOP)
    assert ipc_manual.path == IPC_MANUAL_ALARM_PATH
    assert json.loads(ipc_manual.body or b"") == {"channel": 1, "action": "stop"}
    assert build_batch_ipc_alarm_request(headers).path == BATCH_IPC_ALARM_PATH

    nvr = parse_nvr_alarm_response(
        Response(
            status_code=200,
            body=b'{"alarm_output_info":[{"device_id":1,"delay_time":"10","enabled":"off","alarm_name":"AO1","alarm_type":"NO"}],"error_code":0}',
        )
    )
    assert nvr.outputs[0].alarm_type is AlarmType.NORMALLY_OPEN
    ipc = parse_ipc_alarm_response(
        Response(
            status_code=200,
            body=b'{"delay_time":"600","enabled":"on","alarm_name":"A1","error_code":0}',
        ),
        1,
    )
    assert ipc.output.channel_id == 1
    batch = parse_batch_ipc_alarm_response(
        Response(
            status_code=200,
            body=b'{"alarm_output":[{"channel":1,"delay_time":"5","enabled":"off","alarm_name":"AO111","manual_alarm_out_supported":"1"}],"error_code":0}',
        )
    )
    assert batch.outputs[0].manual_alarm_out_supported == "1"
    manual = parse_alarm_manual_response(
        Response(status_code=200, body=b'{"timer":10,"error_code":0}'), "NVR manual alarm"
    )
    assert manual.timer == 10

    with pytest.raises(ValidationError):
        build_nvr_alarm_set_request(
            headers,
            device_id=0,
            alarm_name="A1",
            delay_time=AlarmDelayTime.TEN,
            enabled=AlarmEnabled.ON,
            alarm_type=AlarmType.NORMALLY_OPEN,
        )
    with pytest.raises(VigiResponseError):
        parse_batch_ipc_alarm_response(
            Response(
                status_code=200,
                body=b'{"alarm_output":[{"channel":1,"delay_time":"7","enabled":"off","alarm_name":"A1","manual_alarm_out_supported":"0"}],"error_code":0}',
            )
        )


def test_hardware_mutations_use_bearer_once_and_do_not_retry() -> None:
    client, transport = _bearer_client(
        [
            Response(status_code=500, body=b"{}"),
            Response(status_code=500, body=b"{}"),
            Response(status_code=500, body=b"{}"),
        ]
    )
    with pytest.raises(VigiApiError):
        client.ptz.move(1, 0, "0.6")
    with pytest.raises(VigiApiError):
        client.audio.set_output_sound(1, AudioToggle.OFF, 50, 50)
    with pytest.raises(VigiApiError):
        client.alarm_outputs.manual_nvr_alarm(1, AlarmAction.START)
    assert len(transport.requests) == 3
    assert all(
        request.headers["Authorization"] == "Bearer secret-token" for request in transport.requests
    )
    assert [request.path for request in transport.requests] == [
        PTZ_MOVE_PATH,
        AUDIO_OUTPUT_SOUND_PATH,
        NVR_MANUAL_ALARM_PATH,
    ]


def test_hardware_services_require_bearer_before_network_call() -> None:
    client, transport = _bearer_client([])
    client.session.info = SessionInfo()

    with pytest.raises(AuthenticationError):
        client.ptz.get_capability(1)
    with pytest.raises(AuthenticationError):
        client.audio.get_capability()
    with pytest.raises(AuthenticationError):
        client.alarm_outputs.get_batch_ipc_alarm()
    assert transport.requests == []

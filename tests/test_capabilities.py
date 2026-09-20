import json

import pytest

from vigi import AuthConfig, AuthMode, ModuleInfo, ModuleListResponse, VigiClient
from vigi.capabilities import (
    MODULE_LIST_PATH,
    build_module_list_request,
    parse_module_list_response,
)
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.session import Session, SessionInfo
from vigi.transport import Request, Response, Transport, TransportConfig


class FakeTransport(Transport):
    def __init__(self, responses: list[Response]) -> None:
        super().__init__(TransportConfig(base_url="https://nvr.local:20443"))
        self.responses = responses
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return self.responses.pop(0)


def _bearer_session(transport: Transport) -> Session:
    return Session(
        transport=transport,
        info=SessionInfo(
            authenticated=True,
            auth_mode=AuthMode.BEARER,
            access_token="secret-token",
        ),
    )


def test_module_list_request_creation() -> None:
    request = build_module_list_request({"Authorization": "Bearer secret-token"})

    assert request == Request(
        method="GET",
        path=MODULE_LIST_PATH,
        headers={"Authorization": "Bearer secret-token"},
    )
    assert "secret-token" not in repr(request)


def test_parse_module_list_response_preserves_unknown_modules_and_empty_lists() -> None:
    parsed = parse_module_list_response(
        Response(
            status_code=200,
            body=json.dumps(
                {
                    "module_list": [
                        {"name": "future_module", "version": 7},
                        {"name": "audio", "version": 1},
                    ],
                    "error_code": 0,
                }
            ).encode("utf-8"),
        )
    )

    assert parsed == ModuleListResponse(
        modules=(
            ModuleInfo(name="future_module", version=7),
            ModuleInfo(name="audio", version=1),
        ),
        error_code=0,
    )
    assert (
        parse_module_list_response(
            Response(
                status_code=200,
                body=json.dumps({"module_list": [], "error_code": 0}).encode("utf-8"),
            )
        ).modules
        == ()
    )


@pytest.mark.parametrize(
    "response",
    [
        Response(status_code=500, body=b"{}"),
        Response(status_code=200, body=json.dumps({"error_code": 1}).encode("utf-8")),
        Response(
            status_code=200,
            body=json.dumps({"module_list": [{"name": "audio"}], "error_code": 0}).encode("utf-8"),
        ),
    ],
)
def test_module_list_errors(response: Response) -> None:
    with pytest.raises((VigiApiError, VigiResponseError)):
        parse_module_list_response(response)


def test_capability_service_requires_bearer_before_network_call() -> None:
    transport = FakeTransport([])
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )

    with pytest.raises(AuthenticationError):
        client.capabilities.list_modules()

    assert transport.requests == []


def test_capability_service_uses_bearer_and_parses_response() -> None:
    transport = FakeTransport(
        [
            Response(
                status_code=200,
                body=json.dumps(
                    {"module_list": [{"name": "channel_management", "version": 1}], "error_code": 0}
                ).encode("utf-8"),
            )
        ]
    )
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )
    client.session.info = _bearer_session(transport).info

    result = client.capabilities.list_modules()

    assert result.modules == (ModuleInfo(name="channel_management", version=1),)
    assert transport.requests[0].method == "GET"
    assert transport.requests[0].path == MODULE_LIST_PATH
    assert transport.requests[0].headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(result)

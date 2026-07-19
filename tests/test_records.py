import json

import pytest

from vigi import AuthConfig, AuthMode, VigiClient
from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.models import (
    RecordDay,
    RecordDaysResponse,
    RecordSearchProcessResponse,
    RecordSearchResultsResponse,
    RecordSegment,
)
from vigi.records import (
    RECORD_DAYS_PATH,
    RECORD_FREE_PROCESS_PATH,
    RECORD_RESULTS_PATH,
    build_record_days_request,
    build_record_free_process_request,
    build_record_results_request,
    parse_record_days_response,
    parse_record_free_process_response,
    parse_record_results_response,
)
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


def _bearer_session(transport: Transport, token: str = "secret-token") -> Session:
    return Session(
        transport=transport,
        info=SessionInfo(
            authenticated=True,
            auth_mode=AuthMode.BEARER,
            token_type="bearer",
            access_token=token,
        ),
    )


def test_record_days_request_creation() -> None:
    request = build_record_days_request(
        {"Authorization": "Bearer secret-token"},
        channel_id=1,
        start_month="202501",
        end_month="202502",
    )

    assert request.method == "GET"
    assert request.path == f"{RECORD_DAYS_PATH}?channel=1&start=202501&end=202502"
    assert request.headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(request)


def test_record_free_process_request_creation() -> None:
    request = build_record_free_process_request({"Authorization": "Bearer secret-token"})

    assert request.method == "GET"
    assert request.path == RECORD_FREE_PROCESS_PATH
    assert request.headers == {"Authorization": "Bearer secret-token"}
    assert "secret-token" not in repr(request)


def test_record_results_request_creation() -> None:
    request = build_record_results_request(
        {"Authorization": "Bearer secret-token"},
        channel_id=1,
        process_id=6,
        day="20250101",
        start_index=0,
        end_index=99,
    )

    assert request.method == "GET"
    assert request.path == (
        f"{RECORD_RESULTS_PATH}?channel=1&process=6&day=20250101&start_index=0&end_index=99"
    )
    assert request.headers == {"Authorization": "Bearer secret-token"}


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        (
            {
                "channel_id": 0,
                "process_id": 1,
                "day": "20250101",
                "start_index": 0,
                "end_index": 99,
            },
            "channel_id",
        ),
        (
            {
                "channel_id": 1,
                "process_id": 0,
                "day": "20250101",
                "start_index": 0,
                "end_index": 99,
            },
            "process_id",
        ),
        (
            {
                "channel_id": 1,
                "process_id": 1,
                "day": "202501",
                "start_index": 0,
                "end_index": 99,
            },
            "day",
        ),
        (
            {
                "channel_id": 1,
                "process_id": 1,
                "day": "20250101",
                "start_index": -1,
                "end_index": 99,
            },
            "start_index",
        ),
        (
            {
                "channel_id": 1,
                "process_id": 1,
                "day": "20250101",
                "start_index": 5,
                "end_index": 4,
            },
            "end_index",
        ),
    ],
)
def test_record_results_request_validation(kwargs: dict[str, int | str], error_match: str) -> None:
    with pytest.raises(ValueError, match=error_match):
        build_record_results_request({"Authorization": "Bearer secret-token"}, **kwargs)


def test_parse_record_days_success_and_empty_response() -> None:
    response = Response(
        status_code=200,
        body=json.dumps(
            {
                "days": [{"day": "20250101"}, {"day": "20250102"}],
                "error_code": 0,
            }
        ).encode("utf-8"),
    )

    parsed = parse_record_days_response(response)

    assert parsed == RecordDaysResponse(
        days=(RecordDay(day="20250101"), RecordDay(day="20250102")),
        error_code=0,
    )
    assert (
        parse_record_days_response(
            Response(
                status_code=200,
                body=json.dumps({"days": [], "error_code": 0}).encode("utf-8"),
            )
        ).days
        == ()
    )


def test_parse_record_free_process_response() -> None:
    parsed = parse_record_free_process_response(
        Response(
            status_code=200,
            body=json.dumps({"process": 6, "error_code": 0}).encode("utf-8"),
        )
    )

    assert parsed == RecordSearchProcessResponse(process_id=6, error_code=0)


def test_parse_record_results_success_and_empty_response() -> None:
    response = Response(
        status_code=200,
        body=json.dumps(
            {
                "results": [
                    {"start_time": "1696118400", "end_time": "1696119000"},
                    {"start_time": "1696119000", "end_time": "1696119600"},
                ],
                "error_code": 0,
            }
        ).encode("utf-8"),
    )

    parsed = parse_record_results_response(response)

    assert parsed == RecordSearchResultsResponse(
        results=(
            RecordSegment(start_time="1696118400", end_time="1696119000"),
            RecordSegment(start_time="1696119000", end_time="1696119600"),
        ),
        error_code=0,
    )
    assert (
        parse_record_results_response(
            Response(
                status_code=200,
                body=json.dumps({"results": [], "error_code": 0}).encode("utf-8"),
            )
        ).results
        == ()
    )


@pytest.mark.parametrize(
    ("parser_name", "body"),
    [
        ("days", b"not-json"),
        ("days", json.dumps([]).encode("utf-8")),
        ("days", json.dumps({"error_code": 0}).encode("utf-8")),
        ("days", json.dumps({"days": {}, "error_code": 0}).encode("utf-8")),
        ("days", json.dumps({"days": [{"day": "202501"}], "error_code": 0}).encode()),
        ("process", json.dumps({"process": "6", "error_code": 0}).encode()),
        ("results", json.dumps({"results": {}, "error_code": 0}).encode()),
        (
            "results",
            json.dumps(
                {
                    "results": [{"start_time": "1696118400"}],
                    "error_code": 0,
                }
            ).encode(),
        ),
    ],
)
def test_record_parsers_malformed_response(parser_name: str, body: bytes) -> None:
    parser = {
        "days": parse_record_days_response,
        "process": parse_record_free_process_response,
        "results": parse_record_results_response,
    }[parser_name]

    with pytest.raises(VigiResponseError):
        parser(Response(status_code=200, body=body))


@pytest.mark.parametrize(
    "parser",
    [
        parse_record_days_response,
        parse_record_free_process_response,
        parse_record_results_response,
    ],
)
def test_record_parsers_api_errors(parser) -> None:
    with pytest.raises(VigiApiError):
        parser(Response(status_code=500, body=b"{}"))

    with pytest.raises(VigiApiError):
        parser(
            Response(
                status_code=200,
                body=json.dumps({"days": [], "error_code": 1001}).encode("utf-8"),
            )
        )


def test_record_service_requires_authentication_before_network_call() -> None:
    transport = FakeTransport([])
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )

    with pytest.raises(AuthenticationError):
        client.records.list_days(1, "202501", "202501")

    assert transport.requests == []


def test_record_service_uses_bearer_session_and_parsers() -> None:
    transport = FakeTransport(
        [
            Response(
                status_code=200,
                body=json.dumps({"days": [{"day": "20250101"}], "error_code": 0}).encode(),
            ),
            Response(
                status_code=200,
                body=json.dumps({"process": 6, "error_code": 0}).encode(),
            ),
            Response(
                status_code=200,
                body=json.dumps(
                    {
                        "results": [{"start_time": "1696118400", "end_time": "1696119000"}],
                        "error_code": 0,
                    }
                ).encode(),
            ),
        ]
    )
    client = VigiClient(
        AuthConfig(host="nvr.local", username="admin", password="password"),
        transport=transport,
    )
    client.session.info = _bearer_session(transport).info

    days = client.records.list_days(1, "202501", "202501")
    process = client.records.get_free_process()
    results = client.records.list_results(1, process.process_id, "20250101", 0, 99)

    assert days.days == (RecordDay(day="20250101"),)
    assert process.process_id == 6
    assert results.results == (RecordSegment(start_time="1696118400", end_time="1696119000"),)
    assert [request.method for request in transport.requests] == ["GET", "GET", "GET"]
    assert transport.requests[0].path.startswith("/openapi/record/days?")
    assert transport.requests[1].path == "/openapi/record/search/free_process"
    assert transport.requests[2].path.startswith("/openapi/record/search/results?")
    assert all(
        request.headers == {"Authorization": "Bearer secret-token"}
        for request in transport.requests
    )
    assert "secret-token" not in repr(results)

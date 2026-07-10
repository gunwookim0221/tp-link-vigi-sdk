"""NVR recording search support."""

import json
from typing import Mapping
from urllib.parse import urlencode

from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError, ValidationError
from vigi.models import (
    RecordDay,
    RecordDaysResponse,
    RecordSearchProcessResponse,
    RecordSearchResultsResponse,
    RecordSegment,
)
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import AuthMode


RECORD_DAYS_PATH = "/openapi/record/days"
RECORD_FREE_PROCESS_PATH = "/openapi/record/search/free_process"
RECORD_RESULTS_PATH = "/openapi/record/search/results"


class RecordService:
    """Documented NVR read-only recording search APIs."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def list_days(
        self, channel_id: int, start_month: str, end_month: str
    ) -> RecordDaysResponse:
        """List days with recordings for a channel over a month range."""

        headers = self._bearer_headers()
        request = build_record_days_request(
            headers,
            channel_id=channel_id,
            start_month=start_month,
            end_month=end_month,
        )
        return parse_record_days_response(self.session.transport.send(request))

    def get_free_process(self) -> RecordSearchProcessResponse:
        """Get a free recording search process ID."""

        request = build_record_free_process_request(self._bearer_headers())
        return parse_record_free_process_response(self.session.transport.send(request))

    def list_results(
        self,
        channel_id: int,
        process_id: int,
        day: str,
        start_index: int = 0,
        end_index: int = 99,
    ) -> RecordSearchResultsResponse:
        """List recording segments for a channel, process, day, and index range."""

        headers = self._bearer_headers()
        request = build_record_results_request(
            headers,
            channel_id=channel_id,
            process_id=process_id,
            day=day,
            start_index=start_index,
            end_index=end_index,
        )
        return parse_record_results_response(self.session.transport.send(request))

    def _bearer_headers(self) -> Mapping[str, str]:
        if self.session is None:
            raise AuthenticationError("An authenticated session is required.")
        if not self.session.info.authenticated:
            raise AuthenticationError("An authenticated session is required.")
        if self.session.info.auth_mode is not AuthMode.BEARER:
            raise AuthenticationError("Bearer authentication is required.")

        headers = self.session.info.bearer_headers()
        if "Authorization" not in headers:
            raise AuthenticationError("Bearer authentication is required.")
        return headers


def build_record_days_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    start_month: str,
    end_month: str,
) -> Request:
    """Build the documented recording days request."""

    _require_positive_int(channel_id, "channel_id")
    _require_ym(start_month, "start_month")
    _require_ym(end_month, "end_month")
    query = urlencode({"channel": channel_id, "start": start_month, "end": end_month})
    return Request(method="GET", path=f"{RECORD_DAYS_PATH}?{query}", headers=headers)


def build_record_free_process_request(headers: Mapping[str, str]) -> Request:
    """Build the documented free-process request."""

    return Request(method="GET", path=RECORD_FREE_PROCESS_PATH, headers=headers)


def build_record_results_request(
    headers: Mapping[str, str],
    *,
    channel_id: int,
    process_id: int,
    day: str,
    start_index: int,
    end_index: int,
) -> Request:
    """Build the documented recording results request."""

    _require_positive_int(channel_id, "channel_id")
    _require_positive_int(process_id, "process_id")
    _require_ymd(day, "day")
    _require_non_negative_int(start_index, "start_index")
    _require_non_negative_int(end_index, "end_index")
    if end_index < start_index:
        raise ValidationError("end_index must be greater than or equal to start_index.")

    query = urlencode(
        {
            "channel": channel_id,
            "process": process_id,
            "day": day,
            "start_index": start_index,
            "end_index": end_index,
        }
    )
    return Request(method="GET", path=f"{RECORD_RESULTS_PATH}?{query}", headers=headers)


def parse_record_days_response(response: Response) -> RecordDaysResponse:
    """Parse a documented recording days response."""

    payload = _parse_payload(response, "Record days")
    days_payload = payload.get("days")
    if not isinstance(days_payload, list):
        raise VigiResponseError("Record days response days must be a list.")

    days: list[RecordDay] = []
    for day_payload in days_payload:
        if not isinstance(day_payload, dict):
            raise VigiResponseError("Record day entry must be a JSON object.")
        day = _required_str(day_payload, "day", "Record day")
        _require_response_ymd(day, "day")
        days.append(RecordDay(day=day))
    return RecordDaysResponse(days=tuple(days), error_code=payload["error_code"])


def parse_record_free_process_response(response: Response) -> RecordSearchProcessResponse:
    """Parse a documented free-process response."""

    payload = _parse_payload(response, "Record free process")
    process_id = _required_int(payload, "process", "Record free process")
    return RecordSearchProcessResponse(
        process_id=process_id,
        error_code=payload["error_code"],
    )


def parse_record_results_response(response: Response) -> RecordSearchResultsResponse:
    """Parse a documented recording results response."""

    payload = _parse_payload(response, "Record results")
    results_payload = payload.get("results")
    if not isinstance(results_payload, list):
        raise VigiResponseError("Record results response results must be a list.")

    results: list[RecordSegment] = []
    for result_payload in results_payload:
        if not isinstance(result_payload, dict):
            raise VigiResponseError("Record result entry must be a JSON object.")
        start_time = _required_str(result_payload, "start_time", "Record result")
        end_time = _required_str(result_payload, "end_time", "Record result")
        results.append(RecordSegment(start_time=start_time, end_time=end_time))
    return RecordSearchResultsResponse(
        results=tuple(results),
        error_code=payload["error_code"],
    )


def _parse_payload(response: Response, label: str) -> dict[str, object]:
    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"{label} endpoint returned HTTP {response.status_code}.")

    try:
        payload = json.loads((response.body or b"{}").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VigiResponseError(f"{label} response is not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise VigiResponseError(f"{label} response must be a JSON object.")

    error_code = payload.get("error_code")
    if not isinstance(error_code, int):
        raise VigiResponseError(f"{label} response is missing numeric error_code.")
    if error_code != 0:
        raise VigiApiError(f"{label} endpoint returned error_code {error_code}.")
    return payload


def _required_int(payload: dict[str, object], key: str, label: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise VigiResponseError(f"{label} field {key} must be an integer.")
    return value


def _required_str(payload: dict[str, object], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise VigiResponseError(f"{label} field {key} must be a string.")
    return value


def _require_positive_int(value: int, field_name: str) -> None:
    if not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer.")
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")


def _require_non_negative_int(value: int, field_name: str) -> None:
    if not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer.")
    if value < 0:
        raise ValidationError(f"{field_name} must be greater than or equal to 0.")


def _require_ym(value: str, field_name: str) -> None:
    _require_digits(value, field_name, 6)


def _require_ymd(value: str, field_name: str) -> None:
    _require_digits(value, field_name, 8)


def _require_response_ymd(value: str, field_name: str) -> None:
    if len(value) != 8 or not value.isdigit():
        raise VigiResponseError(f"Record day field {field_name} must use %Y%m%d format.")


def _require_digits(value: str, field_name: str, length: int) -> None:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string.")
    if len(value) != length or not value.isdigit():
        raise ValidationError(f"{field_name} must use the documented numeric format.")

"""Capability declarations and documented module discovery."""

import json
from typing import Mapping, cast

from vigi.exceptions import AuthenticationError, VigiApiError, VigiResponseError
from vigi.models import ModuleInfo, ModuleListResponse
from vigi.session import Session
from vigi.transport import Request, Response
from vigi.types import CapabilityName
from vigi.types import AuthMode


Capability = CapabilityName

MODULE_LIST_PATH = "/openapi/module_list"


class CapabilityService:
    """Read the NVR's documented module/version capability list."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def list_modules(self) -> ModuleListResponse:
        """List module names and versions from the authenticated NVR."""

        headers = self._bearer_headers()
        session = cast(Session, self.session)
        request = build_module_list_request(headers)
        return parse_module_list_response(session.transport.send(request))

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


def build_module_list_request(headers: Mapping[str, str]) -> Request:
    """Build the documented module-list request."""

    return Request(method="GET", path=MODULE_LIST_PATH, headers=headers)


def parse_module_list_response(response: Response) -> ModuleListResponse:
    """Parse module names and versions while preserving unknown names."""

    if response.status_code < 200 or response.status_code >= 300:
        raise VigiApiError(f"Module list endpoint returned HTTP {response.status_code}.")

    try:
        payload = json.loads((response.body or b"{}").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VigiResponseError("Module list response is not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise VigiResponseError("Module list response must be a JSON object.")

    error_code = payload.get("error_code")
    if not isinstance(error_code, int) or isinstance(error_code, bool):
        raise VigiResponseError("Module list response is missing numeric error_code.")
    if error_code != 0:
        raise VigiApiError(f"Module list endpoint returned error_code {error_code}.")

    modules_payload = payload.get("module_list")
    if not isinstance(modules_payload, list):
        raise VigiResponseError("Module list response module_list must be a list.")

    modules: list[ModuleInfo] = []
    for module_payload in modules_payload:
        if not isinstance(module_payload, dict):
            raise VigiResponseError("Module list entry must be a JSON object.")
        name = module_payload.get("name")
        version = module_payload.get("version")
        if not isinstance(name, str) or not name:
            raise VigiResponseError("Module list field name must be a non-empty string.")
        if not isinstance(version, int) or isinstance(version, bool):
            raise VigiResponseError("Module list field version must be an integer.")
        modules.append(ModuleInfo(name=name, version=version))

    return ModuleListResponse(modules=tuple(modules), error_code=error_code)

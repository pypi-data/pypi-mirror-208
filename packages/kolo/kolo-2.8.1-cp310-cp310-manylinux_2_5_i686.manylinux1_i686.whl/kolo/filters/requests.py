from __future__ import annotations

import os
import time
import types
from typing import Dict, List, TYPE_CHECKING, Tuple

import ulid

from ..serialize import decode_body


if TYPE_CHECKING:
    # Literal and TypedDict only exist on python 3.8+
    # We run mypy using a high enough version, so this is ok!
    from typing import Literal, TypedDict

    class ApiRequest(TypedDict):
        body: str | None
        frame_id: str
        headers: Dict[str, str]
        method: str
        method_and_full_url: str
        subtype: Literal["requests"]
        timestamp: float | str
        type: Literal["outbound_http_request"]
        url: str

    class ApiResponse(TypedDict):
        body: str | None
        frame_id: str
        headers: Dict[str, str] | None
        method: str
        method_and_full_url: str
        status_code: int | None
        subtype: Literal["requests"]
        timestamp: float | str
        type: Literal["outbound_http_response"]
        url: str


class ApiRequestFilter:
    co_names: Tuple[str, ...] = ("send",)
    requests_filename = os.path.normpath("requests/sessions")

    def __init__(self, config) -> None:
        self.config = config
        self.last_response: ApiResponse | None = None
        self._frame_ids: Dict[int, str] = {}

    def __call__(self, frame: types.FrameType, event: str, arg: object) -> bool:
        filepath = frame.f_code.co_filename
        callable_name = frame.f_code.co_name
        return callable_name == "send" and self.requests_filename in filepath

    def process(
        self,
        frame: types.FrameType,
        event: str,
        arg: object,
        call_frames: List[Tuple[types.FrameType, str]],
    ):
        timestamp = time.time()
        frame_locals = frame.f_locals
        request = frame_locals["request"]
        method_and_url = f"{request.method} {request.url}"

        if event == "call":
            frame_id = f"frm_{ulid.new()}"
            self._frame_ids[id(frame)] = frame_id

            api_request: ApiRequest = {
                "body": decode_body(request.body, request.headers),
                "frame_id": frame_id,
                "headers": dict(request.headers),
                "method": request.method,
                "method_and_full_url": method_and_url,
                "subtype": "requests",
                "timestamp": timestamp,
                "type": "outbound_http_request",
                "url": request.url,
            }
            return api_request

        assert event == "return"

        response = arg
        if TYPE_CHECKING:
            from requests.models import Response

            assert isinstance(response, Response)

        if response is None:
            body = None
            headers = None
            status_code = None
        else:
            body = response.text
            headers = dict(response.headers)
            status_code = response.status_code

        api_response: ApiResponse = {
            "body": body,
            "frame_id": self._frame_ids[id(frame)],
            "headers": headers,
            "method": request.method,
            "method_and_full_url": method_and_url,
            "status_code": status_code,
            "subtype": "requests",
            "timestamp": timestamp,
            "type": "outbound_http_response",
            "url": request.url,
        }
        return api_response

from __future__ import annotations

import os
import time
import types
from typing import Dict, List, TYPE_CHECKING, Tuple

import ulid

from ..serialize import decode_body, decode_header_value


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
        subtype: Literal["urllib"]
        timestamp: float | str
        type: Literal["outbound_http_request"]
        url: str

    class ApiResponse(TypedDict):
        frame_id: str
        headers: Dict[str, str]
        method: str
        method_and_full_url: str
        status_code: int
        subtype: Literal["urllib"]
        timestamp: float | str
        type: Literal["outbound_http_response"]
        url: str


class UrllibFilter:
    co_names: Tuple[str, ...] = ("do_open",)
    urllib_filename = os.path.normpath("urllib/request")

    def __init__(self, config) -> None:
        self.config = config
        self.last_response: ApiResponse | None = None
        self._frame_ids: Dict[int, str] = {}

    def __call__(self, frame: types.FrameType, event: str, arg: object) -> bool:
        return (
            frame.f_code.co_name == "do_open"
            and self.urllib_filename in frame.f_code.co_filename
        )

    def process(
        self,
        frame: types.FrameType,
        event: str,
        arg: object,
        call_frames: List[Tuple[types.FrameType, str]],
    ):
        request = frame.f_locals["req"]
        full_url = request.full_url
        method = request.get_method()
        method_and_full_url = f"{method} {full_url}"
        if event == "call":
            frame_id = f"frm_{ulid.new()}"
            self._frame_ids[id(frame)] = frame_id
            request_headers = {
                key: decode_header_value(value) for key, value in request.header_items()
            }

            api_request: ApiRequest = {
                "body": decode_body(request.data, request_headers),
                "frame_id": frame_id,
                "headers": request_headers,
                "method": method,
                "method_and_full_url": method_and_full_url,
                "subtype": "urllib",
                "timestamp": time.time(),
                "type": "outbound_http_request",
                "url": full_url,
            }
            return api_request

        elif event == "return":  # pragma: no branch
            response = frame.f_locals["r"]
            api_response: ApiResponse = {
                "frame_id": self._frame_ids[id(frame)],
                "headers": dict(response.headers),
                "method": method,
                "method_and_full_url": method_and_full_url,
                "status_code": response.status,
                "subtype": "urllib",
                "timestamp": time.time(),
                "type": "outbound_http_response",
                "url": full_url,
            }
            return api_response

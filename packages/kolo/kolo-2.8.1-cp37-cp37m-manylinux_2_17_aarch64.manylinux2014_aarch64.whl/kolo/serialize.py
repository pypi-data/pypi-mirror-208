from __future__ import annotations

import gzip
import json
import logging
import os
import types
from cgi import parse_header
from datetime import date, datetime
from typing import Any, Dict, TypeVar, TYPE_CHECKING


logger = logging.getLogger("kolo")


if TYPE_CHECKING:
    # TypedDict only exists on python 3.8+
    # We run mypy using a high enough version, so this is ok!
    from typing import TypedDict

    from django.http import HttpRequest, HttpResponse, StreamingHttpResponse

    class UserCodeCallSite(TypedDict):
        line_number: int
        call_frame_id: str

    Local = TypeVar("Local")


SERIALIZE_PATH = os.path.normpath("kolo/serialize.py")


# TODO: Make these threadlocals when we support multithreading
QUERYSET_PATCHED = False
IN_KOLO_PROFILER = False


def monkeypatch_queryset_repr():
    global QUERYSET_PATCHED
    if QUERYSET_PATCHED:
        return

    try:
        from django.db.models import QuerySet
    except ImportError:  # pragma: no cover
        QUERYSET_PATCHED = True
        return

    old_repr = QuerySet.__repr__

    def new_repr(queryset):
        if queryset._result_cache is None and IN_KOLO_PROFILER:
            return f"Unevaluated queryset for: {queryset.model}"
        return old_repr(queryset)

    QuerySet.__repr__ = new_repr  # type: ignore
    QUERYSET_PATCHED = True


def dump_json(data):
    global IN_KOLO_PROFILER
    IN_KOLO_PROFILER = True
    try:
        return json.dumps(data, skipkeys=True, cls=KoloJSONEncoder)
    finally:
        IN_KOLO_PROFILER = False


class KoloJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        try:
            return repr(obj)
        except Exception:
            return "SerializationError"


def decode_header_value(bytes_or_str: bytes | str) -> str:
    """
    Convert a bytes header value to text.

    Valid header values are expected to be ascii in modern times, but
    ISO-8859-1 (latin1) has historically been allowed.

    https://datatracker.ietf.org/doc/html/rfc7230#section-3.2.4
    """
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode("latin1")
    return bytes_or_str


def frame_path(frame: types.FrameType) -> str:
    path = frame.f_code.co_filename
    try:
        relative_path = os.path.relpath(path)
    except ValueError:
        relative_path = path
    return f"{relative_path}:{frame.f_lineno}"


def decode_body(body: Any, request_headers: Dict[str, str]) -> Any:
    """Convert a request body into a json-serializable form."""
    if isinstance(body, bytes):
        content_type = request_headers.get("Content-Type", "")
        charset = parse_header(content_type)[1].get("charset", "utf-8")
        try:
            return body.decode(charset)
        except UnicodeDecodeError:
            return "<Binary request body>"
    return body


def get_content(response: HttpResponse | StreamingHttpResponse) -> str:
    if response.streaming:
        return "<Streaming Response>"

    if TYPE_CHECKING:
        assert isinstance(response, HttpResponse)
    content_encoding = response.get("Content-Encoding")
    if content_encoding == "gzip":
        content = gzip.decompress(response.content)
    else:
        content = response.content
    try:
        return content.decode(response.charset)
    except UnicodeDecodeError:
        return f"<Response with invalid charset ({response.charset})>"


def get_request_body(request: "HttpRequest") -> str:
    from django.http.request import RawPostDataException

    try:
        return request.body.decode("utf-8")
    except UnicodeDecodeError:  # pragma: no cover
        return "<Binary request body>"
    except RawPostDataException:
        return "<Request data already read>"

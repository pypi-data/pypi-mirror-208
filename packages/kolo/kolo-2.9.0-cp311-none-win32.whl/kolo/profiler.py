from __future__ import annotations

import inspect
import json
import logging
import sys
import time
import types
from collections.abc import Mapping
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, TypeVar, TYPE_CHECKING, overload

import ulid

from .config import load_config
from .db import save_invocation_in_sqlite, setup_db
from .filters.attrs import attrs_filter
from .filters.celery import CeleryFilter
from .filters.core import (
    build_frame_filter,
    exec_filter,
    frozen_filter,
    library_filter,
    module_init_filter,
)
from .filters.django import DjangoFilter, DjangoTemplateFilter
from .filters.exception import ExceptionFilter
from .filters.huey import HueyFilter
from .filters.kolo import kolo_filter
from .filters.logging import LoggingFilter
from .filters.pypy import pypy_filter
from .filters.pytest import PytestFilter
from .filters.requests import ApiRequestFilter
from .filters.sql import SQLQueryFilter
from .filters.unittest import UnitTestFilter
from .filters.urllib import UrllibFilter
from .filters.urllib3 import Urllib3Filter
from .git import COMMIT_SHA
from .serialize import dump_json, frame_path, monkeypatch_queryset_repr
from .version import __version__


logger = logging.getLogger("kolo")


if TYPE_CHECKING:
    from typing_extensions import Protocol

    from .filters.core import FrameFilter, FrameProcessor
    from .serialize import UserCodeCallSite

    F = TypeVar("F", bound=Callable[..., Any])

    class CallableContextManager(Protocol):
        def __call__(self, func: F) -> F:
            ...

        def __enter__(self) -> None:
            ...

        def __exit__(self, *exc) -> None:
            ...


class KoloProfiler:
    """
    Collect runtime information about code to view in VSCode.

    include_frames can be passed to enable profiling of standard library
    or third party code.

    ignore_frames can also be passed to disable profiling of a user's
    own code.

    The list should contain fragments of the path to the relevant files.
    For example, to include profiling for the json module the include_frames
    could look like ["/json/"].

    The list may also contain frame filters. A frame filter is a function
    (or other callable) that takes the same arguments as the profilefunc
    passed to sys.setprofile and returns a boolean representing whether
    to allow or block the frame.

    include_frames takes precedence over ignore_frames. A frame that
    matches an entry in each list will be profiled.
    """

    def __init__(self, db_path: Path, config=None, one_trace_per_test=False) -> None:
        self.db_path = db_path
        self.one_trace_per_test = one_trace_per_test
        trace_id = ulid.new()
        self.trace_id = f"trc_{trace_id}"
        self.frames_of_interest: List[str] = []
        self.config = config if config is not None else {}
        filter_config = self.config.get("filters", {})
        include_frames = filter_config.get("include_frames", ())
        ignore_frames = filter_config.get("ignore_frames", ())
        self.include_frames = list(map(build_frame_filter, include_frames))
        self.ignore_frames = list(map(build_frame_filter, ignore_frames))
        self._default_include_frames: List[FrameProcessor] = [
            DjangoFilter(self.config),
            DjangoTemplateFilter(self.config),
            CeleryFilter(self.config),
            HueyFilter(self.config),
            ApiRequestFilter(self.config),
            UrllibFilter(self.config),
            Urllib3Filter(self.config),
            ExceptionFilter(
                self.config,
                ignore_frames=self.ignore_frames,
                include_frames=self.include_frames,
            ),
            LoggingFilter(self.config),
            SQLQueryFilter(self.config),
            UnitTestFilter(self.config),
            PytestFilter(self.config),
        ]

        self.default_include_frames: Dict[str, List[FrameProcessor]] = {}
        for filter in self._default_include_frames:
            for co_name in filter.co_names:
                self.default_include_frames.setdefault(co_name, []).append(filter)

        self.default_ignore_frames: List[FrameFilter] = [
            library_filter,
            frozen_filter,
            pypy_filter,
            kolo_filter,
            module_init_filter,
            exec_filter,
            attrs_filter,
        ]
        self.call_frames: List[Tuple[types.FrameType, str]] = []
        self.timestamp = time.time()
        self._frame_ids: Dict[int, str] = {}
        self.rust_profiler = None

    def __call__(self, frame: types.FrameType, event: str, arg: object) -> None:
        if event in ["c_call", "c_return"]:
            return

        for frame_filter in self.include_frames:
            try:
                if frame_filter(frame, event, arg):
                    self.process_frame(frame, event, arg)
                    return
            except Exception as e:
                logger.warning(
                    "Unexpected exception in include_frames: %s",
                    frame_filter,
                    exc_info=e,
                )
                continue

        for frame_filter in self.ignore_frames:
            try:
                if frame_filter(frame, event, arg):
                    return
            except Exception as e:
                logger.warning(
                    "Unexpected exception in ignore_frames: %s",
                    frame_filter,
                    exc_info=e,
                )
                continue

        co_name = frame.f_code.co_name

        # Execute only the filters listening for this co_name
        for frame_filter in self.default_include_frames.get(co_name, ()):
            try:
                if frame_filter(frame, event, arg):
                    frame_data = frame_filter.process(
                        frame, event, arg, self.call_frames
                    )
                    if frame_data:  # pragma: no branch
                        # We use skipkeys here so unserialisable dict keys
                        # are skipped. Otherwise they would break the trace.
                        self.frames_of_interest.append(dump_json(frame_data))
                        if self.one_trace_per_test:  # pragma: no cover
                            if frame_data["type"] == "start_test":
                                self.trace_id = f"trc_{ulid.new()}"
                                self.start_test_index = len(self.frames_of_interest) - 1
                            elif frame_data["type"] == "end_test":
                                self.save_request_in_db(
                                    self.frames_of_interest[self.start_test_index :]
                                )
                    return
            except Exception as e:
                logger.warning(
                    "Unexpected exception in default_include_frames: %s",
                    frame_filter,
                    exc_info=e,
                )
                continue

        for frame_filter in self.default_ignore_frames:
            try:
                if frame_filter(frame, event, arg):
                    return
            except Exception as e:
                logger.warning(
                    "Unexpected exception in default_ignore_frames: %s",
                    frame_filter,
                    exc_info=e,
                )
                continue

        try:
            self.process_frame(frame, event, arg)
        except Exception as e:
            logger.warning(
                "Unexpected exception in KoloProfiler.process_frame",
                exc_info=e,
            )

    def __enter__(self) -> None:
        if self.config.get("use_rust", True):
            try:
                from ._kolo import register_profiler
            except ImportError:
                sys.setprofile(self)
            else:
                register_profiler(self)
        else:
            sys.setprofile(self)

    def __exit__(self, *exc) -> None:
        sys.setprofile(None)

    def format_data(self, data: Dict[str, Any], frames: List[str] | None) -> str:
        """
        Build a json blob from trace data and frame data

        `frames` is a list of json strings, so if we naïvely add it to `data` and
        dump it as json, we'll double encode it. Instead, we build the json array
        with some string formatting and replace the `frames_placeholder` in data
        with more string formatting.
        """
        frames_placeholder = "KOLO_FRAMES_OF_INTEREST"
        data["frames_of_interest"] = frames_placeholder
        json_data = dump_json(data)

        frames = self.frames_of_interest if frames is None else frames
        json_frames = ", ".join(frames)
        return json_data.replace(json.dumps(frames_placeholder), f"[{json_frames}]")

    def save_request_in_db(self, frames=None) -> None:
        if self.rust_profiler:
            self.rust_profiler.save_request_in_db()
            return

        wal_mode = self.config.get("wal_mode", True)
        timestamp = self.timestamp
        data = {
            "command_line_args": sys.argv,
            "current_commit_sha": COMMIT_SHA,
            "meta": {"version": __version__, "use_frame_boundaries": True},
            "timestamp": timestamp,
            "trace_id": self.trace_id,
        }
        json_data = self.format_data(data, frames)
        save_invocation_in_sqlite(self.db_path, self.trace_id, json_data, wal_mode)

    def process_frame(self, frame: types.FrameType, event: str, arg: object) -> None:
        user_code_call_site: UserCodeCallSite | None
        if event == "call" and self.call_frames:
            call_frame, call_frame_id = self.call_frames[-1]
            user_code_call_site = {
                "call_frame_id": call_frame_id,
                "line_number": call_frame.f_lineno,
            }
        else:
            # If we are a return frame, we don't bother duplicating
            # information for the call frame.
            # If we are the first call frame, we don't have a callsite.
            user_code_call_site = None

        co_name = frame.f_code.co_name
        if event == "call":
            frame_id = f"frm_{ulid.new()}"
            self._frame_ids[id(frame)] = frame_id
            self.call_frames.append((frame, frame_id))
        elif event == "return":  # pragma: no branch
            self.call_frames.pop()

        frame_data = {
            "path": frame_path(frame),
            "co_name": co_name,
            "qualname": get_qualname(frame),
            "event": event,
            "frame_id": self._frame_ids[id(frame)],
            "arg": arg,
            "locals": frame.f_locals,
            "timestamp": time.time(),
            "type": "frame",
            "user_code_call_site": user_code_call_site,
        }
        self.frames_of_interest.append(dump_json(frame_data))


def get_qualname(frame: types.FrameType) -> str | None:
    try:
        qualname = frame.f_code.co_qualname
    except AttributeError:
        pass
    else:
        module = frame.f_globals["__name__"]
        return f"{module}.{qualname}"

    co_name = frame.f_code.co_name
    if co_name == "<module>":  # pragma: no cover
        module = frame.f_globals["__name__"]
        return f"{module}.<module>"

    try:
        outer_frame = frame.f_back
        assert outer_frame
        try:
            function = outer_frame.f_locals[co_name]
        except KeyError:
            try:
                self = frame.f_locals["self"]
            except KeyError:
                cls = frame.f_locals.get("cls")
                if isinstance(cls, type):
                    function = inspect.getattr_static(cls, co_name)
                else:
                    try:
                        qualname = frame.f_locals["__qualname__"]
                    except KeyError:
                        function = frame.f_globals[co_name]
                    else:  # pragma: no cover
                        module = frame.f_globals["__name__"]
                        return f"{module}.{qualname}"
            else:
                function = inspect.getattr_static(self, co_name)
                if isinstance(function, property):
                    function = function.fget

        return f"{function.__module__}.{function.__qualname__}"
    except Exception:
        return None


class Enabled:
    def __init__(self, config: Mapping[str, Any] | None = None):
        self.config = config
        self._profiler: KoloProfiler | None = None

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner

    def __enter__(self) -> None:
        if sys.getprofile():
            return

        config = load_config(self.config)
        db_path = setup_db(config)
        monkeypatch_queryset_repr()
        self._profiler = KoloProfiler(db_path, config=config)
        self._profiler.__enter__()

    def __exit__(self, *exc) -> None:
        if self._profiler is not None:
            self._profiler.__exit__(*exc)
        if self._profiler is not None:
            self._profiler.save_request_in_db()
            self._profiler = None


@overload
def enable(_func: F) -> F:
    """Stub"""


@overload
def enable(config: Mapping[str, Any] | None = None) -> CallableContextManager:
    """Stub"""


def enable(config=None):
    if config is None or isinstance(config, Mapping):
        return Enabled(config)
    # Treat as a decorator called on a function
    return Enabled()(config)


enabled = enable

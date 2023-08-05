from __future__ import annotations

import os
import time
from typing import Any, Dict, Tuple, TYPE_CHECKING, Type

import ulid


if TYPE_CHECKING:
    # Literal and TypedDict only exist on python 3.8+
    # We run mypy using a high enough version, so this is ok!
    from typing import Literal, TypedDict
    from huey.api import Task

    class HueyJob(TypedDict, total=False):
        frame_id: str
        name: str
        args: Tuple[Any, ...]
        kwargs: Dict[str, Any]
        timestamp: float
        type: Literal["background_job", "background_job_end"]
        subtype: Literal["huey"]


class HueyFilter:
    co_names: Tuple[str, ...] = ("execute",)
    huey_filename = os.path.normpath("/huey/api.py")
    klass: Type[Task] | None = None

    def __init__(self, config) -> None:
        self.config = config
        self._frame_ids: Dict[int, str] = {}

    def __call__(self, frame, event, arg):
        if (
            self.huey_filename in frame.f_code.co_filename
            and frame.f_code.co_name in self.co_names
        ):
            # Doing the import once and binding is substantially faster than going
            # through the import system every time.
            # See:
            # https://github.com/django/asgiref/issues/269
            # https://github.com/django/asgiref/pull/288
            # A more battle-tested (slightly slower/more complex) alternative would be:
            # https://github.com/django/django/pull/14850
            # https://github.com/django/django/pull/14858
            # https://github.com/django/django/pull/14931
            if HueyFilter.klass is None:
                from huey.api import Task

                HueyFilter.klass = Task
            return isinstance(frame.f_locals["self"], HueyFilter.klass)
        return False

    def process(self, frame, event, arg, call_frames):
        huey_job: HueyJob
        timestamp = time.time()

        frame_locals = frame.f_locals
        task_object = frame_locals["self"]
        task_args, task_kwargs = task_object.data

        if event == "call":
            frame_id = f"frm_{ulid.new()}"
            self._frame_ids[id(frame)] = frame_id
            huey_job = {
                "frame_id": frame_id,
                "name": f"{task_object.__module__}.{task_object.name}",
                "args": task_args,
                "kwargs": task_kwargs,
                "timestamp": timestamp,
                "type": "background_job",
                "subtype": "huey",
            }
            return huey_job

        assert event == "return"

        huey_job = {
            "frame_id": self._frame_ids[id(frame)],
            "name": f"{task_object.__module__}.{task_object.name}",
            "args": task_args,
            "kwargs": task_kwargs,
            "timestamp": timestamp,
            "type": "background_job_end",
            "subtype": "huey",
        }
        return huey_job

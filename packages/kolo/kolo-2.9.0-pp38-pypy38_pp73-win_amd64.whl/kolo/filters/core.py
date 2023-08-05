from __future__ import annotations

import os
import types
import platform
import logging
from importlib import import_module
from typing import Any, Dict, List, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from typing_extensions import Protocol

    class FrameFilter(Protocol):
        def __call__(self, frame: types.FrameType, event: str, arg: object) -> bool:
            pass

    ProtoFrameFilter = str | FrameFilter | Dict[str, str]

    class FrameProcessor(Protocol):
        config: Dict[str, Any]
        co_names: Tuple[str, ...]

        def __call__(self, frame: types.FrameType, event: str, arg: object) -> bool:
            pass

        def process(
            self,
            frame: types.FrameType,
            event: str,
            arg: object,
            call_frames: List[Tuple[types.FrameType, str]],
        ) -> Dict[str, Any]:
            pass


logger = logging.getLogger("kolo")


class HasPath:
    def __init__(self, path: str):
        self.path = path

    def __call__(self, frame: types.FrameType, event: str, arg: object) -> bool:
        return self.path in frame.f_code.co_filename

    def __repr__(self):
        return f'HasPath("{self.path}")'

    def __eq__(self, other):
        return self.path == other.path


def build_frame_filter(filter: "ProtoFrameFilter") -> "FrameFilter":
    if isinstance(filter, str):
        return HasPath(filter)
    if isinstance(filter, dict):
        filter_path = filter["callable"]
        module_path, _sep, filter_name = filter_path.rpartition(".")
        module = import_module(module_path)
        return getattr(module, filter_name)
    return filter


def exec_filter(frame: types.FrameType, event: str, arg: object) -> bool:
    """
    Ignore a frame running a string executed using exec

    We can't show especially interesting information about it, so we skip it.

    A namedtuple is a common example of this case.
    """
    return frame.f_code.co_filename == "<string>"


def frozen_filter(frame: types.FrameType, event: str, arg: object) -> bool:
    """
    Ignore all frozen modules

    Frozen modules are compiled into the interpreter, so are almost
    always part of the standard library.

    To opt into showing a frozen module, specify it in include_frames.
    """
    return "<frozen " in frame.f_code.co_filename


class LibraryPathFilter:
    """
    Ignore library code

    We want to not show library calls, so attempt to filter them out here.
    """

    __slots__ = ("python_implementation", "system", "paths")

    paths: Tuple[str, ...]

    def __init__(self) -> None:
        # ‘CPython’, ‘IronPython’, ‘Jython’, ‘PyPy’.
        self.python_implementation = platform.python_implementation()

        if self.python_implementation not in ["CPython", "PyPy"]:
            logger.warning(
                "Kolo does not formally support this python_implementation: %s",
                self.python_implementation,
            )  # pragma: no cover

        # 'Linux', 'Darwin', 'Java', 'Windows'. An empty string is returned if the value cannot be determined.
        self.system = platform.system()
        if self.system == "":
            logger.warning(
                "Kolo could not determine the current OS. If you're on Windows, capturing frames may be unreliable."
            )  # pragma: no cover

        # Cache all normalised path fragments.
        # Note: there is potentially a future where we can use `sys.base_prefix`, `sys.exec_prefix`,
        # `sys.prefix`, `sys.path`, and `sys.platlibdir` to amortise some of this further based on the
        # configured platform environment.
        default_paths = (
            os.path.normpath("lib/python"),
            os.path.normpath("/site-packages/"),
        )

        windows_paths = (os.path.normpath("/x64/lib/"),)

        pypy_paths = (
            os.path.normpath("lib/pypy"),
            os.path.normpath("versions/pypy"),
            os.path.normpath("/PyPy/"),
        )

        if self.python_implementation == "PyPy" and self.system == "Windows":
            self.paths = default_paths + windows_paths + pypy_paths  # pragma: no cover
        elif self.system == "Windows":
            self.paths = default_paths + windows_paths
        elif self.python_implementation == "PyPy":
            self.paths = default_paths + pypy_paths
        else:
            self.paths = default_paths

    def __call__(self, frame: types.FrameType, *args, **kwargs) -> bool:
        filepath = frame.f_code.co_filename
        # Avoid any() + a <genexp> and break ASAP, it's marginally faster.
        for path in self.paths:
            if path in filepath:
                return True

        # Something like \python\python310\lib\ on windows
        if self.system == "Windows":
            return (
                "\\python\\" in filepath or "\\Python\\" in filepath or "\\pypy\\"
            ) and ("\\lib\\" in filepath or "\\Lib\\" in filepath)
        else:
            return False


library_filter = LibraryPathFilter().__call__


def module_init_filter(frame: types.FrameType, event: str, arg: object) -> bool:
    return frame.f_code.co_name == "<module>"

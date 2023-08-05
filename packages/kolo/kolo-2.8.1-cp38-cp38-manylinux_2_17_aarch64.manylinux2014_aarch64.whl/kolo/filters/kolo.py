from __future__ import annotations

import os
import types


def kolo_filter(frame: types.FrameType, event: str, arg: object) -> bool:
    """Don't profile kolo code"""
    filename = frame.f_code.co_filename
    paths = ("/kolo/middleware", "/kolo/profiler", "/kolo/serialize")
    return any(os.path.normpath(path) in filename for path in paths)

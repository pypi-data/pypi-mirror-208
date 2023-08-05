from __future__ import annotations

import logging
import os
import sys
import threading
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .config import load_config
from .db import setup_db
from .profiler import KoloProfiler
from .serialize import monkeypatch_queryset_repr

logger = logging.getLogger("kolo")

DjangoView = Callable[[HttpRequest], HttpResponse]


class KoloMiddleware:
    def __init__(self, get_response: DjangoView) -> None:
        self._get_response = get_response
        self.enabled = self.should_enable()
        if self.enabled:
            self.config = load_config()
            self.db_path = setup_db(self.config)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # WARNING: Because Django's runserver uses threading, we need
        # to be careful about thread safety here.
        if not self.enabled or self.check_for_third_party_profiler():
            return self.get_response(request)

        filter_config = self.config.get("filters", {})
        ignore_request_paths = filter_config.get("ignore_request_paths", [])
        for path in ignore_request_paths:
            if path in request.path:
                return self.get_response(request)

        # Don't store the KoloProfiler on self to avoid threadsafety
        # bugs. If a different thread gets this instance of KoloProfiler
        # at the wrong time, we lose the original profiler's trace.
        profiler = KoloProfiler(self.db_path, config=self.config)

        monkeypatch_queryset_repr()
        with profiler:
            response = self.get_response(request)

        name = "kolo-save_request_in_db"
        threading.Thread(target=profiler.save_request_in_db, name=name).start()
        return response

    def get_response(self, request: HttpRequest) -> HttpResponse:
        response = self._get_response(request)
        return response

    def check_for_third_party_profiler(self) -> bool:
        profiler = sys.getprofile()
        if profiler:
            logger.warning("Profiler %s is active, disabling KoloMiddleware", profiler)
            return True
        return False

    def should_enable(self) -> bool:
        if settings.DEBUG is False:
            logger.debug("DEBUG mode is off, disabling KoloMiddleware")
            return False

        if os.environ.get("KOLO_DISABLE", "false").lower() not in ["false", "0"]:
            logger.debug("KOLO_DISABLE is set, disabling KoloMiddleware")
            return False

        if self.check_for_third_party_profiler():
            return False

        return True

#!/usr/bin/env python
# -*- coding:utf-8 -*-
from logging import Filter, LogRecord
from threading import current_thread

from ..cache.manager import CacheManager
from ..config import LogLevel

_TRACE_ID_KEY = "trace_id_map_key"


class _SimpleLogFilter(Filter):
    def __init__(self, level: LogLevel):
        super().__init__()
        self.__level = level

    def filter(self, record: LogRecord) -> bool:
        trace_id = CacheManager.get_data(_TRACE_ID_KEY).get(current_thread().ident)
        record.traceid = trace_id or "%TRACEID%"
        return record.levelno >= self.__level.value


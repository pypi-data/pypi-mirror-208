#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps
from typing import Callable, Tuple, Dict, Any

from ..decorators._process import _do
from ..generic import T
from ..scheduler import Ticker


def ticker_apply(interval: int = 1, num: int = 1) -> T:
    """
    A simple scheduled sync task trigger.
    The task should not be expected to have a return.
    :param interval: task execution interval
    :param num: task run times, less than 0 will always be executed.
    """
    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=ticker_apply.__name__, args=args, kwargs=kwargs,
                       opts={"interval": interval, "num": num, "stacklevel": 7})
        return __wrapper
    return __inner


def ticker_apply_async(interval: int = 1, num: int = 1) -> T:
    """
    A simple scheduled async task trigger.
    The task should not be expected to have a return.
    :param interval: task execution interval
    :param num: task run times, less than 0 will always be executed.
    """
    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=ticker_apply_async.__name__, args=args, kwargs=kwargs,
                       opts={"interval": interval, "num": num, "stacklevel": 7})
        return __wrapper
    return __inner


def __do_ticker_apply(func: Callable, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> Any:
    Ticker(opts.get("interval")).apply(opts.get("num"), func, args or (), kwargs or {})


def __do_ticker_apply_async(func: Callable, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> Any:
    Ticker(opts.get("interval")).apply_async(opts.get("num"), func, args or (), kwargs or {})


__all__ = [ticker_apply, ticker_apply_async]

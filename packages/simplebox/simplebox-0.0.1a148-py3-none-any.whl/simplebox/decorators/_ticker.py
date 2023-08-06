#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps
from typing import Callable, Tuple, Dict, Any, Union

from ..decorators._process import _do
from ..generic import T
from ..scheduler import Ticker


def ticker_apply(*, interval: int = 1, loops: int = -1, end_time: Union[int, float] = None,
                 duration: Union[int, float] = None) -> T:
    """
    A simple scheduled sync task trigger.
    The task should not be expected to have a return.
    :param interval: task execution interval

    The following exit checkpoints will exit execution if any one of them is met.
    :param loops: total run times, if both loops and end_time are specified, the system exits when either is met.
    :param end_time: task end time, if both loops and end_time are specified, the system exits when either is met.
    :param duration: the duration of the task running.

    if the decorated function kwargs contain 'ticker' key, will assign a Ticker object to it.
    usage:
        @ticker_apply_async(interval=2, duration=10)
        def demo(ticker: Ticker = None):
            print("a:", ticker.end_time, ticker.now)
        demo()
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=ticker_apply.__name__, args=args, kwargs=kwargs,
                       opts={"interval": interval, "loops": loops, "end_time": end_time,
                             "duration": duration, "stacklevel": 7})

        return __wrapper

    return __inner


def ticker_apply_async(*, interval: int = 1, loops: int = -1, end_time: Union[int, float] = None,
                       duration: Union[int, float] = None) -> T:
    """
    A simple scheduled async task trigger.
    The task should not be expected to have a return.
    :param interval: task execution interval

    The following exit checkpoints will exit execution if any one of them is met.
    :param loops: total run times, if both loops and end_time are specified, the system exits when either is met.
    :param end_time: task end time, if both loops and end_time are specified, the system exits when either is met.
    :param duration: the duration of the task running.

    if the decorated function kwargs contain 'ticker' key, will assign a Ticker object to it.
    usage:
        @ticker_apply_async(interval=2, duration=10)
        def demo(ticker: Ticker = None):
            print("a:", ticker.end_time, ticker.now)
        demo()
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=ticker_apply_async.__name__, args=args, kwargs=kwargs,
                       opts={"interval": interval, "loops": loops, "end_time": end_time,
                             "duration": duration, "stacklevel": 7})

        return __wrapper

    return __inner


def __do_ticker_apply(func: Callable, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> Any:
    Ticker(interval=opts.get("interval"), loops=opts.get("loops"), end_time=opts.get("end_time"),
           duration=opts.get("duration")).apply_sync(func, args or (), kwargs or {})


def __do_ticker_apply_async(func: Callable, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> Any:
    Ticker(interval=opts.get("interval"), loops=opts.get("loops"), end_time=opts.get("end_time"),
           duration=opts.get("duration")).apply_async(func, args or (), kwargs or {})


__all__ = [ticker_apply, ticker_apply_async]

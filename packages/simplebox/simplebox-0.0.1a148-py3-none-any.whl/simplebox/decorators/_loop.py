#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps
from time import sleep
from typing import Type, Callable, Dict, Tuple, List, Union

from ._process import _do
from ..decorators._hook import _run_hook_func
from ..generic import T, R, U
from ..log import LoggerFactory

__LOGGER = LoggerFactory.get_logger("retry")
_ExceptionTypes = Union[Type[Exception], Tuple[Type[Exception]], None]


def retry(frequency: int = 1, interval: int = 1, increasing: int = 0, check: Callable[[R], bool] = lambda r: True,
          ignored_exception: _ExceptionTypes = None, post: Callable[[R, U], None] = None) -> T:
    """
    Provides retry functionality, if function run success, will run once.
    unit second

    callback functions can and only support communication via the chain keyword parameter. example: callback() is ok,
    callback(chain=None) is ok, callback(chain=None, other=None) is ok(other arg will not be assigned),
    callback(other, chain=None) will happened exception

    :param check: Check whether the result is as expected, return the result if it is met, otherwise try again.
    :param ignored_exception: If it is the exception and its child exceptions, no retry is made
    :param post: If the original function is not executed.Two parameters are required, func_params and func_return
    the callback function is executed and the result of the callback function is returned,
    arguments to the original function are passed to the callback function
    :param frequency: number of executions.
    :param interval: retry interval, unit seconds.
    :param increasing: The incrementing interval

    Usage:
        origin_function(a, b, c=None)
        hook(*args, **kwargs) is ok,
        hook(c=None, *args, **kwargs) is ok,
        hook(a, *args, **kwargs) is ok,
        hook() will happened exception
        hook(a) will happened exception
        hook(c=None) will happened exception

    """

    def _inner(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=retry.__name__, args=args, kwargs=kwargs,
                       opts={"frequency": frequency, "interval": interval, "increasing": increasing, "check": check,
                             "ignored_exception": ignored_exception, "post": post, "stacklevel": 7})

        return _wrapper

    return _inner


def retrying(func: Callable, args: Tuple = None, kwargs: Dict = None,
             frequency: int = 1, interval: int = 1, increasing: int = 0,
             check: Callable[[R], bool] = lambda r: r,
             ignore_exception: _ExceptionTypes = None,
             post: Callable[[R, U], None] = None) -> T:
    """
    if function run success, will run once.
    :param func: The function to be retried.
    :param args: The parameters of the function to be retried must be provided as args.
    :param kwargs: The parameters of the function to be retried must be provided as kwargs.
    :param check: Check whether the result is as expected, return the result if it is met, otherwise try again.
    :param ignore_exception: If it is the exception and its child exceptions, no retry is made
    :param post: If the original function is not executed.Two parameters are required, func_params and func_return
    the callback function is executed and the result of the callback function is returned,
    arguments to the original function are passed to the callback function
    :param frequency: number of executions.
    :param interval: retry interval.
    :param increasing: The incrementing interval
    :return:
    """
    return __do_retry(func, args=args or (), kwargs=kwargs or {},
                      opts={"frequency": frequency, "interval": interval, "increasing": increasing, "check": check,
                            "ignore_exception": ignore_exception, "post": post, "stacklevel": 4})


def repeat(frequency: int = 1, interval: int = 1, increasing: int = 0,
           ignored_exception: _ExceptionTypes = None) -> T:
    """
    Repeat the function, return last result.
    :param frequency: number of executions
    :param interval: the time between executions, unit seconds
    :param increasing: the incrementing interval
    :param ignored_exception:
                if happened exception and exception not included in ignored_exception will interrupt execution
    :return: last execute result
    Usage:
        origin_function(a, b, c=None)
        hook(*args, **kwargs) is ok,
        hook(c=None, *args, **kwargs) is ok,
        hook(a, *args, **kwargs) is ok,
        hook() will happened exception
        hook(a) will happened exception
        hook(c=None) will happened exception
    """

    def _inner(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=repeat.__name__, args=args, kwargs=kwargs,
                       opts={"frequency": frequency, "interval": interval, "increasing": increasing,
                             "ignore_exception": ignored_exception, "stacklevel": 7})

        return _wrapper

    return _inner


def repeating(func, frequency: int = 1, interval: int = 1, increasing: int = 0,
              ignored_exception: _ExceptionTypes = None,
              args: Tuple = None, kwargs: Dict = None) -> T:
    """
    Repeat the function, return last result
    :param func: the function to execute
    :param frequency: number of executions
    :param interval: the time between executions, unit seconds
    :param increasing: the incrementing interval
    :param ignored_exception:
                    if happened exception and exception not included in ignored_exception will interrupt execution
    :param args: func needs args
    :param kwargs: func needs kwargs
    :return: last execute result
    """
    return __do_repeat(func, args=args or (), kwargs=kwargs or {},
                       opts={"frequency": frequency, "interval": interval, "increasing": increasing,
                             "ignore_exception": ignored_exception, "stacklevel": 4})


def __do_retry(func: Callable = None, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> T:
    interval: int = opts.get("interval")
    frequency: int = opts.get("frequency")
    increasing: int = opts.get("increasing")
    ignore_exception: _ExceptionTypes = opts.get("ignore_exception")
    post: Callable[[R, U], None] = opts.get("post")
    check: Callable[[R], bool] = opts.get("check")
    args_ = args or ()
    kwargs_ = kwargs or {}
    for _ in range(1, frequency + 1):
        # noinspection PyBroadException
        try:
            result = func(*args_, **kwargs_)
            if check(result):
                return result
            else:
                __LOGGER.log(level=30, msg=f"check result fail!!!", stacklevel=4)
            __LOGGER.log(level=20, msg=f"run function '{func.__name__}' "
                                       f"fail: retrying {_} time(s)", stacklevel=4)
            sleep(interval)
            interval += increasing
        except BaseException as e:
            e_type = type(e)
            if issubclass(type(ignore_exception), List):
                for e_ in ignore_exception:
                    if not issubclass(e_type, e_):
                        raise
            else:
                if ignore_exception and not issubclass(type(e), ignore_exception):
                    raise
            __LOGGER.log(level=20, msg=f"run function '{func.__name__}' exception {type(e).__name__}: {str(e)}."
                                       f" retrying {_} time(s)", stacklevel=4)
            sleep(interval)
            interval += increasing
    else:
        if post:
            post(*args_, **kwargs_)
            _run_hook_func(post, args, kwargs)


def __do_repeat(func, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> T:
    stacklevel: int = opts.get("stacklevel")
    interval: int = opts.get("interval")
    frequency: int = opts.get("frequency")
    increasing: int = opts.get("increasing")
    ignored_exception: _ExceptionTypes = opts.get("ignored_exception")
    args_ = args or ()
    kwargs_ = kwargs or {}
    result = None
    for _ in range(1, frequency + 1):
        # noinspection PyBroadException
        try:
            result = func(*args_, **kwargs_)
        except BaseException as e:
            __LOGGER.log(level=40, msg=f"run '{func.__name__}(args={args}, kwargs={kwargs})' happened exception, "
                                       f"result={result}, exception={str(e)}, run {_} time(s).", stacklevel=stacklevel)
            if ignored_exception and not issubclass(e.__class__, ignored_exception):
                raise
        finally:
            __LOGGER.log(level=20, msg=f"run '{func.__name__}(args={args}, kwargs={kwargs})', "
                                       f"result={result}, run {_} time(s).", stacklevel=stacklevel)
        if _ == frequency:
            break
        sleep(interval)
        interval += increasing
    return result


__all__ = [retry, retrying, repeat, repeating]

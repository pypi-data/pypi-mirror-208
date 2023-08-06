#!/usr/bin/env python
# -*- coding:utf-8 -*-
from threading import Thread
from time import time, sleep
from typing import Callable, Tuple, Dict, Union

from .._internal._method_helper import func_full_args


class Ticker(object):
    """
    A simple timer.
    """

    def __init__(self, *, interval: int = 1, loops: int = -1, end_time: Union[int, float] = None,
                 duration: Union[int, float] = None):
        """
        A simple scheduled task trigger
        :param interval: The interval for the next execution, in seconds.
        :param loops: total run times, if both loops and end_time are specified, the system exits when either is met.
        :param end_time: task end time, if both loops and end_time are specified, the system exits when either is met.
        :param duration: task run duration time
        """
        if not issubclass(type_ := type(interval), int):
            raise TypeError(f"interval expect type int, got {type_.__name__}")
        if not issubclass(type_ := type(loops), int):
            raise TypeError(f"loops expect type int, got {type_.__name__}")
        if end_time is not None and not issubclass(type_ := type(end_time), (int, float)):
            raise TypeError(f"end_time expect type int or float, got {type_.__name__}")
        if duration is not None and not issubclass(type_ := type(duration), int):
            raise TypeError(f"duration expect type int, got {type_.__name__}")
        self.__start: float = time()
        self.__now: float = self.__start
        self.__interval: int = interval
        self.__current_loops: int = 1
        self.__loops: int = loops
        self.__end_time: Union[int, float, None] = end_time
        self.__duration: Union[int, float, None] = duration
        self.__current_duration: float = 0

    def apply_sync(self, task: Callable = None, args: Tuple = None, kwargs: Dict = None):
        """
        Synchronize execution tasks.
        The task should not be expected to have a return.
        :param task: task FUNCTION.
        :param args: run task need's args.
        :param kwargs: run task need's kwargs. if kwargs contain 'ticker' key, will assign a Ticker object to it.

        if kwargs contain 'ticker' key, will assign a Ticker object to it.
        usage:
            @ticker_apply_async(interval=2, duration=10)
            def demo(ticker: Ticker = None):
                print("a:", ticker.end_time, ticker.now)
            demo()
        """
        all_args = func_full_args(task, args or (), kwargs or {})
        if "ticker" in all_args:
            all_args["ticker"] = self
        if issubclass(type(task), Callable):
            return self.__actuator(task, all_args)
        else:
            return self.__actuator_no_call()

    def apply_async(self, task: Callable = None, args: Tuple = None, kwargs: Dict = None):
        """
        Asynchronous execution of tasks.
        The task should not be expected to have a return.
        :param task: task.
        :param args: task args.
        :param kwargs: task kwargs. if kwargs contain 'ticker' key, will assign a Ticker object to it.

        if kwargs contain 'ticker' key, will assign a Ticker object to it.
        usage:
            @ticker_apply_async(interval=2, duration=10)
            def demo(ticker: Ticker = None):
                print("a:", ticker.end_time, ticker.now)
            demo()
        """
        all_args = func_full_args(task, args or (), kwargs or {})
        if "ticker" in all_args:
            all_args["ticker"] = self
        if issubclass(type(task), Callable):
            ticker_thread = Thread(target=self.__actuator, args=(task, all_args))
        else:
            ticker_thread = Thread(target=self.__actuator_no_call)
        ticker_thread.start()

    def __actuator(self, task: Callable, kwargs):
        sleep(self.__interval)
        if (0 <= self.__loops < self.__current_loops) \
                or (self.__end_time and self.__now > self.__end_time) \
                or (self.__duration and 0 <= self.__duration < self.__current_duration):
            return
        task(**kwargs)
        self.__now = time()
        self.__current_loops += 1
        self.__current_duration += self.__now - self.__start
        return self.__actuator(task, kwargs)

    def __actuator_no_call(self):
        if (0 <= self.__loops < self.__current_loops) \
                or (self.__end_time and self.__now > self.__end_time) \
                or (self.__duration and 0 <= self.__duration < self.__current_duration):
            return
        sleep(self.__interval)
        self.__now = time()
        self.__current_loops += 1
        self.__current_duration += self.__now - self.__start
        return self.__actuator_no_call()

    @property
    def start_time(self) -> float:
        """
        task start run time
        """
        return self.__start

    @property
    def loops(self) -> int:
        """
        The total number of runs.
        """
        return self.__loops

    @property
    def current_loops(self) -> int:
        """
        The current running loop number.
        """
        return self.__current_loops

    @property
    def duration(self) -> float:
        """
        The excepted task run duration time.
        """
        return self.__duration

    @property
    def current_duration(self) -> float:
        """
        The current running duration time.
        :return:
        """
        return self.__current_duration

    @property
    def end_time(self) -> int:
        """
        Get task run end time.
        """
        return self.__end_time

    @property
    def now(self) -> float:
        """
        Current time
        """
        return self.__now


__all__ = [Ticker]

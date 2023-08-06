#!/usr/bin/env python
# -*- coding:utf-8 -*-
from threading import Thread
from time import time, sleep
from typing import Callable, Tuple, Dict


class Ticker(object):
    """
    A simple timer.
    """

    def __init__(self, interval: int = 1):
        """
        A simple scheduled task trigger
        :param interval: The interval for the next execution, in seconds
        """
        self.__now = time()
        self.__interval: int = interval
        self.__next: float = self.__now + self.__interval
        self.__num: int = 1

    def apply(self, num: int = -1, call: Callable = None, args: Tuple = None, kwargs: Dict = None):
        """
        Synchronize execution tasks.
        The task should not be expected to have a return.
        :param num: task run times, less than 0 will always be executed.
        :param call: task.
        :param args: task args.
        :param kwargs: task kwargs.
        """
        if not issubclass(type(num), int):
            raise TypeError(f"expect int, got {type(num).__name__}")
        if issubclass(type(call), Callable):
            return self.__ticker(num, call, args or (), kwargs or {})
        else:
            return self.__ticker_no_call(num)

    def apply_async(self, num: int = -1, call: Callable = None, args: Tuple = None, kwargs: Dict = None):
        """
        Asynchronous execution of tasks.
        The task should not be expected to have a return.
        :param num: task run times, less than 0 will always be executed.
        :param call: task.
        :param args: task args.
        :param kwargs: task kwargs.
        """
        if not issubclass(type(num), int):
            raise TypeError(f"expect int, got {type(num).__name__}")
        if issubclass(type(call), Callable):
            ticker_thread = Thread(target=self.__ticker,
                                   args=(num, call, args or (), kwargs or {}))
        else:
            ticker_thread = Thread(target=self.__ticker_no_call, args=(num,))
        ticker_thread.start()

    def __ticker(self, num: int = None, call: Callable = None, args: Tuple = None, kwargs: Dict = None):
        if 0 <= num < self.__num:
            return
        sleep(self.__interval)
        call(*args, **kwargs)
        timer = Ticker(self.__interval)
        self.__now = timer.__now
        self.__next = timer.__next
        self.__num += 1
        return self.__ticker(num, call, args, kwargs)

    def __ticker_no_call(self, num: int = None):
        if 0 <= num < self.__num:
            return
        sleep(self.__interval)
        timer = Ticker(self.__interval)
        self.__now = timer.__now
        self.__next = timer.__next
        self.__num += 1
        return self.__ticker_no_call(num)

    @property
    def num(self) -> int:
        """
        The current number of runs
        """
        return self.__num

    @property
    def now(self) -> float:
        """
        Current time
        """
        return self.__now


__all__ = [Ticker]

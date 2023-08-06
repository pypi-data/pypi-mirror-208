#!/usr/bin/env python
# -*- coding:utf-8 -*-
import multiprocessing
from contextlib import contextmanager
from multiprocessing.synchronize import RLock as PLock
from threading import RLock as TLock
from typing import Set, TypeVar

from gevent.lock import Semaphore

from ..utils.objects import ObjectsUtils

T = TypeVar("T", TLock, PLock, Semaphore)


class Locksmith(object):
    """
    lock by variable.
    Theoretically, objects can be locked in this way.
    For example, file locking.
    """

    def __init__(self, lock: T):
        self.__free: Set = set()
        self.__using: Set = set()
        self.__lock: T = lock

    def release(self, obj):
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__using.remove(obj)
        self.__free.add(obj)
        self.__lock.release()
        return obj

    def add(self, obj):
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__free.add(obj)
        self.__lock.release()

    def remove(self, obj):
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__using.remove(obj)
        self.__lock.release()

    @contextmanager
    def acquire(self):
        """
        Try to get an object
        """
        obj = None
        try:
            self.__lock.acquire()
            size = len(self.__free)
            if size > 0:
                obj = self.__free.pop()
                self.__using.add(obj)

            self.__lock.release()
            yield obj
        finally:
            if obj is not None:
                self.release(obj)


class _Singleton(type):
    """
    singletons
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LockManager(metaclass=_Singleton):
    """
    Built-in lock type
    """
    # multi processing lock
    PLock: Locksmith = Locksmith(multiprocessing.RLock())
    # multi thread lock
    TLock: Locksmith = Locksmith(TLock())
    # coroutine lock
    CLock: Locksmith = Locksmith(Semaphore(1))


__all__ = [LockManager, Locksmith]

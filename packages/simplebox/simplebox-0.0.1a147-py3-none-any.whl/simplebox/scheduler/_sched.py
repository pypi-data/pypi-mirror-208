#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Callable, Tuple, Dict

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.gevent import GeventExecutor
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from psutil import cpu_count

from ..scheduler._base import CronTriggerExt

_THREAD_POOLS = 20
_PROCESS_POOLS = int(cpu_count() / 2) or 1


class Scheduler:

    def run(self, action: Callable, args: Tuple = None, kwargs: Dict = None):
        """
        Execute the scheduler
        :param action: task
        :param args: list of positional arguments to task with
        :param kwargs: dict of keyword arguments to task with
        """
        scheduler: BaseScheduler = getattr(self, f"_{self.__class__.__name__}__scheduler")
        opts = getattr(self, f"_{self.__class__.__name__}__opts")

        scheduler.add_job(action, **opts, args=args, kwargs=kwargs)
        scheduler.start()


class SchedulerSync(Scheduler):
    """
    When the scheduler is the only thing in your app to run.
    Executor use thread pool.
    """

    def __init__(self, cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        self.__scheduler = BlockingScheduler()
        self.__opts = {"trigger": CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                       "executors": {"default": ThreadPoolExecutor(pools)}}


class SchedulerAsync(Scheduler):
    """
    Used when you're not running any other framework and want the scheduler to execute in the background of your app
    (this is how charging stations use).
    Executor use thread pool.
    """

    def __init__(self, cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        self.__scheduler = BackgroundScheduler()
        self.__opts = {"trigger": CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                       "executors": {"default": ThreadPoolExecutor(pools)}}


class SchedulerSyncProcess(Scheduler):
    """
    When the scheduler is the only thing in your app to run.
    Executor use process pool.
    """

    def __init__(self, cron, pools: int = _PROCESS_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        self.__scheduler = BlockingScheduler()
        self.__opts = {"trigger": CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                       "executors": {"default": ProcessPoolExecutor(pools)}}


class SchedulerAsyncProcess(Scheduler):
    """
    Used when you're not running any other framework and want the scheduler to execute in the background of your app
    (this is how charging stations use).
    Executor use process pool.
    """

    def __init__(self, cron, pools: int = _PROCESS_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        self.__scheduler = BackgroundScheduler()
        self.__opts = {"trigger": CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                       "executors": {"default": ProcessPoolExecutor(pools)}}


class SchedulerAsyncIO(Scheduler):
    """
    Use when your program uses asyncio, an asynchronous framework.
    """

    def __init__(self, cron, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        self.__scheduler = AsyncIOScheduler()
        self.__opts = {"trigger": CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                       "executors": {"default": AsyncIOExecutor()}}


class SchedulerGevent(Scheduler):
    """
    Use when your program uses gevent, the high-performance Python concurrency framework.
    """

    def __init__(self, cron, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        self.__scheduler = GeventScheduler()
        self.__opts = {"trigger": CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                       "executors": {"default": GeventExecutor()}}


__all__ = [Scheduler, SchedulerSync, SchedulerAsync, SchedulerSyncProcess, SchedulerAsyncProcess, SchedulerAsyncIO,
           SchedulerGevent]

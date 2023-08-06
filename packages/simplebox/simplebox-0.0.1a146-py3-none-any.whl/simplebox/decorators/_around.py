#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps
from typing import Tuple, Dict, Callable, TypeVar, Union, List

from ._hook import _run_hook_func
from ._process import _do
from ..generic import T

_TDict = TypeVar("_TDict", bound=Dict)
_Types = Union[Tuple[Callable], List[Callable], Callable, None]


def around(before: _Types = None, after: _Types = None, catch: bool = False) -> T:
    """
    Preform facet operations on functions
    It supports injecting the return value of the preceding hook function into the decorated function
    Support to inject the return value of the decorated function into the post hook function.

    The decorated function can get the return value of the fore hook function through the "func_return" parameter,
    and the after hook function can get the return value of the decorated function via the "func_return" parameter.

    All the parameters of the original function are injected into the hook function.
    example:
        origin_function(a, b, c=None)
        hook(*args, **kwargs) is ok,
        hook(c=None, *args, **kwargs) is ok,
        hook(a, *args, **kwargs) is ok,
        hook() will happened exception
        hook(a) will happened exception
        hook(c=None) will happened exception


    For example:
def setup_module(*args, **kwargs):
    kwargs["chain"]["x"] += 1


def setup_module1(self, *args, **kwargs):
    print(self)


def teardown_module(*args, **kwargs):
    kwargs["chain"]["x"] += 1


class Hook(object):

    @staticmethod
    def setup_static(*args, **kwargs):
        kwargs["chain"]["x"] += 1

    @classmethod
    def setup_class(cls, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    def setup_instance(self, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    @staticmethod
    def teardown_static(*args, **kwargs):
        kwargs["chain"]["x"] += 1

    @classmethod
    def teardown_class(cls, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    def teardown_instance(self, *args, **kwargs):
        kwargs["chain"]["x"] += 1


def retry_hook():
    print("retry hook")


hook = Hook()


class AroundTest(object):

    @staticmethod
    def setup_static(*args, **kwargs):
        kwargs["chain"]["x"] += 1

    @classmethod
    def setup_class(cls, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    def setup_instance(self, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    @staticmethod
    def teardown_static(*args, **kwargs):
        kwargs["chain"]["x"] += 1

    @classmethod
    def teardown_class(cls, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    def teardown_instance(self, *args, **kwargs):
        kwargs["chain"]["x"] += 1

    def retry_hook_instance(self):
        print("retry_hook_instance")

    @classmethod
    def retry_hook_class(cls):
        print("retry_hook_class")

    # @retry(timeout=1, interval=1, post_hook=retry_hook_instance)
    @around(before=[setup_module, setup_module1, hook.setup_static, hook.setup_class, hook.setup_instance, setup_static, setup_class,
                    setup_instance],
            after=[teardown_instance, teardown_class, teardown_static, hook.teardown_instance, hook.teardown_class,
                   hook.teardown_static, teardown_module])
    def case1(self, a, b, *args, e, j=None, chain=None, **kwargs):
        chain["x"] += 1
        # print(1/0)
        return "instance.case1"

    @staticmethod
    @around(before=[setup_module, setup_module1, hook.setup_static, hook.setup_class, hook.setup_instance, setup_static],
            after=[teardown_static, hook.teardown_instance, hook.teardown_class, hook.teardown_static, teardown_module])
    def case2(a, b, *args, e, j=None, chain=None, **kwargs):
        chain["x"] += 1
        return "static.case2"

    @classmethod
    @around(before=[setup_module, setup_module1, hook.setup_static, hook.setup_class, hook.setup_instance, setup_static, setup_class],
            after=[teardown_class, teardown_static, hook.teardown_instance, hook.teardown_class, hook.teardown_static,
                   teardown_module])
    def case3(cls, a, b, *args, e, j=None, chain=None, **kwargs):
        chain["x"] += 1
        return "class.case3"


@around(before=[setup_module, setup_module1, hook.setup_static, hook.setup_class, hook.setup_instance])
def case1(a, b, *args, e, j=None, chain=None, **kwargs):
    chain["x"] += 1
    return "case1"


if __name__ == '__main__':
    chain = {"x": 1}
    result = AroundTest().case1(1, 2, 3, 4, e=5, j=6, h=7, chain=chain)
    assert chain["x"] == 16
    assert result == "instance.case1", result

    chain = {"x": 1}
    result = AroundTest().case2(1, 2, 3, 4, e=5, j=6, h=7, chain=chain)
    assert chain["x"] == 12, chain
    assert result == "static.case2", result

    chain = {"x": 1}
    result = AroundTest().case3(1, 2, 3, 4, e=5, j=6, h=7, chain=chain)
    assert chain["x"] == 14
    assert result == "class.case3", result

    chain = {"x": 1}
    result = AroundTest.case2(1, 2, 3, 4, e=5, j=6, h=7, chain=chain)
    assert chain["x"] == 12
    assert result == "static.case2", result

    chain = {"x": 1}
    result = AroundTest.case3(1, 2, 3, 4, e=5, j=6, h=7, chain=chain)
    assert chain["x"] == 14
    assert result == "class.case3", result

    chain = {"x": 1}
    result = case1(1, 2, 3, 4, e=5, j=6, h=7, chain=chain)
    assert chain["x"] == 6
    assert result == "case1", result


    :param catch: decorated function throw exception when runtime, if True, will catch exception and run hook function,
                    then throw origin exception. If False, throw the exception directly.
                    Valid only for after hook functions.
    :param before:
        Preceding hook function before the decorated function is executed.
        If "before" is a dictionary, the key is the hook function object,
        and the value is the parameter of the hook function.
        When the hook function is executed, it will be passed to the hook function in the form of key value pairs.
        If "before" is a list, it means that the hook function has no parameters.
        If "before" is an executable object, the hook function is directly executed
    :param after:
        Post hook function.
        reference resources @params before
    """
    def _inner(func):
        @wraps(func)
        def _wrapper(*args: Tuple, **kwargs: Dict):
            return _do(func=func, decorator_name=around.__name__, args=args, kwargs=kwargs,
                       opts={"before": before, "after": after, "catch": catch, "args": args, "kwargs": kwargs,
                             "stacklevel": 7})

        return _wrapper

    return _inner


def __do_around(func: Callable, args: Tuple = None, kwargs: Dict = None, opts: Dict = None):
    args_ = args or ()
    kwargs_ = kwargs or {}
    _run_hook_func(opts.get("before"), args, kwargs)
    # noinspection PyBroadException
    try:
        result = func(*args_, **kwargs_)
        return result
    except BaseException:
        if not opts.get("catch"):
            raise
    finally:
        _run_hook_func(opts.get("after"), args, kwargs)


__all__ = [around]

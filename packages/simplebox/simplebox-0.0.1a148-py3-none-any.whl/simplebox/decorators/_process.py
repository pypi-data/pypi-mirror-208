#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from typing import Any, Dict

from . import _DecoratorsCache, decorators_name_key, decorators_impl_map_key
from ._tools import AstTools


def _do(func, decorator_name, args, kwargs, opts: Dict = None) -> Any:
    """
    Decorator master. Assign the executor of the decorator.
    :param func: origin function.
    :param decorator_name: the name of the decorator on the function.
    :param args: origin function's args.
    :param kwargs: origin function's kwargs.
    :return: origin function return value
    """
    func_full_name: str = func.__qualname__
    module = sys.modules[func.__module__]
    if "." in func_full_name:
        class_name = func_full_name.split(".")[0]
        clz = getattr(module, class_name, None)
    else:
        clz = func
    if clz is None:
        raise ValueError("method's class is None")
    decorator_name_list_tmp = []
    if _DecoratorsCache.has_cache(func):
        decorator_name_list_tmp = _DecoratorsCache.get(func)
    else:
        decorator_name_list = AstTools(clz).get_decorator_of_function_by_name(func.__name__)
        if not decorator_name_list:
            return func(*args, **kwargs)
        for decorator in decorator_name_list:
            if decorator in _DecoratorsCache.get(decorators_name_key):
                decorator_name_list_tmp.append(decorator)
        _DecoratorsCache.put(func, decorator_name_list_tmp)
    process_map = _DecoratorsCache.get(decorators_impl_map_key).get(decorator_name, {})
    for decorator_func, _ in process_map.items():
        process_map[decorator_func] = opts
        break
    result = None
    if decorator_name_list_tmp and decorator_name_list_tmp[-1] == decorator_name:
        for decorator in decorator_name_list_tmp:
            process_map: Dict = _DecoratorsCache.get(decorators_impl_map_key)[decorator]
            for decorator_func, decorator_func_opts in process_map.items():
                result = decorator_func(func, args=args, kwargs=kwargs, opts=decorator_func_opts)
                break
    else:
        result = func(*args, **kwargs)
    return result

#!/usr/bin/env python
# -*- coding:utf-8 -*-
from inspect import getfullargspec
from typing import Callable, Dict, List, Tuple, Iterable


def _run_hook_func(call_obj: Iterable[Callable] or Callable, args: Tuple, kwargs: Dict) -> Dict:
    if not call_obj:
        return {}
    call_list = []
    if issubclass(type(call_obj), Iterable):
        call_list.extend(call_obj)
    else:
        call_list.append(call_obj)
    for call in call_list:
        func_type_name = type(call).__name__
        hook_args = []
        if func_type_name == "function":
            assert callable(call), f"'{func_type_name}' not a callable"
            __hook_params(call, hook_args, args)
            call(*hook_args, **kwargs)
        elif func_type_name == "method":
            assert callable(call), f"'{func_type_name}' not a callable"
            __hook_params(call, hook_args, args)
            call(*hook_args, **kwargs)
        else:
            assert hasattr(call, "__func__"), f"'{func_type_name}' not a callable"
            __hook_params(call.__func__, hook_args, args)
            call.__func__(*hook_args, **kwargs)


def __hook_params(call: Callable, hook_args: List, args: Tuple):
    spec = getfullargspec(call)
    start_index = 0
    if len(spec.args) > 0:
        if len(args) > 0:
            call_qualname = call.__qualname__
            class_name = None
            if "." in call_qualname:
                class_name = call_qualname.split(".")[0]
            instance = args[0]
            if isinstance(instance, type):
                if class_name == instance.__name__:
                    hook_args.append(instance)
                    start_index = 1
            else:
                if class_name == type(instance).__name__:
                    hook_args.append(instance)
                    start_index = 1

        for arg in args[start_index:]:
            hook_args.append(arg)


def _build_new_params(kwargs: Dict) -> (List, Dict):
    t_args = []
    if "args" in kwargs:
        t_args = kwargs.pop("args")
    t_kwargs = {}
    if "kwargs" in kwargs:
        t_kwargs.update(kwargs.pop("kwargs"))
    t_kwargs.update(kwargs)
    return t_args, t_kwargs

#!/usr/bin/env python
# -*- coding:utf-8 -*-
from inspect import getfullargspec
from typing import Callable, Tuple, Dict, List

_SELF, _CLS = "self", "cls"


def func_full_args(func: Callable, args: Tuple, kwargs: Dict) -> Dict:
    new_params = {}
    func_spec = getfullargspec(func)

    tmp_arg_names = func_spec.args
    tmp_arg_values = __copy_args(args)
    tmp_kwarg_kvs = __copy_kwargs(kwargs)
    if len(args) > 0:
        if len(func_spec.args) > 0:
            if (func_spec.args[0] == _SELF and func.__qualname__.split(".")[0] == args[0].__class__.__name__) or \
                    (func_spec.args[0] == _CLS and func.__qualname__.split(".")[0] == args[0].__name__):
                new_params[func_spec.args[0]] = args[0]
        else:
            # noinspection PyBroadException
            try:
                if func.__qualname__.split(".")[0] == args[0].__class__.__name__ or func.__qualname__.split(".")[0] == \
                        args[0].__name__:
                    if isinstance(args[0], type):
                        new_params[_CLS] = args[0]
                    else:
                        new_params[_SELF] = args[0]
            except BaseException:
                pass
    tmp_arg_names_len = len(tmp_arg_names)
    if func_spec.defaults and len(tmp_arg_values) < tmp_arg_names_len:
        diff = tmp_arg_names_len - len(tmp_arg_values)
        tmp_arg_values.extend(func_spec.defaults[:diff])
    choice_args_values = tmp_arg_values[:len(tmp_arg_names)]
    no_choice_values = tmp_arg_values[len(tmp_arg_names):]

    choice_args_values_len = len(choice_args_values)
    if tmp_arg_names_len > choice_args_values_len:
        diff_num = tmp_arg_names_len - choice_args_values_len
        for i in range(diff_num, tmp_arg_names_len):
            value = tmp_kwarg_kvs.get(tmp_arg_names[i])
            choice_args_values.insert(i, value)
            k = tmp_arg_names[i]
            if k in tmp_kwarg_kvs:
                del tmp_kwarg_kvs[k]
    new_params.update(dict(zip(tmp_arg_names, choice_args_values)))  # 添加位置参数kv
    for k, v in new_params.items():
        if k in tmp_kwarg_kvs:
            new_params[k] = tmp_kwarg_kvs.get(k)
            del tmp_kwarg_kvs[k]
    kw_defaults = func_spec.kwonlydefaults
    if not kw_defaults:
        kw_defaults = {}
    kw_defaults_keys = kw_defaults.keys()
    must_need_value_keys = [i for i in func_spec.kwonlyargs if i not in kw_defaults_keys]
    for key in kw_defaults_keys:
        if key in kwargs:
            new_params[key] = kwargs[key]
            del tmp_kwarg_kvs[key]
        else:
            new_params[key] = kw_defaults[key]
    for key in must_need_value_keys:
        if key not in new_params and key in kwargs:
            new_params[key] = kwargs[key]
            del tmp_kwarg_kvs[key]
        else:
            new_params[key] = None
    if func_spec.varargs:
        new_params[func_spec.varargs] = no_choice_values
    if func_spec.varkw:
        new_params[func_spec.varkw] = tmp_kwarg_kvs
    return new_params


def __copy_args(args: Tuple or List) -> List:
    if args is None:
        return []
    tmp_args = []
    tmp_args_append = tmp_args.append
    for arg in args:
        tmp_args_append(arg)
    return tmp_args


def __copy_kwargs(kwargs: Dict) -> Dict:
    if kwargs is None:
        return {}
    tmp_kwargs = {}
    for k, v in kwargs.items():
        tmp_kwargs[k] = v
    return tmp_kwargs

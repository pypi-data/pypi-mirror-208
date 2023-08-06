#!/usr/bin/env python
# -*- coding:utf-8 -*-
from datetime import datetime
from functools import wraps
from typing import List, Callable, Tuple, Dict, Type, Optional, Union, Any

from ._process import _do
from .._internal._method_helper import func_full_args
from ..classes import ForceType
from ..generic import T
from ..valid import StringValidator, CompareValidator, MemberValidator, Validator, ValidatorExecutor

_RETURN = "return"


class Valid(object):
    name = ForceType(str)
    compare = ForceType(CompareValidator, None)
    string = ForceType(StringValidator, None)
    contain = ForceType(MemberValidator, None)
    contained = ForceType(MemberValidator, None)
    datetime_format = ForceType(str, None)
    empty = ForceType(bool, None)
    notEmpty = ForceType(bool, None)
    types = ForceType(Tuple[Type, ...], None)
    validators = ForceType(Tuple[Validator, ...], ValidatorExecutor, None)

    def __init__(self, name: str, compare: Optional[CompareValidator] = None, string: Optional[StringValidator] = None,
                 contain: Optional[MemberValidator] = None,
                 contained: Optional[MemberValidator] = None,
                 datetime_format: Optional[str] = None, empty: bool = False, notEmpty: bool = False,
                 types: Optional[Tuple[Type, ...]] = None,
                 validators: Union[Tuple[Validator, ...], ValidatorExecutor, None] = None):
        """
        A metadata object that validates the validity of the parameter.
        :param name: Parameter name. if name is 'return', 'Valid' will apply to the return value.
        :param compare: Verify that the length of the parameter is the same as expected.
        :param string: Verify that the string of the parameter.
        :param contain: Verify that the parameter contains this option. # a in b
        :param contained: Verify that the option (iterable) contains parameters. b in a
        :param datetime_format: If the parameter is time, verifies that the time is in the specified format.
        :param types: Verify whether the parameter's type
        :param validators: custom validator object
        """
        self.name: str = name
        self.compare: Optional[CompareValidator] = compare
        self.string: Optional[StringValidator] = string
        self.contain: Optional[MemberValidator] = contain
        self.contained: Optional[MemberValidator] = contained
        self.datetime_format: Optional[str] = datetime_format
        self.empty: Optional[bool] = empty
        self.notEmpty: Optional[bool] = notEmpty
        self.types: Optional[Tuple[Type, ...]] = types
        if types:
            self.__types_names: List[str] = [t.__name__ for t in types]
        else:
            self.__types_names = []
        self.validators: Union[Tuple[Validator, ...], ValidatorExecutor, None] = validators

    @property
    def type_names(self) -> List[str]:
        return self.__types_names


def validate(*conditions: Valid) -> T:
    """
    Parameters to the validation method/function.
    :param conditions: Validation conditions, a collection of instances of Valid
    Example:
        # 1.check name in between Jerry and Tom
        class Person:

            @validate(Valid(name="name", contained=MemberValidator(in_=["Jerry", "Tom"])))
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tom = Person(10, "Tom")
        tom = Person(10, "Jack") # raise exception

        # 2.check age between 1 and 10(contains 1 and 10)
        class Person:

            @validate(Valid(name="name", compare=CompareValidator(le=10, ge=1)))
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(5, "Tony")
        tony = Person(-1, "Tony")  # raise exception
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return _do(func=func, decorator_name=validate.__name__, args=args, kwargs=kwargs, opts={"conditions": conditions, "stacklevel": 7})

        return __wrapper

    return __inner


def __do_validate(func: Callable, args: Tuple = None, kwargs: Dict = None, opts: Dict = None) -> Any:
    args_ = args or ()
    kwargs_ = kwargs or {}
    func_parameters = func_full_args(func, args_, kwargs_)
    return_validators = []
    return_validators_append = return_validators.append
    for valid in opts.get("conditions", []):
        if not isinstance(valid, Valid):
            raise TypeError(f"valid check metadata type error , excepted type '{Valid.__name__}', "
                            f"got a '{type(valid).__name__}'")
        if _RETURN == valid.name.strip().lower():
            return_validators_append(valid)
            continue
        parameter = func_parameters.get(valid.name)
        _valid_process(valid, parameter)

    result = func(*args_, **kwargs_)
    for valid in return_validators:
        _valid_process(valid, result)
    return result


def _valid_process(valid: Valid, value: Any):
    if valid.empty:
        assert not value, f"valid check parameter '{valid.name}' is empty, but '{valid.name}=({value})' is not empty."
    if valid.notEmpty:
        assert value, f"valid check parameter '{valid.name}' is not empty, but '{valid.name}=({value})' is empty."
    if valid.types is not None:
        assert issubclass(value_type := type(value), valid.types), \
            f"valid check parameter '{valid.name}' type, expected '{valid.type_names}', got '{value_type.__name__}'"
    if valid.compare is not None:
        valid.compare.validate(value)
    if valid.contain is not None:
        ori_kw = valid.contain.operators
        kw = {k.name: value for k, v in valid.contain.operators.items()}
        MemberValidator(**kw).validate(list(ori_kw.values())[0])
    if valid.contained is not None:
        valid.contained.validate(value)
    if valid.datetime_format is not None:
        try:
            datetime.strptime(value, valid.datetime_format)
            result = True
        except ValueError:
            result = False
        assert result, f"Valid '{valid.name}' datetime format check: expected datetime format " \
                       f"'{valid.datetime_format}', got '{value}'"
    if valid.validators is not None:
        if issubclass(type(valid.validators), tuple):
            for validator in valid.validators:
                if issubclass(validator_type := type(validator), Validator):
                    validator.validate(value, f"Valid function '{valid.name}': ")
                else:
                    raise TypeError(f"Valid '{valid.name}' type error: excepted {Validator.__name__} type, "
                                    f"got a {validator_type.__name__} type")
        else:
            valid.validators.validate(value, f"Valid function '{valid.name}': ")


__all__ = ["validate", "Valid"]

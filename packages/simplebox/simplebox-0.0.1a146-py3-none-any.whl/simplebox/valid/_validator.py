#!/usr/bin/env python
# -*- coding:utf-8 -*-
import operator
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Callable, Optional, Iterable, Any, Type, Set, List, Union

from ..classes import ForceType
from ..enums import EnhanceEnum
from ..exceptions import ValidatorException
from ..utils.strings import StringUtils


class _Symbols(EnhanceEnum):
    eq = "=="
    ne = "!="
    le = "<="
    lt = "<"
    ge = ">="
    gt = ">"
    is_ = "is"
    is_not = "is not"
    in_ = "in"
    not_in = "not in"


class Validator(ABC):
    """
    Custom validators need to inherit from Validator
    and must supply a validate() method to test various restrictions as needed.
    """

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value, message: str = None):
        pass


class ValidatorExecutor(Validator):
    """
    Execute multiple validators.
    Example:
        class Person:
            age = ValidatorExecutor(TypeValidator(int, float), CompareValidator(ge=1, le=10))
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(-1, "Tony")  # raise exception
    """

    def __init__(self, *validators: Validator):
        self.__validators: Tuple[Validator] = validators

    def validate(self, value, message: str = None):
        for validator in self.__validators:
            validator.validate(value, message)


class CompareValidator(Validator):
    """
    Compare operation checks
    Example:
        class Person:
            age = CompareValidator(ge=1, le=10)
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(-1, "Tony")  # raise exception
    """

    def __init__(self, eq: Any = None, ne: Any = None, le: Any = None, lt: Any = None, ge: Any = None, gt: Any = None):
        self.__operators = {_Symbols.eq: eq, _Symbols.ne: ne, _Symbols.lt: lt, _Symbols.le: le, _Symbols.ge: ge,
                            _Symbols.gt: gt}
        self.__operators = {k: v for k, v in self.__operators.items() if v is not None}

    def validate(self, value, message: str = None):
        for operate, obj in self.__operators.items():
            operate_ = f"__{operate.name}__"
            symbol = operate.value
            _check(not hasattr(obj, operate_) or not hasattr(value, operate_), message,
                   ValidatorException(f"Valid error: '{obj}' have not '{operate}' implemented."))
            _check((value_type := type(value)) != (obj_type := type(obj)), message, TypeError(
                f"Valid error: '{value_type.__name__}' and '{obj_type.__name__}' cannot be '{symbol}'"))
            result = getattr(operator, operate.name)(value, obj)
            _check(not result, message,
                   ValidatorException(f"Valid error: CompareValidator fail: excepted '{value}' {symbol} '{obj}', "
                                      f"but actual check fail."))


class IdentityValidator(Validator):
    """
    Identity validator
    Example:
            class Person:
                age = IdentityValidator(is_=-1)
                def __init__(self, age, name):
                    self.age = age
                    self.name = name


            tony = Person(-1, "Tony")  # success
            tony = Person(1, "Tony")   # raise exception, 1 is not -1
    """

    def __init__(self, is_: Any = None, is_not: Any = None):
        self.__operators = {_Symbols.is_: is_, _Symbols.is_not: is_not}
        self.__operators = {k: v for k, v in self.__operators.items() if v is not None}

    def validate(self, value, message: str = None):
        _check(_Symbols.is_ in self.__operators and _Symbols.is_not in self.__operators, message, ValidatorException(
            f"Valid error: '{_Symbols.is_.value}' and '{_Symbols.is_not.value}' cannot exist at the same time."))
        for operate, obj in self.__operators.items():
            result = getattr(operator, operate.name)(value, obj)
            _check(not result, message,
                   ValidatorException(f"Valid error: Excepted '{value}' {operate.value} '{obj}', but check fail."))


class MemberValidator(Validator):
    """
    Member validators. Parameters are members of validators.
    Example:
        class Person:
            age = MemberValidator(in_=(1, 2, 3))
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(1, "Tony")  # success
        tony = Person(-1, "Tony")  # raise exception, -1 not in (1, 2, 3)

    """

    def __init__(self, in_: Optional[Iterable] = None, not_in: Optional[Iterable] = None):
        self.__operators = {_Symbols.in_: in_, _Symbols.not_in: not_in}
        self.__operators = {k: v for k, v in self.__operators.items() if v is not None}

    @property
    def operators(self) -> dict:
        return self.__operators

    def validate(self, value, message: str = None):
        _check(_Symbols.in_ in self.__operators and _Symbols.not_in in self.__operators, message,
               ValidatorException(f"Valid error: '{_Symbols.in_.value}' and '{_Symbols.not_in.value}'"
                                  f" cannot exist at the same time."))
        for operate, obj in self.__operators.items():
            result = getattr(operator, "contains")(obj, value)
            if operate == _Symbols.not_in:
                result = not result
            _check(not result, message,
                   ValidatorException(f"Valid error: Excepted '{value}' {operate.value} '{obj}', but check fail."))


class StringValidator(Validator):
    """
    verifies that a value is a str.
    Optionally, it validates a given minimum or maximum length. It can validate a user-defined predicate as well.
    Usage:
        class Person:
        name = StringValidator(minsize=2, maxsize=3, prefix="A")
        def __init__(self, age, name):
            self.age = age
            self.name = name


        tony = Person(1, "Ami")  # success
        tony = Person(1, "Tom")  # raise exception, prefix is not 'A'
        tony = Person(1, "Alice")  # raise exception, max size great than 3
    """
    __min = ForceType(int, None)
    __max = ForceType(int, None)
    __prefix = ForceType(str, None)
    __suffix = ForceType(str, None)
    __predicate = ForceType(Callable[[Any], bool], None)
    __empty = ForceType(bool, None)
    __black = ForceType(bool, None)

    def __init__(self, minsize: Optional[int] = None, maxsize: Optional[int] = None, prefix: Optional[str] = None,
                 suffix: Optional[str] = None, predicate: Optional[Callable[[Any], bool]] = None,
                 empty: Union[bool] = False, black: Union[bool] = False):
        self.__min = minsize
        self.__max = maxsize
        if self.__max < self.__min:
            self.__min, self.__max = self.__max, self.__min
        self.__prefix = prefix
        self.__suffix = suffix
        self.__predicate = predicate
        self.__empty = empty
        self.__black = black

    def validate(self, value, message: str = None):
        _check(not isinstance(value, str), message, TypeError(f'Valid error: Expected {value!r} to be an str'))
        v_len = len(value)
        _check(self.__min is not None and v_len <= self.__min, message, ValidatorException(
            f'Valid error: Expected {value!r} to be no smaller than {self.__min!r}'
        ))
        _check(self.__max is not None and v_len >= self.__max, message, ValidatorException(
            f'Valid error: Expected {value!r} to be no bigger than {self.__max!r}'
        ))
        _check(self.__prefix is not None and not value.startswith(self.__prefix), message,
               ValidatorException(f"Valid error: Expected '{value}' prefix is {self.__prefix}, but check fail."))
        _check(self.__suffix is not None and not value.endswith(self.__suffix), message,
               ValidatorException(f"Valid error: Expected '{value}' suffix is {self.__suffix}, but check fail."))
        _check(self.__predicate is not None and not self.__predicate(value), message, ValidatorException(
            f'Valid error: Expected {self.__predicate} to be true for {value!r}'
        ))
        _check(self.__black and StringUtils.is_not_black(value), message,
               ValidatorException(f"Valid error: Excepted black, but got a '{value}'"))
        _check(self.__empty and StringUtils.is_not_empty(value), message,
               ValidatorException(f"Valid error: Excepted empty, but got a '{value}'"))


class TypeValidator(Validator):
    """
    verifies that a value type in types.
    Usage:
        class Person:
            age = TypeValidator(float, int)
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(1, "Ami")  # success
        tony = Person(2.0, "Ami") # success
        tony = Person("3", "Ami")  # raise exception
    """

    def __init__(self, *types: Optional[Type]):
        self.__none_type: Set[None] = set()
        self.__can_none: bool = False
        self.__types: Set[Type] = set()
        self.__type_names: List[str] = []
        self.__type_names_append = self.__type_names.append
        for t in types:
            if t is None:
                self.__none_type.add(t)
                self.__can_none = True
                self.__type_names_append("NoneType")
            elif not isinstance(t, type):
                raise ValidatorException(f"Valid error: Excepted 'type' object, got a '{t}' from {types}")
            else:
                self.__types.add(t)
                self.__type_names_append(t.__name__)

    def validate(self, value, message: str = None):
        _check(not issubclass(value_type := type(value), tuple(self.__types)) or (self.__can_none and value is not None), message,
               ValidatorException(f"Valid error: Expected type \"{self.__type_names}\", got type '{value_type.__name__}'"))


class BoolValidator(Validator):
    """
    bool validator.
    "", [], {}, (), None, 0, False => False
    """

    __true = ForceType(bool, None)

    def __init__(self, true: bool = False):
        self.__true = true

    def validate(self, value, message: str = None):
        if self.__true:
            _check(self.__true, message,
                   ValidatorException(f"Valid error: Excepted true, but false."))
        else:
            _check(value, message, ValidatorException(f"Valid error: Excepted false, but true."))


class DatetimeValidator(Validator):
    """
    datetime validator
    """
    __format = ForceType(str, None)
    __future = ForceType(bool, None)
    __past = ForceType(bool, None)

    def __init__(self, format: str = None, future: bool = False, past: bool = False):
        self.__format = format
        self.__future = future
        self.__past = past

    def validate(self, value, message: str = None):
        now_ = datetime.now()
        if isinstance(value, datetime):
            difference = (value - now_).microseconds
        elif isinstance(value, str):
            _check(not self.__format, message, ValidatorException(f"Valid error: datetime format is must required."))
            difference = (datetime.strptime(value, self.__format) - datetime.strptime(now_, self.__format)).microseconds
        elif isinstance(value, (float, int)):
            difference = value - time.time()
        else:
            difference = 0
        _check(self.__future and difference < 0, message,
               ValidatorException(f"Valid error: Excepted datetime is after, got a before datetime: {value}"))
        _check(self.__past and difference > 0, message,
               ValidatorException(f"Valid error: Excepted datetime is before, got a after datetime: {value}"))


class IterableValidator(Validator):
    """
    IterableValidator. A validator is a member of a parameter.
    iterable's element must be hashable.
    """

    __has = ForceType(Iterable, None)
    __has_no = ForceType(Iterable, None)
    __eq = ForceType(Iterable, None)
    __ne = ForceType(Iterable, None)

    def __init__(self, has: Iterable = None, has_no: Iterable = None, eq: Iterable = None, ne: Iterable = None):
        self.__has: Iterable = has
        self.__has_no: Iterable = has_no
        self.__eq: Iterable = eq
        self.__ne: Iterable = ne

    def validate(self, value, message: str = None):
        if not issubclass(value_type := type(value), Iterable):
            raise TypeError(f"Excepted type 'Iterable', got a '{value_type.__name__}'")

        _check(self.__ne is not None and self.__eq is not None, message,
               ValidatorException(f"Cannot be both equal and unequal."))
        _check(self.__has is not None and self.__has_no is not None, message,
               ValidatorException(f"Cannot be both have and no."))
        _check(self.__eq is not None and not self.__eq == value, message,
               ValidatorException(f"Check '{value}' == '{self.__eq}' fail."))
        _check(self.__ne is not None and not self.__ne != value, message,
               ValidatorException(f"Check '{value}' != '{self.__eq}' fail."))
        _check(self.__has is not None and self.__has not in value, message,
               ValidatorException(f"Check '{self.__has}' in '{value}' fail."))
        _check(self.__has_no is not None and self.__has_no in value, message,
               ValidatorException(f"Check '{value}' not in '{self.__has_no}' fail."))


def _check(condition, message, default_exception):
    if condition:
        if message:
            msg = message
            msg += " : ".join(default_exception.args)
            default_exception.args = (msg,)
            raise default_exception
        else:
            raise default_exception


__all__ = ["Validator", "ValidatorExecutor", "CompareValidator", "IdentityValidator", "MemberValidator",
           "StringValidator", "TypeValidator", "BoolValidator", "DatetimeValidator", "IterableValidator"]

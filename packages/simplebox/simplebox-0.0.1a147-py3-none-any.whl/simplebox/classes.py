#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
from types import GenericAlias
from typing import Tuple, Type, _Final, List, Optional

from .exceptions import raise_exception, InstanceException

__all__ = ['ForceType', 'StaticClass', 'Final', 'ConstructorIntercept']


class ForceType(object):
    """
    Given a type as the type of a variable, an exception is thrown if the assigned type is inconsistent with that type.

    Excample:
        class Person:
            age = ForceType(int) # ForceType(int, bool)
            name = ForceType(str)

            def __init__(self, age, name):
                self.age = age
                self.name = name

        tony = Person(15, 'Tony')
        tony.age = '15'  # raise exception
    """

    def __init__(self, *types: Optional[Type]):
        self.__can_none = False
        self.__types: List[Type] = []
        self.__types_append = self.__types.append
        self.__types_name = []
        self.__types_name_append = self.__types_name.append
        for t in types:
            if t is None:  # NoneType begin with Python version 3.10+
                self.__can_none = True
                self.__types_name_append("NoneType")
            elif issubclass(t_ := (type(t)), type):
                self.__types_append(t)
                self.__types_name_append(self.__get__name(t))
            elif issubclass(t_, _Final):
                self.__types_append(getattr(t, "__origin__"))
                self.__types_name_append(self.__get__name(t))
            elif issubclass(t_, GenericAlias):
                t_g_alias = type(t())
                self.__types_append(t_g_alias)
                self.__types_name_append(t_g_alias.__name__)
            else:
                raise TypeError(f"expected 'type' type class, but found '{t_.__name__}'")
        self.__types: Tuple[Type, ...] = tuple(self.__types)

    @staticmethod
    def __get__name(t: Type) -> str:
        if issubclass(type(t), _Final):
            return getattr(t, "_name") or getattr(getattr(t, "__origin__"), "__name__")
        else:
            return t.__name__

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set_name__(self, cls, name):
        self.name = name

    def __set__(self, instance, value):
        value_type = type(value)
        if issubclass(value_type, self.__types) or (self.__can_none and value is None):
            instance.__dict__[self.name] = value
        else:
            raise TypeError(f"expected {self.__types_name}, got '{value_type.__name__}'")


class StaticClass(type):
    """
    Create a class that cannot be instantiated
    Example:
        Class Foo(metaclass=StaticClass):
            pass
        Foo() # raise exception
    """

    def __call__(cls, *args, **kwargs):
        raise_exception(InstanceException(f"Class '{cls.__name__}' cannot be instantiated!!!"))


class Final(type):
    """
    Classes that are prohibited from being inherited.
    usage:

        class People(metaclass=Final):
            pass


        class Child(People):
            pass

        compile and run python script  # raise exception: type 'People' is not an acceptable base type
    """

    def __new__(mcs, name, bases, dict, *args, **kwargs):
        for base in bases:
            if isinstance(base, Final):
                raise TypeError("type '{0}' is not an acceptable base type".format(base.__name__))
        return super().__new__(mcs, name, bases, dict, **kwargs)


class ConstructorIntercept(type):
    """
    Some classes are not allowed to be accessed or instantiated externally,
    so use ConstructorIntercept to decorate classes that need to be restricted.
    For example, providing services externally through the wrapper function

    Subclasses will also be affected, i.e. subclasses also need to be instantiated together in the current file,
    otherwise an exception will be thrown
    usage:
        producer.py
            class People(metaclass=ConstructorIntercept):
                pass

            class Child(People):
                pass

            # no exception
            def init_wrapper():
                // Instantiate class People
                // do something
                // return

        consumer.py
            // Instantiate class People  #  raise exception


    """

    def __call__(cls, *args, **kwargs):
        stack = inspect.stack()[1]
        if __file__ != stack.filename:
            raise RuntimeError(f"Initialization error. No instantiation functionality is provided externally")
        return type.__call__(cls, *args, **kwargs)

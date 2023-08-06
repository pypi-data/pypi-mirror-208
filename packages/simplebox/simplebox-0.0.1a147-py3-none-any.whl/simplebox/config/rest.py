#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Union, Optional

from ..singleton import SingletonMeta

B = Union[bool, str]


class __RestConfig(metaclass=SingletonMeta):
    """
    Rest  global configuration
    """

    def __init__(self):
        self.__allow_redirection = True
        self.__check_status = False
        self.__encoding = "utf-8"

    @property
    def allow_redirection(self) -> bool:
        return self.__allow_redirection

    @allow_redirection.setter
    def allow_redirection(self, value: B):
        self.__set_allow_redirection(value)

    def __set_allow_redirection(self, value: B):
        if issubclass(v_type := (type(value)), bool):
            self.__allow_redirection = value
        elif issubclass(v_type, str):
            self.__allow_redirection = _to_bool(value, True)

    @property
    def check_status(self) -> bool:
        return self.__check_status

    @check_status.setter
    def check_status(self, value: B):
        self.__set_check_status(value)

    def __set_check_status(self, value: B):
        if issubclass(v_type := (type(value)), bool):
            self.__check_status = value
        elif issubclass(v_type, str):
            self.__check_status = _to_bool(value, False)

    @property
    def encoding(self) -> str:
        return self.__encoding

    @encoding.setter
    def encoding(self, value: Optional[str]):
        self.__set_encoding(value)

    def __set_encoding(self, value: Optional[str]):
        if issubclass(type(value), str):
            self.__encoding = value


def _to_bool(value: str, default: bool = False) -> bool:
    """
    Converts the string bool type to a true bool type.
    :param value: string bool type.
    :param default: If it is not of type string bool, the value returned by default.
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value == "True" or value == "true":
            return True
        elif value == "False" or value == "false":
            return False
    return default


RestConfig: __RestConfig = __RestConfig()

__all__ = [RestConfig]

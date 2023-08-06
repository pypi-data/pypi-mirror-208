#!/usr/bin/env python
# -*- coding:utf-8 -*-

from jsonpath import jsonpath
from operator import contains, eq, ne, lt, le, ge, gt, not_, truth, is_, is_not

from .collection.collectors import Stream
from .void import Void


class JsonOperator(object):
    """
    Make quick judgments on JSON results
    """

    def __init__(self, obj):
        self.__obj = obj
        self.__obj_str = str(self.__obj)

    def __repr__(self):
        return self.__obj_str

    def __str__(self):
        return self.__obj_str

    @property
    def value(self):
        return self.__obj

    def has(self, value) -> bool:
        return contains(self.__obj, value)

    def not_has(self, value) -> bool:
        return not self.has(value)

    def eq(self, value) -> bool:
        return eq(self.__obj, value)

    def ne(self, value) -> bool:
        return ne(self.__obj, value)

    def lt(self, value) -> bool:
        return lt(self.__obj, value)

    def le(self, value) -> bool:
        return le(self.__obj, value)

    def ge(self, value) -> bool:
        return ge(self.__obj, value)

    def gt(self, value) -> bool:
        return gt(self.__obj, value)

    @property
    def false(self) -> bool:
        """
        Return the outcome of not self.__obj. (Note that there is no __not__() method for object instances;
        only the interpreter core defines this operation.
        The result is affected by the __bool__() and __len__() methods.)
        means self.__obj expression equal false
        example:
            self.__obj = False
            instance.false will return True
        """
        return not_(self.__obj)

    @property
    def true(self) -> bool:
        """
        Return True if obj is true, and False otherwise. This is equivalent to using the bool constructor.
        means self.__obj expression equal true
        example:
            self.__obj = True
            instance.True will return True
        """
        return truth(self.__obj)

    def is_(self, value) -> bool:
        """
        Return self.__obj is value. Tests object identity.
        """
        return is_(self.__obj, value)

    def is_not(self, value) -> bool:
        """
        Return self.__obj is not value. Tests object identity.
        """
        return is_not(self.__obj, value)


class JsonParser(object):
    """
    Parsing json, the result always returns List
    """

    def __init__(self, json):
        self.__json = json

    def parser(self, path):
        """
        Parse JSON
        """
        return JsonContainer(self.__json, path)


class JsonContainer(JsonOperator):

    def __init__(self, obj, path):
        self.__path = path
        self.__obj = jsonpath(obj, path)
        self.__obj = [] if self.__obj is False else self.__obj
        super().__init__(self.__obj)

    def index(self, index: int = 0):
        """
        Get value from list.
        Because parsing results is always list, sometimes only the only result can be obtained directly.
        """
        length = len(self.__obj)
        return JsonOperator(self.__obj[index if length > index else length - 1]) \
            if self.__obj and length > 0 else JsonOperator(Void())

    def parser(self, path):
        """
        Parse JSON.
        """
        return JsonContainer(self.__obj, path)

    @property
    def stream(self) -> Stream:
        """
        To Stream()
        """
        return Stream.of_item(self.__obj)


__all__ = [JsonParser, JsonOperator, JsonContainer]

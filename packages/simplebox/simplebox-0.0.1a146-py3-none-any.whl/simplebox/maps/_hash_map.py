#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Dict, Callable, overload

from ..collection.collectors import Stream
from ..generic import V, K
from ..maps._map import Map


class HashMap(Map[K, V]):

    @overload
    def __init__(self):
        self.__init__(kwargs={}, factory=None)

    @overload
    def __init__(self, factory: Callable = None):
        self.__init__(factory=factory)

    @overload
    def __init__(self, kwargs: Dict):
        self.__init__(kwargs)

    @overload
    def __init__(self, kwargs: Dict, factory: Callable = None):
        self.__init__(kwargs=kwargs, factory=factory)

    @overload
    def __init__(self, **kwargs):
        self.__init__(kwargs=kwargs)

    @overload
    def __init__(self, factory: Callable = None, **kwargs):
        self.__init__(factory=factory, kwargs=kwargs)

    def __init__(self, kwargs: Dict[K, V] = None, factory: Callable = None, **kw):
        """
        The factory is called without arguments to produce
        a new value when a key is not present, in __getitem__ only.
        A HashMap compares equal to a dict with the same items.
        All remaining arguments are treated the same as if they were
        passed to the dict constructor, including keyword arguments.
        """
        self.__factory = factory
        m = {} if kwargs is None else kwargs
        m.update(kw)
        super().__init__(m)

    def __delitem__(self, key):
        if self.contain_key(key):
            super().__delitem__(key)
        else:
            raise KeyError(f"not found '{key}' in {self}")

    def __setitem__(self, key: K, value: V):
        super().__setitem__(key, value)

    def __getitem__(self, key: K) -> V:
        v = super(HashMap, self).__getitem__(key)
        if v is None:
            v = self.__factory()
        return v

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"

    def merge(self, other: Dict[K, V]) -> 'HashMap[K, V]':
        return HashMap(dict(self, **other))

    def update(self, other: Dict[K, V], **kwargs: [K, V]) -> 'HashMap[K, V]':
        if isinstance(other, Dict):
            self.update(other)
        self.update(kwargs)
        return self

    def put(self, key: K, value: V) -> V:
        v = self.get(key)
        super().__setitem__(key, value)
        return v

    def put_if_absent(self, key: K, value: V) -> V:
        v = self.get(key)
        if key not in self:
            super(HashMap, self).__setitem__(key, value)
        return v

    def remove(self, key: K, default: V = None) -> V:
        return super().pop(key, default)

    def remove_value_none(self) -> 'HashMap[K, V]':
        return self.remove_if_predicate(lambda k, v: v is None)

    def remove_if_predicate(self, predicate: Callable[[K, V], bool]) -> 'HashMap[K, V]':
        rm = HashMap()
        for k, v in self.items():
            if predicate(k, v):
                rm[k] = v
                del self[k]
        return rm

    def size(self) -> int:
        return len(self)

    def items(self) -> Stream[(K, V)]:
        return super(HashMap, self).items()

    def keys(self) -> Stream[K]:
        return super(HashMap, self).keys()

    def values(self) -> Stream[V]:
        return super(HashMap, self).values()

    def contain_key(self, key):
        return key in self.keys()

    def contain_value(self, value):
        return value in self.values()

    def for_each(self, action: Callable[[K, V], None]):
        for k, v in self.items():
            action(k, v)


__all__ = [HashMap]

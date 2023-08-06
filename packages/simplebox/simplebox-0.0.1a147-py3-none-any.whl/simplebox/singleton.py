#!/usr/bin/env python
# -*- coding:utf-8 -*-

class SingletonMeta(type):
    __INSTANCES = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__INSTANCES:
            cls.__INSTANCES[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__INSTANCES[cls]


class Singleton(metaclass=SingletonMeta):
    """
    singletons base class
    classes that need to implement singletons only need to inherit Singleton
    usage:
        class Foo(Singleton):
            def __init__(self, name):
                self.name = name
        f1 = Foo("f1")
        f2 = Foo("f2)
        assert id(f1) == id(f2)
        assert f1.name == f2.name
        assert f1.name == "f1"
        assert f2.name == "f1"
    """

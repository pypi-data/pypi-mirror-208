#!/usr/bin/env python
# -*- coding:utf-8 -*-
import ujson as json
import os
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Optional, Union, Any, Generic, Dict, List

from dataclasses_json import dataclass_json, Undefined

from ._tools import AstTools
from ..config import PropertyConfig
from ..exceptions import ValidatorException
from ..generic import T
from ..singleton import SingletonMeta

_ENTITY_TYPE = "EntityType"
_PROPERTY_SOURCE = "PropertySource"


class Entity(Generic[T]):
    """
    All entities need to inherit the entire class.
    """

    @classmethod
    def get(cls: T):
        """
        get entity instance.
        it's singleton, the instance is automatically managed.
        """
        return _process(cls.get, cls)

    @classmethod
    def get_from_dict(cls: T, from_dict: Dict, fixed: bool = False):
        """
        create a temp entity instance from dict,
        if fixed is True, it will be managed by the manager, then use get() method.
        """
        return _process(cls.get_from_dict, cls, from_dict, fixed)

    @classmethod
    def get_from_json(cls: T, from_json: str, fixed: bool = False):
        """
        create a temp entity instance from json string,
        if fixed is True, it will be managed by the manager, then use get() method.
        """
        return _process(cls.get_from_json, cls, from_json, fixed)


class _PropertiesManager(metaclass=SingletonMeta):
    __lock = RLock()

    def __init__(self):
        self.__cache = {}

    def push(self, cls: T, instance: T):
        with self.__lock:
            self.__cache[cls] = instance

    def pull(self, cls: T, default: Any = None) -> T:
        with self.__lock:
            instance = self.__cache.get(cls)
            if instance:
                return instance
            return default


def EntityType(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=True, letter_case=None,
               undefined: Optional[Union[str, Undefined]] = None) -> T:
    """
    Tag entity classes.

    If init is true, an __init__() method is added to the class. If
    repr is true, a __repr__() method is added. If order is true, rich
    comparison dunder methods are added. If unsafe_hash is true, a
    __hash__() method function is added. If frozen is true, fields may
    not be assigned to after instance creation. If match_args is true,
    the __match_args__ tuple is added. If kw_only is true, then by
    default all fields are keyword-only. If slots is true, an
    __slots__ attribute is added.

    Usage:
        @Entry()
        class Student(Entity):
            name: str
            age: int
    """

    def __wrapper(cls):
        _check_entity(cls, True)
        return _build(cls, init=init, repr_=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                      frozen=frozen, letter_case=letter_case, undefined=undefined)

    return __wrapper


def PropertySource(path: Union[Path, str] = None, coding: str = "utf-8", from_dict: Dict = None):
    """
    Ingress entity tags that automatically assemble attribute values.
    :param from_dict: if not None, will use from_dict to entity and ignore path.
    :param path:  file path.
    If the path is not absolute, the resources path will be read from the PropertyConfig for concatenation.
    If the path is not a file, the name of the entity class is used as the config file name.
    If the given file does not exist, an exception is thrown.
    path default PropertyConfig.resources and file name is entity class-name.
    :param coding:  file encoding。
    If the read file has garbled characters, attempts to read the file using the specified encoding.
    coding default utf-8.
    Usage:
        scene 1:
            @EntryType()  # Tag sub-property type
            class Student(Entity):
                name: str
                age: int

            @Properties("properties.json")  # property content file path.
            @EntryType()  # Tag property object.
            class Class(Entity):
                students: list[Student]
                teacher: str

            #  properties.json file content
            {"teacher": "Alice", "students": [{"name": "Tom", "age": 20}]}

            c: Class = Class.init()  # Entity create by init method.
            print(c.teacher)  # Alice
            print(c.students)  # [Student(name="Tom", age=20)]
            print(c.students[0].name)  # Tome


        scene 2(force type check):
            @EntryType()  # Tag sub-property type
            class Student(Entity):
                name: str
                age: int = ForceType(int)  # Force variable type validation

            @Properties("properties.json")  # property content file path.
            @EntryType()  # Tag property object.
            class Class(Entity):
                students: list[Student]
                teacher: str

            #  properties.json file content, age use string number, will assignment failed
            {"teacher": "Alice", "students": [{"name": "Tom", "age": "20"}]}

            c: Class = Class.init()  # Entity create by init method.
            print(c.teacher)  # Alice
            print(c.students)  # []  Because the variable type verification of the Student fails,
                                     all Students are not instantiated successfully.
            print(c.students[0].name)  # IndexError: list index out of range

    """

    def __inner(cls):
        _check_entity(cls)
        if isinstance(from_dict, Dict):
            instance = cls.from_dict(from_dict)
            _PropertiesManager().push(cls, instance)
        else:
            default_name = cls.__name__ + ".json"
            if path is None:
                pathway = PropertyConfig.resources.joinpath(default_name)
            elif issubclass(path_type := type(path), (str, bytes, os.PathLike)):
                pathway = Path(path)
            else:
                raise TypeError(f"Excepted type is str, bytes, os.PathLike, got {path_type.__name__}")

            if not pathway.is_absolute():
                tmp = PropertyConfig.resources.joinpath(pathway).absolute()
                if tmp.is_dir():
                    path_ = str(tmp.joinpath(default_name))
                else:
                    path_ = str(tmp)
            elif pathway.is_dir():
                path_ = str(pathway.joinpath(default_name))
            else:
                path_ = str(pathway)

            if not Path(path_).exists():
                raise ValueError(f"'{path}' not exists.")

            with open(path_, "r", encoding=coding) as f:
                data = json.load(f)
                instance = cls.from_dict(data)
                _PropertiesManager().push(cls, instance)
        return cls

    return __inner


def _check_entity(cls, only_entity: bool = False):
    class_name = cls.__name__
    decorators: List = AstTools(cls).get_decorator_of_class_by_name(class_name)
    if not decorators or _ENTITY_TYPE not in decorators:
        raise ValidatorException(f"{class_name}' decorator wrong:'{class_name}' must be decorated '{_ENTITY_TYPE}'.")
    if decorators.count(_ENTITY_TYPE) != 1:
        raise ValidatorException(f"{class_name}' decorator number wrong: '{_ENTITY_TYPE}' "
                                 f"decorator can only have one, but '{class_name}' found multiple.")
    if not only_entity:
        if decorators.count(_PROPERTY_SOURCE) != 1:
            raise ValidatorException(f"'{class_name}' decorator number wrong: '{_PROPERTY_SOURCE}' "
                                     f"decorator can only have one, but '{class_name}' found multiple.")
        if decorators.index(_PROPERTY_SOURCE) > decorators.index(_ENTITY_TYPE):
            raise ValidatorException(f"'{class_name}' decorator sequence wrong: '{_PROPERTY_SOURCE}' "
                                     f"must precede '{_ENTITY_TYPE}'")


def _build(cls, init=True, repr_=True, eq=True, order=False, unsafe_hash=False, frozen=True, letter_case=None,
           undefined: Optional[Union[str, Undefined]] = None):
    return dataclass_json(dataclass(cls, init=init, repr=repr_, eq=eq, order=order, unsafe_hash=unsafe_hash,
                                    frozen=frozen), letter_case=letter_case, undefined=undefined)


def _process(action, cls, data: Dict or str = None, fixed: bool = False) -> T:
    if action == cls.get:
        return _PropertiesManager().pull(cls)
    elif action == cls.get_from_dict:
        _check_entity(cls, True)
        entity = cls.from_dict(data)
        if fixed:
            _PropertiesManager().push(cls, entity)
        return entity
    elif action == cls.get_from_json:
        _check_entity(cls, True)
        entity = cls.from_json(data)
        if fixed:
            _PropertiesManager().push(cls, entity)
        return entity


__all__ = ["Entity", "PropertySource", "EntityType"]

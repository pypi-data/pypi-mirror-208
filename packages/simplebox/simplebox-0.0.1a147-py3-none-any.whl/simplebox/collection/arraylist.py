#!/usr/bin/env python
# -*- coding:utf-8 -*-
from bisect import bisect, bisect_left, insort, insort_right, insort_left, bisect_right
from typing import Iterable, List

from .collectors import Stream
from ..generic import T
from ..utils.optionals import Optionals


class ArrayList(List[T]):
    """
    A superset of list, which mainly adds streaming operations
    """

    def __init__(self, iterable: Iterable[T] = None):
        """
        Initialization by ArrayList.of() or ArrayList.of_item()
        """
        if iterable is None:
            iterable = []
        super(ArrayList, self).__init__(iterable)

    @staticmethod
    def of(*args: T) -> 'ArrayList[T]':
        return ArrayList(args)

    @staticmethod
    def of_item(iterable: Iterable[T]) -> 'ArrayList[T]':
        return ArrayList(iterable)

    @staticmethod
    def empty() -> 'ArrayList[T]':
        return ArrayList()

    @property
    def stream(self) -> Stream[T]:
        return Stream.of_item(self)

    def get(self, index: int) -> Optionals[T]:
        """
        Gets the element that specifies the subscript
        :param index:
        :return:
        """
        if 0 <= index <= len(self):
            return Optionals.of_none_able(self[index])
        return Optionals.empty()

    def bisect(self, element, lo: int = 0, hi: int = None):
        """
        Similar to bisect_left(), but returns an insertion point which comes after (to the right of) any existing
        entries of x in a.

        The returned insertion point i partitions the array a into two halves so that all(val <= x for val in a[lo:i])
        for the left side and all(val > x for val in a[i:hi]) for the right side.
        """
        return bisect(self, element, lo=lo, hi=hi if hi is not None else len(self))

    def bisect_left(self, element, lo: int = 0, hi: int = None):
        """
        Locate the insertion point for x in a to maintain sorted order. The parameters lo and hi may be used to
        specify a subset of the list which should be considered; by default the entire list is used.
        If x is already present in a, the insertion point will be before (to the left of) any existing entries.
        The return value is suitable for use as the first parameter to list.insert() assuming that a is already sorted.

        The returned insertion point i partitions the array a into two halves so that all(val < x for val in a[lo:i])
        for the left side and all(val >= x for val in a[i:hi]) for the right side.
        """
        return bisect_left(self, element, lo=lo, hi=hi if hi is not None else len(self))

    def bisect_right(self, element, lo: int = 0, hi: int = None):
        return bisect_right(self, element, lo=lo, hi=hi if hi is not None else len(self))

    def insort(self, element, lo: int = 0, hi: int = None):
        """
        Similar to insort_left(), but inserting x in a after any existing entries of x.
        """
        return insort(self, element, lo=lo, hi=hi if hi is not None else len(self))

    def insort_left(self, element, lo: int = 0, hi: int = None):
        """
        Insert x in a in sorted order. This is equivalent to a.insert(bisect.bisect_left(a, x, lo, hi), x) assuming
        that a is already sorted. Keep in mind that the O(log n) search is dominated by the slow O(n) insertion step.
        """
        return insort_left(self, element, lo=lo, hi=hi if hi is not None else len(self))

    def insort_right(self, element, lo: int = 0, hi: int = None):
        return insort_right(self, element, lo=lo, hi=hi if hi is not None else len(self))


__all__ = [ArrayList]

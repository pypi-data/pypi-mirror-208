#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Void:
    """
    Represents an empty or useless object
    """
    def __str__(self):
        return Void.__name__

    def __repr__(self):
        return Void.__name__

    def __next__(self):
        raise StopIteration

    def __bool__(self):
        return False

    def __contains__(self, item):
        return False

    def __len__(self):
        return 0

    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __ne__(self, other):
        return False

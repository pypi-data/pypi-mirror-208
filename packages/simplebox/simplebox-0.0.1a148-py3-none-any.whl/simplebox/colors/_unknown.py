#!/usr/bin/env python
# -*- coding:utf-8 -*-
import warnings
import platform
from enum import Enum

"""
unknown platform use print() function
"""


_PLATFORM_NAME = platform.system()


class ForegroundColor(Enum):
    BLACK = None
    BLUE = None
    GREEN = None
    SKYBLUE = None
    RED = None
    PINK = None
    YELLOW = None
    WHITE = None


class BackgroundColor(Enum):
    BLACK = None
    BLACK_HIGHLIGHT = None
    BLUE = None
    BLUE_HIGHLIGHT = None
    GREEN = None
    GREEN_HIGHLIGHT = None
    SKYBLUE = None
    SKYBLUE_HIGHLIGHT = None
    RED = None
    RED_HIGHLIGHT = None
    PINK = None
    PINK_HIGHLIGHT = None
    YELLOW = None
    YELLOW_HIGHLIGHT = None
    WHITE = None
    WHITE_HIGHLIGHT = None


def dye(content, fc: ForegroundColor, bc: BackgroundColor = BackgroundColor.BLACK):
    warnings.warn(f"color output not support platform: {_PLATFORM_NAME}, use print() function.", category=RuntimeWarning, stacklevel=1, source=None)
    print(content)

__all__ = []

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ctypes
import sys
from enum import Enum

STD_INPUT_HANDLE = ctypes.windll.kernel32.GetStdHandle(-10)
STD_OUTPUT_HANDLE = ctypes.windll.kernel32.GetStdHandle(-11)
STD_ERROR_HANDLE = ctypes.windll.kernel32.GetStdHandle(-12)


class ForegroundColor(Enum):
    BLACK = 0x00
    BLUE = 0x01
    GREEN = 0x02
    SKYBLUE = 0x03
    RED = 0x04
    PINK = 0x05
    YELLOW = 0x06
    WHITE = 0x07


class BackgroundColor(Enum):
    BLACK = 0
    BLACK_HIGHLIGHT = 0x80
    BLUE = 0x10
    BLUE_HIGHLIGHT = 0x90
    GREEN = 0x20
    GREEN_HIGHLIGHT = 0xa0
    SKYBLUE = 0x30
    SKYBLUE_HIGHLIGHT = 0xb0
    RED = 0x40
    RED_HIGHLIGHT = 0xc0
    PINK = 0x50
    PINK_HIGHLIGHT = 0xd0
    YELLOW = 0x60
    YELLOW_HIGHLIGHT = 0xe0
    WHITE = 0x70
    WHITE_HIGHLIGHT = 0xf0


def dye(content, fc: ForegroundColor, bc: BackgroundColor = BackgroundColor.BLACK):
    ctypes.windll.kernel32.SetConsoleTextAttribute(STD_OUTPUT_HANDLE, bc.value | fc.value)
    sys.stdout.write(content + "\n")
    sys.stdout.flush()
    ctypes.windll.kernel32.SetConsoleTextAttribute(STD_OUTPUT_HANDLE,
                                                   ForegroundColor.RED.value | ForegroundColor.GREEN.value | ForegroundColor.BLUE.value)


__all__ = []

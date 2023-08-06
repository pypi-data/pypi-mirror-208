#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from enum import Enum


class ForegroundColor(Enum):
    BLACK = "30"
    BLUE = "34"
    GREEN = "32"
    SKYBLUE = "36"
    RED = "31"
    PINK = "35"
    YELLOW = "33"
    WHITE = "37"


class BackgroundColor(Enum):
    BLACK = "0;{};40"
    BLACK_HIGHLIGHT = "1;{};40"
    BLUE = "0;{};44"
    BLUE_HIGHLIGHT = "1;{};44"
    GREEN = "0;{};42"
    GREEN_HIGHLIGHT = "1;{};42"
    SKYBLUE = "0;{};46"
    SKYBLUE_HIGHLIGHT = "1;{};46"
    RED = "0;{};41"
    RED_HIGHLIGHT = "1;{};41"
    PINK = "0;{};45"
    PINK_HIGHLIGHT = "1;{};45"
    YELLOW = "0;{};43"
    YELLOW_HIGHLIGHT = "1;{};43"
    WHITE = "0;{};47"
    WHITE_HIGHLIGHT = "1;{};47"


def dye(content, fc: ForegroundColor, bc: BackgroundColor = BackgroundColor.BLACK):
    fcontent = f"\033[{bc.value.format(fc.value)}m{content}\033[0m"
    sys.stdout.write(fcontent + "\n")
    sys.stdout.flush()


__all__ = []

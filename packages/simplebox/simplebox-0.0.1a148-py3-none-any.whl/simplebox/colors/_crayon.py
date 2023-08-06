#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform

_PLATFORM_NAME = platform.system()
if _PLATFORM_NAME == "Windows":
    from ._windows import ForegroundColor, BackgroundColor, dye
elif _PLATFORM_NAME == "Linux":
    from ._linux import ForegroundColor, BackgroundColor, dye
else:
    from ._unknown import ForegroundColor, BackgroundColor, dye


def crayon(content, fc: ForegroundColor = ForegroundColor.WHITE, bg: BackgroundColor = BackgroundColor.BLACK):
    """
    A simple terminal color output tool. if you need more advanced color display, you need to implement it yourself.
    :param content: will output text
    :param fc: text color
    :param bg: text background color,default Black
    """
    dye(content, fc, bg)


__all__ = [ForegroundColor, BackgroundColor, crayon]

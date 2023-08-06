#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

from apscheduler.triggers.cron.expressions import AllExpression


class UnknownExpression(AllExpression):
    value_re = re.compile(r'\?(?:/(?P<step>\d+))?$')


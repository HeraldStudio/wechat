# -*- coding:utf-8 -*-
import time


def getHour():
    d = time.localtime(time.time())
    h = d.tm_hour % 24
    return h


def getWeekDay():
    d = time.localtime(time.time())
    w = d.tm_wday + 1 + d.tm_hour / 24
    w %= 7
    if w == 0:
        return 7
    else:
        return w


def getMin():
    d = time.localtime(time.time())
    return d.tm_min

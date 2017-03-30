# -*- coding: utf-8 -*-
# @Date    : 2014-06-29 17:16:08
# @Author  : xindervella@gamil.com yml_bright@163.com
from time import time, localtime, strftime


def today():
    return strftime('%a', localtime(time()))


def tomorrow():
    return strftime('%a', localtime(time() + 24 * 3600))

def changedate():
    if int(strftime('%H', localtime(time())))>=19:
        return tomorrow()
    else:
        return today()

def ismorning():
    if 5<=int(strftime('%H', localtime(time())))<=8:
        return True
    else:
        return False

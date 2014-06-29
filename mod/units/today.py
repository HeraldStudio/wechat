# -*- coding: utf-8 -*-
# @Date    : 2014-06-29 17:16:08
# @Author  : xindervella@gamil.com
from time import time, localtime, strftime


def today():
    return strftime('%a', localtime(time()))

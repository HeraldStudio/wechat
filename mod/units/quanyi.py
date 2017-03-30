#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-03 12:53:44
# @Author  : yml_bright@163.com


from ..models.message import Messsage
from time import localtime, strftime
import base64

def quanyi(db, user):
    msg = u'<a href="https://jinshuju.net/f/By3aTK">点我向校会权益投诉</a>\n\n'
    try:
        message = db.query(Messsage).filter( Messsage.openid == 'quanyi').one()
        if message.state:
            #msg += u'[%s]\n'%strftime('%Y-%m-%d %H:%M', localtime(message.timestamp))
            msg += '%s'%base64.b64decode(message.message).decode('utf8')
    except:
        msg += u'没有什么新的动态'
    finally:
        msg += u'\n\n<a href="https://jinshuju.net/s/VeyDUV">戳我查询投诉结果与动态</a>'
        return msg
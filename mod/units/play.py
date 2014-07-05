# -*- coding: utf-8 -*-
# @Date    : 2014-07-05 22:43:49
# @Author  : xindervella@gamil.com
from tornado.httpclient import HTTPRequest, HTTPClient
from config import SERVICE, TIME_OUT
import urllib


def update(db, user):

    if user.state == 0:
        user.state = 1
        try:
            db.commit()
            return u'come on!'
        except:
            db.rollback()
            return u'T T 出了点小问题，要不你再试试？'
    elif user.state == 1:
        user.state = 0
        try:
            db.commit()
            return u'bye~~'
        except:
            db.rollback()
            return u'T T 出了点小问题，要不你再试试？'


def simsimi(content):
    client = HTTPClient()
    params = urllib.urlencode({
        'msg': content.encode('utf-8')
    })
    request = HTTPRequest(SERVICE + 'simsimi', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except:
        return u'=。= 出了点小问题啊'
    if response.body == 'time out':
        return u'=。= 出了点小问题啊'
    elif response.body == 'error':
        return u'=。= 我看不懂你说什么'
    else:
        msg = ''.join(response.body.split(' '))
        return msg

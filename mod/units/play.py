# -*- coding: utf-8 -*-
# @Date    : 2014-07-05 22:43:49
# @Author  : xindervella@gamil.com yml_bright@163.com
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from config import SERVICE, TIME_OUT, DEFAULT_UUID
from get_api_return import error_map
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


def simsimi(content, user):
    client = HTTPClient()
    if user.uuid:
        uuid = user.uuid
    else:
        uuid = DEFAULT_UUID
    params = urllib.urlencode({
        'uuid': uuid,
        'msg': content.encode('utf-8')
    })
    request = HTTPRequest(SERVICE + 'simsimi', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except HTTPError as e:
        return error_map[e.code]
    if response.body == 'error':
        return u'=。= 坏掉了'
    else:
        return response.body

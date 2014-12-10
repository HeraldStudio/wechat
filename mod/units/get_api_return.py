#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-12-10 19:56:54
# @Author  : yml_bright@163.com

from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from config import LOCAL, SERVICE, TIME_OUT
import urllib, json

error_map = {
        599 : u'=。= 暂时无法连接，不如待会再试试',        # time out
        408 : u'=。= 暂时无法连接，不如待会再试试',        # returned time out
        404 : u'=。= 暂时无法连接，请联系小猴君',         # access denied
        400 : u'=。= 后台接口错误，请联系小猴君',         # params error
        401 : u'<a href="%s/register/%s">你不是把一卡通密码输错了吧，快点我修改。</a>',                     
                                                     # uuid error
        500 : u'=。= 出了点故障，不如待会再试试吧',        # server error
    }

def get_api_return(api_name, user):
    ret = {}
    client = HTTPClient()
    params = urllib.urlencode({'uuid': user.uuid})
    request = HTTPRequest(SERVICE + api_name, method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
        ret = json.loads(response.body)
        if ret['code'] == 200:
            return ret
        ret['content'] = error_map[ret['code']]
    except HTTPError as e:
        ret['code'] = e.code
        if ret['code'] == 401:
            ret['content'] = error_map[401] % (LOCAL, user.openid)
        else:
            ret['content'] = error_map[ret['code']]
    except:
        ret['code'] = 500
        ret['content'] = u'=。= 服务器未能及时回应请求，如不再试试'
    return ret


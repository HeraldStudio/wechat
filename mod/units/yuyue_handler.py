#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-09-23 18:38:13
# @Author  : jerry.liang.qq.com

import tornado.web
from ..models.user import User
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from config import SERVICE,TIME_OUT
import urllib

class yuyueHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        self.db.close()

    def get(self,openid):
        user = self.db.query(User).filter(User.openid == openid).one()
        data = {'uuid':user.uuid}
        print user.uuid
        try:
            client = HTTPClient()
            request = HTTPRequest(
                SERVICE+'yuyue',
                method='POST',
                body=urllib.urlencode(data),
                request_timeout=8)
            response = client.fetch(request)
            print response.body
            # cookie = 'iPlanetDirectoryPro=AQIC5wM2LY4SfcyCBSsUYTXSZN9cSsO5Rcsnt6EAOv9pQoo%3D%40AAJTSQACMDI%3D%23'
            self.render('yuyue.html',cookie=response.body,openid=openid)
            # self.render('yuyue.html',cookie=cookie,openid=openid)
            # self.write(response.body)
        except HTTPError as e:
            code = e.code
            print code
            self.write('密码错误T_T，请返回修改密码~')
            self.finish()
    def post(self,openid):
        url = self.get_argument('url')
        recookie = self.get_argument('cookie')
        retype = self.get_argument('type')
        data = {}
        #判断请求是否合法
        if retype == '1':
            itemId = self.get_argument('itemId')
            dayInfo = self.get_argument('dayInfo')
            time = self.get_argument('time')
            data = {
                'itemId':itemId,
                'dayInfo':dayInfo,
                'time':time
            }
        client = HTTPClient()
        request = HTTPRequest(
            url,
            method='POST',
            body=urllib.urlencode(data),
            headers = {
                'Cookie':recookie
            },
            request_timeout=8)
        response = client.fetch(request)
        self.write(response.body)
        print response.body
        self.finish()



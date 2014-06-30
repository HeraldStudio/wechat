# -*- coding: utf-8 -*-
# @Date    : 2014-06-30 19:28:08
# @Author  : xindervella@gamil.com
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from config import RENEW, TIME_OUT
from sqlalchemy.orm.exc import NoResultFound
from ..models.user import User
import tornado.web
import tornado.gen
import urllib
import json

TEMPLATE = '<center><h1 style="margin-top:30%">{content}</h2></center>'


class RenewHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, openid, barcode):
        try:
            user = self.db.query(User).filter(User.openid == openid).one()
            params = urllib.urlencode({
                'username': user.lib_username,
                'password': user.lib_password,
                'barcode': barcode
            })
            client = AsyncHTTPClient()
            request = HTTPRequest(RENEW, method='POST', body=params,
                                  request_timeout=TIME_OUT)
            response = yield tornado.gen.Task(client.fetch, request)
            if (not response.headers) or response.body == 'server error':
                self.write(TEMPLATE.format(content='=。= 又宕机了，待会再试试吧'))
            elif response.body == 'username or password error':
                self.write(TEMPLATE.format(content='=。= 同学，用户名/密码错了吧'))
            else:
                result = json.loads(response.body)
                if result['result']:
                    self.write(TEMPLATE.format(content='续借成功'))
                elif not result['result']:
                    self.write(TEMPLATE.format(content='现在不是可以续借的时间哦'))
        except NoResultFound:
            self.write('access verification fail')
        finally:
            self.finish()

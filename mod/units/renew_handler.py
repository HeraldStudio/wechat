# -*- coding: utf-8 -*-
# @Date    : 2014-06-30 19:28:08
# @Author  : xindervella@gamil.com yml_bright@163.com
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from config import SERVICE, TIME_OUT
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
            self.db.close()

            params = urllib.urlencode({
                'uuid': user.uuid,
                'barcode': barcode
            })
            client = AsyncHTTPClient()
            request = HTTPRequest(SERVICE + 'renew', method='POST', body=params,
                                  request_timeout=TIME_OUT)
            response = yield tornado.gen.Task(client.fetch, request)
            if (not response.headers) or response.body == 'error':
                self.write(TEMPLATE.format(content='=。= 又宕机了，待会再试试吧'))
            elif response.body == 'wrong card number or password':
                self.write(TEMPLATE.format(content='=。= 同学，用户名/密码错了吧'))
            else:
                if response.body == 'success':
                    self.write(TEMPLATE.format(content='续借成功'))
                else:
                    self.write(TEMPLATE.format(content='现在不是可以续借的时间哦'))
        except NoResultFound:
            self.write('access verification fail')
        finally:
            self.finish()

    def on_finish(self):
        self.db.close()

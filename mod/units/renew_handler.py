# -*- coding: utf-8 -*-
# @Date    : 2014-06-30 19:28:08
# @Author  : xindervella@gamil.com yml_bright@163.com

from sqlalchemy.orm.exc import NoResultFound
from ..models.user import User
from get_api_return import get_api_return
import tornado.web
import tornado.gen

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
            
            data = { 'barcode': barcode }
            response = get_api_return('renew', user, data)

            if response['code'] == 200:
                if response['content'] == 'success':
                    self.write(TEMPLATE.format(content='续借成功'))
                else:
                    self.write(TEMPLATE.format(content='现在不是可以续借的时间哦'))
            else:
                self.write(response['content'])
        except NoResultFound:
            self.write('access verification fail')
        finally:
            self.finish()

    def on_finish(self):
        self.db.close()

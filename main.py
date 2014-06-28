# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:16:23
# @Author  : xindervella@gamil.com

from sqlalchemy.orm import scoped_session, sessionmaker
from mod.models.db import engine
from mod.user.user_handler import UserHandler
from tornado.httpclient import HTTPRequest, HTTPClient
from mod.models.user import User
from config import SERVICE, TERM, TIME_OUT
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.gen
import urllib
import wechat
import json
import os

from tornado.options import define, options
define('port', default=7000, help='run on the given port', type=int)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/wechat/', WechatHandler),
            (r'/register/([\S]+)/', UserHandler)
        ]
        settings = dict(
            cookie_secret="7CA71A57B571B5AEAC5E64C6042415DE",
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = scoped_session(sessionmaker(bind=engine))


class WechatHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self):
        self.wx = wechat.Message(token='herald')
        if self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default='')):
            self.write(self.get_argument('echostr'))
        else:
            self.write('access verification fail')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        self.wx = wechat.Message(token='herald')
        # self.wx.check_signature(self.get_argument('signature', default=''),
        #                        self.get_argument('timestamp', default=''),
        #                        self.get_argument('nonce', default='')):
        if True:
            msg = self.wx.parse_msg(self.request.body)
            if self.wx.msg_type == 'event' and self.wx.event == 'subscribe':
                self.write(self.wx.response_text_msg('welcome'))
            elif self.wx.event_key == 'curriculum' or \
                    self.wx.content == 'curriculum':
                self.curriculum(self.wx.openid)
            else:
                self.write(self.wx.response_text_msg(json.dumps(msg)))
        else:
            self.wx.parse_msg(self.request.body)
            self.write(self.wx.response_text_msg('message processing fail'))

        self.finish()

    def curriculum(self, openid):
        user = self.db.query(User).filter(User.openid == openid)
        try:
            user = self.db.query(User).filter(User.openid == openid).one()
            client = HTTPClient()
            params = urllib.urlencode({
                'cardnum': user.cardnum,
                'term': TERM
            })
            request = HTTPRequest(SERVICE + 'curriculum', method='POST',
                                  body=params, request_timeout=TIME_OUT)
            response = client.fetch(request)
            print response.body
            self.write(self.wx.response_text_msg(
                json.loads(response.body)))
        except:
            self.write(self.wx.response_text_msg('11'))


if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

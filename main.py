# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:16:23
# @Author  : xindervella@gamil.com

from sqlalchemy.orm import scoped_session, sessionmaker
from mod.models.db import engine
from mod.user.user_handler import UserHandler
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
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

    def get(self):
        wx = wechat.Message(token='herald')
        if wx.check_signature(self.get_argument('signature', default=''),
                              self.get_argument('timestamp', default=''),
                              self.get_argument('nonce', default='')):
            self.write(self.get_argument('echostr'))
        else:
            self.write('access verification fail')

    def post(self):
        wx = wechat.Message(token='herald')
        if wx.check_signature(self.get_argument('signature', default=''),
                              self.get_argument('timestamp', default=''),
                              self.get_argument('nonce', default='')):
            msg = wx.parse_msg(self.request.body)
            if wx.msg_type == 'event' and wx.envent == 'subscribe':
                self.write(wx.response_text_msg('welcome'))
            else:
                self.write(wx.response_text_msg(json.dumps(msg)))
        else:
            wx.parse_msg(self.request.body)
            self.write(wx.response_text_msg('message processing fail'))


if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
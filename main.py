# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:16:23
# @Author  : xindervella@gamil.com yml_bright@163.com

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from mod.models.db import engine
from mod.user.user_handler import UserHandler
from mod.units.curriculum_handler import CurriculumHandler
from mod.units.renew_handler import RenewHandler
from mod.units.gpa_handler import GPAHandler
from mod.units.srtp_handler import SRTPHandler
from mod.units import update
from mod.units import get
from mod.units import play
from mod.models.user import User
from mod.units.weekday import today, tomorrow
from mod.units.config import LOCAL
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.gen
import wechat
import os

from tornado.options import define, options
define('port', default=7200, help='run on the given port', type=int)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/wechat2/', WechatHandler),
            (r'/wechat2/register/([\S]+)', UserHandler),
            (r'/wechat2/curriculum/([\S]+)', CurriculumHandler),
            (r'/wechat2/renew/([\S]+)/([\S]+)', RenewHandler),
            (r'/wechat2/gpa/([\S]+)', GPAHandler),
            (r'/wechat2/srtp/([\S]+)', SRTPHandler),

        ]
        settings = dict(
            cookie_secret="7CA71A57B571B5AEAC5E64C6042415DE",
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = scoped_session(sessionmaker(bind=engine,
                                              autocommit=False, autoflush=True,
                                              expire_on_commit=False))


class WechatHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def unitsmap(self):
        return {
            'update-curriculum': self.update_curriculum,
            'today-curriculum': self.today_curriculum,
            'tomorrow-curriculum': self.tomorrow_curriculum,
            'new-curriculum': self.new_curriculum,
            'pe': self.pe_counts,
            'library': self.rendered,
            'gpa': self.gpa,
            'update-gpa': self.update_gpa,
            'srtp': self.srtp,
            'update-srtp': self.update_srtp,
            'play': self.play,
            'change-user': self.change_user,
            'help': self.help,
            'nic': self.nic,
            'card': self.card,
            'lecture': self.lecture,
            'nothing': self.nothing
        }

    def on_finish(self):
        self.db.close()

    def get(self):
        self.wx = wechat.Message(token='bright')
        if self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default='')):
            self.write(self.get_argument('echostr'))
        else:
            self.write('access verification fail')

    @tornado.web.asynchronous
    def post(self):
        self.wx = wechat.Message(token='bright')
        if self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default='')):
            self.wx.parse_msg(self.request.body)
            if self.wx.msg_type == 'event' and self.wx.event == 'subscribe':
                self.write(self.wx.response_text_msg('welcome'))
                self.finish()
            elif self.wx.msg_type == 'text':
                try:
                    user = self.db.query(User).filter(
                        User.openid == self.wx.openid).one()
                    if user.state == 0:
                        self.unitsmap[self.wx.content](user)
                    elif user.state == 1:
                        self.simsimi(self.wx.raw_content, user)
                    self.finish()
                except NoResultFound:
                    self.write(self.wx.response_text_msg(
                        u'<a href="%s/register/%s">=。= 不如先点我绑定一下？</a>' % (
                            LOCAL, self.wx.openid)))
                    self.finish()
            elif self.wx.msg_type == 'event':
                try:
                    user = self.db.query(User).filter(
                        User.openid == self.wx.openid).one()
                    try:
                        self.unitsmap[self.wx.event_key](user)
                    except KeyError:
                        pass
                    self.finish()
                except NoResultFound:
                    self.write(self.wx.response_text_msg(
                        u'<a href="%s/register/%s">=。= 不如先点我绑定一下？</a>' % (
                            LOCAL, self.wx.openid)))
                    self.finish()
            else:
                self.write(self.wx.response_text_msg(u'??'))
                self.finish()
        else:
            self.write('message processing fail')
            self.finish()

    # 课表
    # 更新频率较低，无需缓存

    def update_curriculum(self, user):
        msg = update.curriculum(self.db, user)
        self.write(self.wx.response_text_msg(msg))

    def today_curriculum(self, user):
        msg = get.curriculum(self.db, user, today())
        self.write(self.wx.response_text_msg(msg))

    def tomorrow_curriculum(self, user):
        msg = get.curriculum(self.db, user, tomorrow())
        self.write(self.wx.response_text_msg(msg))

    def new_curriculum(self, user):
        msg = get.new_curriculum(self.db, user)
        self.write(self.wx.response_text_msg(msg))

    # 跑操
    # service 做了缓存，这里不再缓存

    def pe_counts(self, user):
        msg = get.pe_counts(user)
        self.write(self.wx.response_text_msg(msg))

    # 图书馆借书信息
    # 暂时使用旧版服务

    def rendered(self, user):
        msg = get.rendered(user)
        self.write(self.wx.response_text_msg(msg))

    # GPA

    def gpa(self, user):
        msg = get.gpa(self.db, user)
        self.write(self.wx.response_text_msg(msg))

    def update_gpa(self, user):
        msg = update.gpa(self.db, user)
        self.write(self.wx.response_text_msg(msg))

    # SRTP
    def srtp(self, user):
        msg = get.srtp(self.db, user)
        self.write(self.wx.response_text_msg(msg))

    def update_srtp(self, user):
        msg = update.srtp(self.db, user)
        self.write(self.wx.response_text_msg(msg))

    # 调戏
    def play(self, user):
        msg = play.update(self.db, user)  # u'=。= 暂不接受调戏'
        self.write(self.wx.response_text_msg(msg))

    def simsimi(self, content, user):
        msg = play.simsimi(content, user)
        try:
            self.write(self.wx.response_text_msg(msg.decode('utf-8')))
        except UnicodeEncodeError:
            self.write(self.wx.response_text_msg(msg))
        except:
            self.write(self.wx.response_text_msg(u'encode error'))

    #一卡通
    def card(self, user):
        msg = get.card(user)
        self.write(self.wx.response_text_msg(msg))

    #人文讲座
    def lecture(self, user):
        msg = get.lecture(user)
        self.write(self.wx.response_text_msg(msg))

    #校园网
    def nic(self, user):
        msg = get.nic(user)
        self.write(self.wx.response_text_msg(msg))



    # 其他
    def change_user(self, user):
        msg = u'当前用户为：%s \n\n\n<a href="%s/register/%s">点击重新绑定</a>' % (
            user.cardnum, LOCAL, self.wx.openid)
        self.write(self.wx.response_text_msg(msg))

    def help(self, user):
        msg = u'<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=202009235&idx=1&sn=6659475ca9c4afd40c46b32c6a45ecb2#rd"> =。= 点我查看使用说明 </a>'
        self.write(self.wx.response_text_msg(msg))

    def nothing(self, user):
        msg = u'无法识别命令，想要调戏小猴别忘了点一下[调戏],么么哒'
        self.write(self.wx.response_text_msg(msg))

if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

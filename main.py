# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:16:23
# @Author  : xindervella@gamil.com

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from config import SERVICE, TIME_OUT, TERM, LOCAL, LIBRARY
from mod.models.db import engine
from mod.user.user_handler import UserHandler
from mod.units.curriculum_handler import CurriculumHandler
from mod.units.renew_handler import RenewHandler
from mod.models.course import Course
from mod.models.user import User
from mod.units.weekday import today, tomorrow
from tornado.httpclient import HTTPRequest, HTTPClient
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.gen
import wechat
import urllib
import json
import os

from tornado.options import define, options
define('port', default=7000, help='run on the given port', type=int)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/wechat/', WechatHandler),
            (r'/wechat/register/([\S]+)', UserHandler),
            (r'/wechat/curriculum/([\S]+)', CurriculumHandler),
            (r'/wechat/renew/([\S]+)/([\S]+)', RenewHandler)
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
            'pe': self.pe_counts,
            'library': self.rendered,
            'nothing': self.help
        }

    def get(self):
        self.wx = wechat.Message(token='herald')
        if self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default='')):
            self.write(self.get_argument('echostr'))
        else:
            self.write('access verification fail')

    @tornado.web.asynchronous
    def post(self):
        self.wx = wechat.Message(token='herald')
        # if self.wx.check_signature(self.get_argument('signature', default=''),
        #                        self.get_argument('timestamp', default=''),
        #                        self.get_argument('nonce', default='')):
        if True:
            self.wx.parse_msg(self.request.body)
            if self.wx.msg_type == 'event' and self.wx.event == 'subscribe':
                self.write(self.wx.response_text_msg('welcome'))
            elif self.wx.msg_type == 'text':
                try:
                    user = self.db.query(User).filter(
                        User.openid == self.wx.openid).one()
                    self.db.close()
                    self.unitsmap[self.wx.content](user)
                except NoResultFound:
                    self.write(self.wx.response_text_msg(
                        u'<a href="%s/register/%s">=。= 不如先绑定一下？</a>' % (
                            LOCAL, self.wx.openid)))
                    self.finish()
            elif self.wx.msg_type == 'event':
                try:
                    user = self.db.query(User).filter(
                        User.openid == self.wx.openid).one()
                    self.db.close()
                    self.unitsmap[self.wx.event_key](user)
                    self.finish()
                except NoResultFound:
                    self.write(self.wx.response_text_msg(
                        u'<a href="%s/register/%s">=。= 不如先绑定一下？</a>' % (
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
        client = HTTPClient()
        params = urllib.urlencode({
            'cardnum': user.cardnum,
            'term': TERM
        })
        request = HTTPRequest(SERVICE + 'curriculum', method='POST',
                              body=params, request_timeout=TIME_OUT)
        response = client.fetch(request)
        if (not response.headers) or response.body == 'time out':
            self.write(self.wx.response_text_msg(u'=。= 由于网络状况更新失败，不如待会再试试'))
            self.finish()
        else:
            self.write(self.wx.response_text_msg(u'更新成功'))
            self.finish()
            courses = self.db.query(Course).filter(
                Course.openid == user.openid).all()

            for course in courses:
                self.db.delete(course)
            curriculum = json.loads(response.body)
            for day, items in curriculum.items():
                for item in items:
                    self.db.add(Course(openid=user.openid,
                                       course=item[0],
                                       period=item[1],
                                       place=item[2],
                                       day=day))
            try:
                self.db.commit()
            except:
                self.db.rollback()
            finally:
                self.db.close()

    def today_curriculum(self, user):
        self.get_curriculum(user, today())

    def tomorrow_curriculum(self, user):
        self.get_curriculum(user, tomorrow())

    def get_curriculum(self, user, day):
        courses = self.db.query(Course).filter(
            Course.openid == user.openid, Course.day == day).all()
        self.db.close()
        msg = u''
        for course in courses:
            msg += course.course + u'\n' + \
                course.period + u'\n' + course.place + u'\n\n'
        if not msg:
            msg = u'没课哦'
        msg = msg.strip() + '\n\n' + \
            u'<a href="%s/curriculum/%s">查看课表</a>' % (
                LOCAL, user.openid)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    # 跑操
    # service 做了缓存，这里不再缓存

    def pe_counts(self, user):
        client = HTTPClient()
        if user.pe_password:
            pwd = user.pe_password
        else:
            pwd = user.cardnum
        params = urllib.urlencode({
            'cardnum': user.cardnum,
            'pwd': pwd
        })
        request = HTTPRequest(SERVICE + 'pe', method='POST',
                              body=params, request_timeout=TIME_OUT)
        response = client.fetch(request)
        if (not response.headers) or response.body == 'time out':
            self.write(self.wx.response_text_msg(u'=。= 体育系暂时无法连接，不如待会再试试吧'))
            self.finish()
        elif response.body == 'wrong card number or password':
            self.write(self.wx.response_text_msg(
                u'<a href="%s/register/%s">=。= 同学，密码错了吧，快点我重新绑定。</a>' % (
                    LOCAL, user.openid)))
            self.finish()
        else:
            try:
                counts = int(response.body)
                self.write(self.wx.response_text_msg(
                           u'当前跑操次数 %d 次' % counts))
                self.finish()
            except:
                self.write(self.wx.response_text_msg(
                           u'=。= 出了点故障，不如待会再试试吧'))
                self.finish()

    # 图书馆借书信息
    # 暂时使用旧版服务
    def rendered(self, user):
        client = HTTPClient()
        params = urllib.urlencode({
            'username': user.lib_username,
            'password': user.lib_password
        })
        request = HTTPRequest(LIBRARY, method='POST', body=params,
                              request_timeout=TIME_OUT)
        response = client.fetch(request)
        if (not response.headers) or response.body == 'server error':
            self.write(self.wx.response_text_msg(u'=。= 图书馆暂时无法连接，不如待会再试试'))
            self.finish()
        elif response.body == 'username or password error':
            self.write(self.wx.response_text_msg(
                u'<a href="%s/register/%s">=。= 同学，用户名/密码错了吧，快点我重新绑定。</a>' % (
                    LOCAL, user.openid)))
            self.finish()
        else:
            msg = u''
            try:
                books = json.loads(response.body)
                for book in books:
                    detail = u'\n%s\n%s\n借书时间：%s\n到期时间：%s' % (
                        book['author'], book['place'],
                        book['render_date'], book['due_date'])
                    if book['renew_time'] == u'0':
                        msg += u'<a href="%s/renew/%s/%s">《%s》</a>%s' % (
                            LOCAL, user.openid, book['barcode'],
                            book['title'], detail)
                    else:
                        msg += u'《%s》%s\n续借次数：%s' % (
                            book['title'], detail, book['renew_time'])
                    msg += u'\n\n'
                msg += u'如果要续借的话请戳书名'
                if not msg:
                    msg = u'没有在图书馆借书哦'
                self.write(self.wx.response_text_msg(msg.strip()))
                self.finish()
            except:
                self.write(self.wx.response_text_msg(u'=。= 图书馆暂时无法连接，不如待会再试试'))
                self.finish()

    # 其他

    def help(self, user):
        self.write(self.wx.response_text_msg(u'=。='))
        self.finish()

if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

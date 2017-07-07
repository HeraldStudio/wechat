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
from mod.units.update_handler import UpdateHandler
from mod.units.card_handler import CradHandler
from mod.units import update
from mod.units import get
from mod.units import play
from mod.units import quanyi
from mod.models.user import User
from mod.units.weekday import today, tomorrow
from mod.units.config import LOCAL
from mod.units.ticket_handler import ticket_handler
from mod.lecture.handler import LectureHandler
from mod.units.lecture import LectureQueryHandler
from mod.units.pe_handler import PeDetailHandler
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.gen
import wechat
import os, sys
from time import localtime, strftime, time

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
            (r'/wechat2/card/([\S]+)', CradHandler),
            (r'/wechat2/srtp/([\S]+)', SRTPHandler),
            (r'/wechat2/update/([\S]+)/([\S]+)', UpdateHandler),
            (r'/wechat2/lecture',LectureHandler),
            (r'/wechat2/lecturequery',LectureQueryHandler),
            (r'/wechat2/pedetail/([\S]+)',PeDetailHandler),

        ]
        settings = dict(
            cookie_secret="7CA71A57B571B5AEAC5E64C6042415DE",
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=False
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = scoped_session(sessionmaker(bind=engine,
                                              autocommit=False, autoflush=True,
                                              expire_on_commit=False))
        self.requestLog = {}


class WechatHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def unitsmap(self):
        return {
            'update-curriculum': self.update_curriculum,
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
            'lecturenotice': self.lecturenotice,
            'jwc': self.jwc,
            'searchlib': self.searchlib,
            'schoolbus': self.schoolbus,
            'quanyi': self.quanyi_info,
            'phylab': self.phylab,
            'grade': self.grade,
            'dm':self.dm,
            'room':self.room,
	    	'schoolnum':self.schoolnum,
            'yuyue':self.yuyue,
            'xiaoli':self.xiaoli,
            'exam':self.exam,
            'feedback':self.feedback,
            'tice':self.tice,
            'app':self.app,
	    	'newseu':self.newseu,
			'xinli':self.xinli,
            'nothing': self.nothing,
            'bonus':self.bonus
            'unicom':self.unicom,
        }

    def on_finish(self):
        self.db.close()

    def get(self):
        self.wx = wechat.Message(token='Herald2016NewStart')
        if self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default='')):
            self.write(self.get_argument('echostr'))
        else:
            self.write('access verification fail')

    @tornado.web.asynchronous
    def post(self):
        self.wx = wechat.Message(token='Herald2016NewStart')
        s = self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default=''))
        if self.wx.check_signature(self.get_argument('signature', default=''),
                                   self.get_argument('timestamp', default=''),
                                   self.get_argument('nonce', default='')):
            self.wx.parse_msg(self.request.body)
            try:
                typelog = "log"
                if self.wx.msg_type == 'event' and self.wx.event == 'subscribe':
                    self.write(self.wx.response_text_msg(u'欢迎关注小猴偷米。小猴功能需要绑定才能使用哦。更多精彩请下载<a href="http://app.heraldstudio.com">app</a>'))
                    self.finish()
                elif self.wx.msg_type == 'text':
                    try:
                        key = self.wx.content_key(self.wx.content)
                        currentTime = time()
                        if self.wx.openid in self.application.requestLog and currentTime - self.application.requestLog[self.wx.openid] < 1:
                            self.write(self.wx.response_text_msg(u'正在查询'))
                            self.finish()
                        else:
                            self.application.requestLog[self.wx.openid] = currentTime
                            if self.wx.check_user(key):
                                user = self.db.query(User).filter(
                                    User.openid == self.wx.openid).one()
                                if user.state == 0:
                                    self.unitsmap[key](user)
                                elif user.state == 1:
                                    if key=='nothing':
                                        self.simsimi(self.wx.raw_content, user)
                                    else:
                                        self.unitsmap[key](user)
                            else:
                                self.unitsmap[key](None)
                    except NoResultFound:
                        self.write(self.wx.response_text_msg(
                            u'<a href="%s/register/%s">=。= 不如先点我绑定一下？</a>.新生绑定前请务必登录个人信息门户(http://my.seu.edu.cn)修改密码,否则将会无法绑定或者功能无法使用' % (
                                LOCAL, self.wx.openid)))
                        self.finish()
                elif self.wx.msg_type == 'event':
                    try:
                        typelog = self.wx.event_key
                        key = self.wx.event_key
                        user = None
                        currentTime = time()
                        if self.wx.openid in self.application.requestLog and currentTime - self.application.requestLog[self.wx.openid] < 2:
                            self.write(self.wx.response_text_msg(u'正在查询'))
                            self.finish()
                        else:
                            self.application.requestLog[self.wx.openid] = currentTime
                            if self.wx.check_user(key):
                                user = self.db.query(User).filter(
                                    User.openid == self.wx.openid).one()
                            try:
                                self.unitsmap[key](user)
                            except KeyError:
                                self.finish()
                    except NoResultFound:
                        self.write(self.wx.response_text_msg(
                            u'<a href="%s/register/%s">=。= 不如先点我绑定一下？</a>' % (
                                LOCAL, self.wx.openid)))
                        self.finish()
                elif self.wx.msg_type == 'voice':
                    try:
                        key = self.wx.content_key(self.wx.voice_content)
                        if self.wx.check_user(key):
                            user = self.db.query(User).filter(
                                User.openid == self.wx.openid).one()
                            if user.state == 0:
                                self.unitsmap[key](user)
                            elif user.state == 1:
                                if key=='nothing':
                                    self.simsimi(self.wx.voice_content, user)
                                else:
                                    self.unitsmap[key](user)
                        else:
                            self.unitsmap[key](None)
                    except NoResultFound:
                        self.write(self.wx.response_text_msg(
                            u'<a href="%s/register/%s">=。= 不如先点我绑定一下？</a>' % (
                                LOCAL, self.wx.openid)))
                        self.finish()
                else:
                    self.write(self.wx.response_text_msg(u'??'))
                    self.finish()
            except:
                with open('wechat_error.log','a+') as f:
                    f.write(strftime('%Y%m%d %H:%M:%S in [wechat]', localtime(time()))+'\n'+str(sys.exc_info()[0])+'\n'+typelog+'\n'+str(sys.exc_info()[1])+'\n\n')
                self.write(self.wx.response_text_msg(u'小猴正在自我改良中～稍候再试， 么么哒！'))
                self.finish()
        else:
            self.write('message processing fail')
            self.finish()

    # 课表
    # 更新频率较低，无需缓存

    def update_curriculum(self, user):
        msg = update.curriculum(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def tomorrow_curriculum(self, user):
        msg = get.curriculum(self.db, user, tomorrow())
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def new_curriculum(self, user):
        msg = get.new_curriculum(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    # 跑操
    # service 做了缓存，这里不再缓存

    def pe_counts(self, user):
        msg = get.pe_counts(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    # 图书馆借书信息
    # 暂时使用旧版服务

    def rendered(self, user):
        msg = get.rendered(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    # GPA

    def gpa(self, user):
        msg = get.gpa(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def update_gpa(self, user):
        msg = update.gpa(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    # SRTP
    def srtp(self, user):
        msg = get.srtp(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def update_srtp(self, user):
        msg = update.srtp(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    # 调戏
    def play(self, user):
        msg = play.update(self.db, user)  # u'=。= 暂不接受调戏'
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def simsimi(self, content, user):
        msg = play.simsimi(content, user)
        try:
            self.write(self.wx.response_text_msg(msg.decode('utf-8')))
        except UnicodeEncodeError:
            self.write(self.wx.response_text_msg(msg))
        except:
            self.write(self.wx.response_text_msg(u'encode error'))
        self.finish()

    #一卡通
    def card(self, user):
        msg = get.card(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #人文讲座
    def lecture(self, user):
        msg = get.lecture(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #校园网
    def nic(self, user):
        msg = get.nic(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #教务处
    def jwc(self, user):
        #msg = u'正在维护'
        msg = get.jwc(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #图书馆搜索图书
    def searchlib(self, user):
        msg = get.searchlib(user, self.wx.sub_content)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #校车
    def schoolbus(self, user):
        msg = get.schoolbus(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def phylab(self, user):
        msg = get.phylab(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def lecturenotice(self, user):
        msg = get.lecturenotice(self.db,user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def grade(self, user):
        msg = get.grade(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #xiao quan yi
    def quanyi_info(self, user):
        msg = quanyi.quanyi(self.db, user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    #  弹幕
    def dm(self,user):
        self.write(self.wx.response_text_msg(get.dm(user,self.wx.sub_content)))
        self.finish()
    # 宿舍
    def room(self,user):
        msg = get.room(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def schoolnum(self,user):
        msg = get.schoolnumber(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()
    def yuyue(self,user):
        msg = get.yuyue(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()
    def xiaoli(self,user):
        self.write(self.wx.response_pic_msg(u'2016-17学年校历','http://mmbiz.qpic.cn/mmbiz/RmfKVHqzAibS1f3xFqJqxeDkEgFzAlrD0Q4JPjKOgwdkLmtub3NWuLsx78wltCz4bV7b0DoeBG8KRVmR4d8ffKg/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1',u'点击查看详细','http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=400874492&idx=1&sn=2ed0d9882fdc78a3c2e4f5dfc4565802#rd'))
        self.finish()

    def exam(self,user):
        msg = get.exam(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()
    def feedback(self,user):
        msg = u'\n<a href="http://www.heraldstudio.com/service/feedback?cardnum=%s">点我进行反馈哦~</a>' % user.cardnum
        self.write(self.wx.response_text_msg(msg))
        self.finish()
    def tice(self,user):
        msg = get.tice(user)
        self.write(self.wx.response_text_msg(msg))
        self.finish()
    def xinli(self,user):
        msg = u'<a href="http://www.mikecrm.com/lduJMn">点我预约心理健康中心！</a>'
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def bonus(self,user):
        msg = u'居然在小猴上查我的名字，看来是真爱哦！'
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def app(self,user):
        msg = u'<a href="http://app.heraldstudio.com">点我下载app哦~</a>'
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def unicom(self):
        mediaId = 'ZPIovg0k7WxOeY7FGAPzDJPXRfM18jIvVFqIwnG3eJuENSXC0B2oUmcjVPCcrB5B' #from wechat upload interface
        self.write(self.wx.response_picture_msg(mediaId))
        self.finish()

    # 其他
    def change_user(self, user):
        msg = u'当前用户为：%s \n\n\n<a href="%s/register/%s">点击重新绑定</a>' % (
            user.cardnum, LOCAL, self.wx.openid)
        msg += u'\n<a href="http://www.heraldstudio.com/service/feedback?cardnum=%s">点我进行反馈哦~</a>' % user.cardnum
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def help(self, user):
        msg = u'<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=211217347&idx=1&sn=5821c986e24b4e6ce001396819927fdc#rd">点我查看使用说明 </a>'
        msg += u'\n<a href="http://url.cn/41x4fjh">常见问题</a>'
        self.write(self.wx.response_text_msg(msg))
        self.finish()
    def newseu(self,user):
        msg = u'<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=2651223258&idx=2&sn=4355e2e37fcf19374ded26fb1fc4d88b#rd">【新生tips】住</a>'
        msg += u'\n<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=2651223258&idx=3&sn=73a73b453f472a5a6f1f36410f6f0712#rd">【新生tips】行</a>'
        msg += u'\n<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=2651223265&idx=2&sn=4941071e8563065c18ebe25b79999a45#rd">【新生tips】学</a>'
        msg += u'\n<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=2651223265&idx=3&sn=dcbe48b966f75f4a9dcdc678d25a0c54#rd">【新生tips】吃</a>'
        self.write(self.wx.response_text_msg(msg))
        self.finish()

    def nothing(self, user):
        msg = u'无法识别命令.\n想要调戏小猴别忘了点一下[调戏]\n想要找图书前面别忘了加上"ss"'
        msg += u'\n输入[考试安排]查询考试安排'
        msg += u'\n输入[宿舍]查询当前宿舍信息'
        msg += u'\n<a href="http://mp.weixin.qq.com/s?__biz=MjM5NDI3NDc2MQ==&mid=402080773&idx=1&sn=328ae46e08271a42c67488921b39dc9b#rd">点我查看功能列表</a>'
        msg += u'\n<a href="http://www.heraldstudio.com/service/feedback?cardnum=%s">点我进行反馈哦~</a>' % user.cardnum
        msg += u'\n<a href="http://app.heraldstudio.com">点我下载app哦~</a>'
        msg += u'\n么么哒'
        self.write(self.wx.response_text_msg(msg))
        self.finish()

if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


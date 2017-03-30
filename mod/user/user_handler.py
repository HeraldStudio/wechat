# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 20:10:43
# @Author  : xindervella@gamil.com yml_bright@163.com

import tornado.web
from tornado.httpclient import HTTPRequest, HTTPClient
from ..models.user import User
from ..units import update
from ..units.config import AUTH, APPID, TIME_OUT
import urllib

class UserHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self, openid):
        self.render('register.html', openid=openid)

    @tornado.web.asynchronous
    def post(self, openid):
        cardnum = self.get_argument('cardnum', default='')
        number = self.get_argument('number', default='')
        password = self.get_argument('password', default='')
        pe_password = self.get_argument('pe_password', default='')
        lib_username = self.get_argument('lib_username', default='')
        lib_password = self.get_argument('lib_password', default='')
        flag = True
        if not openid:
            self.write('access verification fail')
            self.finish()
            flag = False
        elif not (cardnum and password):
            self.write('同学，至少填一下必填项吧')
            self.finish()
            flag = False

        if flag:
            newUser = False
            try:
                user = self.db.query(User).filter(User.openid == openid).one()
                data = {
                    'cardnum': cardnum,
                    'password': password
                }
                if number:
                    data['number'] = number
                if pe_password:
                    data['pe_password'] = pe_password
                if lib_username:
                    data['lib_username'] = lib_username
                if lib_password:
                    data['lib_password'] = lib_password
            except:
                data = {
                    'cardnum': cardnum,
                    'number': number,
                    'password': password,
                    'pe_password': pe_password,
                    'lib_username': lib_username,
                    'lib_password': lib_password
                }
                newUser = True
            finally:
                try:
                    x = urllib.urlencode(data)
                except:
                    self.write('=.= 输入了非法字符')
                    self.finish()
                    self.db.close()
                    return
                if self.update_info(data):
                    uuid = self.auth(data)
                    if uuid:
                        if newUser:
                            user = User(openid=openid,
                                        cardnum=cardnum,
                                        uuid=uuid,
                                        state=0)
                        else:
                            user.cardnum = cardnum
                            user.uuid = uuid
                        self.db.add(user)
                    else:
                        self.write('=.= 网络有点差，等会再是一次吧')
                        self.finish()
                        self.db.close()
                        return
                else:
                    self.write('=.= 一卡通或统一身份密码不正确，要不再是一次')
                    self.finish()
                    self.db.close()
                    return
                self.db.commit()
                self.write('success')
                self.finish()
                update.curriculum(self.db, user)
                update.gpa(self.db, user)
                update.srtp(self.db, user)
                self.db.close()

    def update_info(self, data):
        client = HTTPClient()
        request = HTTPRequest(AUTH + 'update', method='POST',
                              body=urllib.urlencode(data), request_timeout=TIME_OUT)
        try:
            response = client.fetch(request)
            if response.body == 'OK':
                return True
        except:
            pass
        return False

    def auth(self, data):
        data['appid'] = APPID
        data['user'] = data['cardnum']
        client = HTTPClient()
        request = HTTPRequest(AUTH + 'auth', method='POST',
                              body=urllib.urlencode(data), request_timeout=TIME_OUT)
        try:
            response = client.fetch(request)
            if response.body:
                return response.body
        except:
            pass
        return False
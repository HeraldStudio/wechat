# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 20:10:43
# @Author  : xindervella@gamil.com

import tornado.web
from ..models.user import User
from ..units import update


class UserHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self, openid):
        self.render('register.html', openid=openid)

    @tornado.web.asynchronous
    def post(self, openid):
        cardnum = self.get_argument('cardnum', default='')
        password = self.get_argument('password', default='')
        pe_password = self.get_argument('pe_password', default='')
        lib_username = self.get_argument('lib_username', default='')
        lib_password = self.get_argument('lib_password', default='')

        if not openid:
            self.write('access verification fail')
            self.finish()
        elif not cardnum:
            self.write('同学，至少填一下一卡通号吧')
            self.finish()
        else:
            try:
                user = self.db.query(User).filter(User.openid == openid).one()
                if cardnum:
                    user.cardnum = cardnum
                if password:
                    user.password = password
                if pe_password:
                    user.pe_password = pe_password
                if lib_username:
                    user.lib_username = lib_username
                if lib_password:
                    user.lib_password = lib_password
            except:
                user = User(openid=openid, cardnum=cardnum, password=password,
                            pe_password=pe_password, lib_username=lib_username,
                            lib_password=lib_password, state=0)
                self.db.add(user)
            finally:
                self.db.commit()
                self.write('success')
                self.finish()
                update.curriculum(self.db, user)
                update.gpa(self.db, user)
                self.db.close()

# -*- coding: utf-8 -*-
# @Date    : 2015-05-28

import tornado.web
from ..models.eat import Eat
from config import eat_token
import datetime,time
from sqlalchemy.orm.exc import NoResultFound

class EatHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    def get(self):
        self.render('eat.html')

    def post(self):
        status = self.get_argument('status',default = None)
        token = self.get_argument('token',default = None)
        if not status or not token:
            self.write('请填写完整信息哦')
            self.finish()
        else:
            if not token==eat_token:
                self.write('token不正确')
                self.finish()
            else:
                day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                today = time.strftime('%Y-%m-%d-%H',time.localtime(time.time()))
                try:
                    item = self.db.query(Eat).filter(Eat.day == day).one()
                    item.status = status
                    item.time = today
                except NoResultFound:
                    eat = Eat(
                                day = day,
                                time = today,
                                status = status)
                    self.db.add(eat)
                try:
                    self.db.commit()
                    self.write('success')
                    self.finish()
                except Exception,e:
                    print str(e)
                    self.db.rollback()
                    self.write('发布失败T T')
                    self.finish()
                self.db.close()

    

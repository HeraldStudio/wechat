#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-12-11 21:49:24
# @Author  : yml_bright@163.com

import tornado.web
from sqlalchemy.orm.exc import NoResultFound
from ..models.course import Course
from ..models.user import User
from ..models.gpa import Overview as GPAO, Detail as GPAD
from ..models.srtp import Overview as SRTPO, Detail as SRTPD
from get_api_return import get_api_return

TEMPLATE = u'<center><h1 style="margin-top:30%">{content}</h2></center>'

class UpdateHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self, type, openid):
        try:
            db = self.db
            user = self.db.query(User).filter(User.openid == openid).one()
            if type == 'srtp':
                response = get_api_return('srtp', user, timeout=17)
                if response['code'] == 200:
                    srtp = response['content']
                    try:
                        overview = db.query(SRTPO).filter(SRTPO.openid == user.openid).one()
                        overview.total = srtp[0]['total']
                        overview.score = srtp[0]['score']
                    except NoResultFound:
                        db.add(SRTPO(openid=user.openid,
                                     total=srtp[0]['total'],
                                     score=srtp[0]['score']))
                    items = db.query(SRTPD).filter(SRTPD.openid == user.openid).all()
                    for item in items:
                        db.delete(item)
                    for item in srtp[1:]:
                        db.add(SRTPD(openid=user.openid,
                                     project=item['project'],
                                     department=item['department'],
                                     date=item['date'],
                                     project_type=item['type'],
                                     total_credit=item['total credit'],
                                     credit=item['credit'],
                                     proportion=item['proportion']))
                    try:
                        db.commit()
                        self.write(TEMPLATE.format(content=u'更新好啦'))
                    except:
                        db.rollback()
                        self.write(TEMPLATE.format(content=u'T T 出了点小问题'))
                else:
                    self.write(TEMPLATE.format(content=response['content']))
            elif type == 'gpa':
                response = get_api_return('gpa', user, timeout=30)
                if response['code'] == 200:
                    gpa = response['content']
                    try:
                        overview = db.query(GPAO).filter(GPAO.openid == user.openid).one()
                        overview.gpa = gpa[0]['gpa']
                        overview.before_revamp = gpa[0]['gpa without revamp']
                        overview.calc_time = gpa[0]['calculate time']
                    except NoResultFound:
                        db.add(GPAO(openid=user.openid,
                                    gpa=gpa[0]['gpa'],
                                    before_revamp=gpa[0]['gpa without revamp'],
                                    calc_time=gpa[0]['calculate time']))
                    items = db.query(GPAD).filter(GPAD.openid == user.openid).all()
                    for item in items:
                        db.delete(item)
                    for item in gpa[1:]:
                        db.add(GPAD(openid=user.openid,
                                    course=item['name'],
                                    credit=item['credit'],
                                    semester=item['semester'],
                                    score=item['score'],
                                    score_type=item['type'],
                                    extra=item['extra']))
                    try:
                        db.commit()
                        self.write(TEMPLATE.format(content=u'更新好啦'))
                    except:
                        db.rollback()
                        self.write(TEMPLATE.format(content=u'T T 出了点小问题'))
                else:
                    self.write(TEMPLATE.format(content=response['content']))
            elif type == 'curriculum':
                response = get_api_return('curriculum', user, timeout=30)
                if response['code'] == 200:
                    courses = db.query(Course).filter(Course.openid == user.openid).all()
                    curriculum = response['content']
                    for course in courses:
                        db.delete(course)
                    for day, items in curriculum.items():
                        for item in items:
                            db.add(Course(openid=user.openid,
                                          course=item[0],
                                          period=item[1],
                                          place=item[2],
                                          day=day))
                    try:
                        db.commit()
                        self.write(TEMPLATE.format(content=u'更新好啦'))
                    except:
                        db.rollback()
                        self.write(TEMPLATE.format(content=u'T T 出了点小问题'))
                else:
                    self.write(TEMPLATE.format(content=response['content']))
            else:
                self.write(TEMPLATE.format(content=u'T T 出了点小问题???'))
        except:
            self.write(TEMPLATE.format(content=u'T T 出了点小问题...'))
        self.finish()

    def on_finish(self):
        self.db.close()
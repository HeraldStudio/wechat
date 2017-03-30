# -*- coding: utf-8 -*-
# @Date    : 2014-06-29 18:56:08
# @Author  : xindervella@gamil.com

import tornado.web
from ..models.course import Course
from weekday import today
from collections import OrderedDict
import re


class CurriculumHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self, openid):
        courses = self.db.query(Course).filter(Course.openid == openid).all()
        self.db.close()
        daymap = OrderedDict()
        daymap['Mon'] = '一'
        daymap['Tue'] = '二'
        daymap['Wed'] = '三'
        daymap['Thu'] = '四'
        daymap['Fri'] = '五'
        daymap['Sat'] = '六'
        daymap['Sun'] = '日'

        days = set()
        for course in courses:
            days.add(course.day)

        p = re.compile(r'\[|\]|\(|\)')
        self.render(
            'curriculum.html', courses=courses, today=today(),
            daymap=daymap, days=days, p=p)

    def on_finish(self):
        self.db.close()

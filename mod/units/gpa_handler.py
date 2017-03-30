# -*- coding: utf-8 -*-
# @Date    : 2014-07-01 22:00:36
# @Author  : xindervella@gamil.com
import tornado.web
from ..models.gpa import Detail as GPAD
from collections import OrderedDict


class GPAHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self, openid):
        items = self.db.query(GPAD).filter(GPAD.openid == openid).all()
        detail = OrderedDict()
        semesters = [item.semester for item in items]
        for semester in semesters:
            detail[semester] = []
        for item in items:
            detail[item.semester].append([
                item.course, item.credit, item.score,
                item.score_type, item.extra])

        self.render('gpa.html', detail=detail)
        self.db.close()

    def on_finish(self):
        self.db.close()

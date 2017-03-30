# -*- coding: utf-8 -*-
# @Date    : 2014-07-02 01:44:46
# @Author  : xindervella@gamil.com
import tornado.web
from ..models.srtp import Detail as SRTPD


class SRTPHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self, openid):
        items = self.db.query(SRTPD).filter(SRTPD.openid == openid).all()
        detail = [[item.project, item.department, item.date,
                   item.project_type, item.total_credit, item.credit,
                   item.proportion] for item in items]
        self.render('srtp.html', detail=detail)
        self.db.close()

    def on_finish(self):
        self.db.close()

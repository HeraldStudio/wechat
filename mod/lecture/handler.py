#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-03-07 12:46:36
# @Author  : jerry.liangj@qq.com

from ..models.lecturedb import LectureDB
from sqlalchemy.orm.exc import NoResultFound
from time import time,mktime,strftime,localtime,strptime
import tornado.web
import tornado.gen
import json
class LectureHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self):
        self.write('Herald Web Service')

    def post(self):
        retjson = {'code':200, 'content':''}
        date = mktime(strptime(strftime('%Y-%m-%d' ,localtime(time())), '%Y-%m-%d'))
        # read from db
        try:
            status = self.db.query(LectureDB).filter( LectureDB.date >=  date ).all()
            ret = []
            for l in status:
                ret.append({
                'date': l.time,
                'topic': l.topic,
                'speaker': l.speaker,
                'location': l.location,
                'detail': l.detail
                })
            retjson['content'] = ret
        except Exception,e:
            print str(e)
            retjson['code'] = 500
            retjson['content'] = 'error'
        ret = json.dumps(retjson, ensure_ascii=False, indent=2)
        self.write(ret)
        self.finish()

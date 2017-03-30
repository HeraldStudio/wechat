#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-03-17 18:38:13
# @Author  : yml_bright@163.com

import tornado.web
from ..models.user import User
from get_api_return import get_api_return
from time import time,mktime,strftime,localtime,strptime
from ..models.lecturedb import LectureDB
from sqlalchemy.orm.exc import NoResultFound
import json

TEMPLATE = u'<center><h1 style="margin-top:30%">{content}</h2></center>'

class LectureQueryHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        self.db.close()

    def get (self) :
        self.render('lecture.html')
    
    def post(self):
        query = self.get_argument('date',default=None)
        retjson = {'code':200,'content':''}
        if query==None:
            retjson['code'] = 400
            retjson['content'] = u'参数不能为空'
        else:
            # read from db                                           
            try:
                date = mktime(strptime(query,'%Y-%m-%d'))                                                     
                status = self.db.query(LectureDB).filter(LectureDB.date==int(date)).all()
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
                retjson['code'] = 500                                
                retjson['content'] = str(e)                         
        ret = json.dumps(retjson, ensure_ascii=False, indent=2)  
        self.write(ret)                                          
        self.finish()                                            




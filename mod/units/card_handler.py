#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-03-17 18:38:13
# @Author  : yml_bright@163.com

import tornado.web
from ..models.user import User
from get_api_return import get_api_return
import json

TEMPLATE = u'<center><h1 style="margin-top:30%">{content}</h2></center>'

class CradHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        self.db.close()

    def get (self,openid) :
        user = self.db.query(User).filter(User.openid == openid).one()
        
        response=get_api_return('card',user,{'timedelta':1},17)
        
        if response['code'] == 200:
            detail=response['content']
            self.render('card.html', detail=detail)
        else:
            self.write(TEMPLATE.format(content=u'T T 出了点小问题'))
            self.finish()
    

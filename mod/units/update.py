# -*- coding: utf-8 -*-
# @Date    : 2014-06-29 22:01:21
# @Author  : xindervella@gamil.com

from tornado.httpclient import HTTPRequest, HTTPClient
from sqlalchemy.orm.exc import NoResultFound
from config import SERVICE, TERM, TIME_OUT, LOCAL
from ..models.course import Course
from ..models.gpa import Overview as GPAO, Detail as GPAD
import urllib
import json


def curriculum(db, user):
    client = HTTPClient()
    params = urllib.urlencode({
        'cardnum': user.cardnum,
        'term': TERM
    })
    request = HTTPRequest(SERVICE + 'curriculum', method='POST',
                          body=params, request_timeout=TIME_OUT)
    response = client.fetch(request)
    if (not response.headers) or response.body == 'time out':
        return u'=。= 由于网络状况更新失败，不如待会再试试'
    else:
        courses = db.query(Course).filter(Course.openid == user.openid).all()
        curriculum = json.loads(response.body)
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
            return u'更新成功'
        except:
            db.rollback()
            return u'T T 出了点小问题'


def gpa(db, user):
    client = HTTPClient()
    params = urllib.urlencode({
        'username': user.cardnum,
        'password': user.password
    })
    request = HTTPRequest(SERVICE + 'gpa', method='POST',
                          body=params, request_timeout=TIME_OUT)
    response = client.fetch(request)
    if (not response.headers) or response.body == 'time out':
        return u'=。= 由于网络状况更新失败，不如待会再试试'

    elif response.body == 'wrong username or password':
        return u'<a href="%s/register/%s">居然没有绩点你敢信？你不是把一卡通/\
密码输错了吧，快点我修改。</a>' % (LOCAL, user.openid)

    else:
        gpa = json.loads(response.body)
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
            return u'更新成功'
        except:
            db.rollback()
            return u'T T 出了点小问题'

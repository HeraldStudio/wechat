# -*- coding: utf-8 -*-
# @Date    : 2014-06-29 22:01:21
# @Author  : xindervella@gamil.com

from tornado.httpclient import HTTPRequest, HTTPClient
from config import SERVICE, TERM, TIME_OUT
from ..models.course import Course
import urllib
import json


def init_curriculum(db, user):
    client = HTTPClient()
    params = urllib.urlencode({
        'cardnum': user.cardnum,
        'term': TERM
    })
    request = HTTPRequest(SERVICE + 'curriculum', method='POST',
                          body=params, request_timeout=TIME_OUT + 20)
    response = client.fetch(request)
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
    db.commit()
    return

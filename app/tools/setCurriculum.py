# -*- coding:utf-8 -*-
import json
import urllib
from app.models import UserInfo
from app.models import Curriculum

def setCurriculum(openId, term='13-14-3'):
    user = UserInfo.objects.filter(openId=openId)
    if user:
        cardNumber = user[0].cardNumber
    uFile = urllib.urlopen(
        "http://121.248.63.105/herald_web_service/curriculum/%s/%s/" % (cardNumber, term))
    curriculum = json.load(uFile)
    morning = curriculum[1][0]  # 早上
    afternoon = curriculum[1][1]  # 下午
    evening = curriculum[1][2]  # 晚上
    sat = curriculum[1][3]  # 周六
    sun = curriculum[1][4]  # 周日

    for i in xrange(7):
        if i < 5:
            dayCourse = morning[i] + afternoon[i] + evening[i]
        elif i == 5:
            dayCourse = sat
        elif i == 6:
            dayCourse = sun

        for course in dayCourse:
            day = i + 1
            courseName = course[0]
            week = course[1]
            period = course[2]
            try:
                place = course[3]
                strategy = '全'
                try:
                    if u"(单)" == course[3][:3]:
                        strategy = '单'
                        place = course[3][3:]
                    elif u"(双)" == course[3][:3]:
                        strategy = '双'
                        place = course[3][3:]
                except:
                    pass
            except:
                place = ''
                strategy = '全'
            Curriculum.objects.create(openId=openId, day=day, courseName=courseName,
                                      week=week, period=period, place=place, strategy=strategy)

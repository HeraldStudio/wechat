# -*- coding:utf-8 -*-
from app.models import Curriculum
from app.tools.getTime import getWeekDay, getHour, getMin


def getDayCourse(openId,day):
    dayCourse = Curriculum.objects.filter(openId=openId, day=day)
    infor = u''
    for i in dayCourse:
        if i.strategy != u'全':
            infor += u'(' + i.strategy + u') '
        infor += i.courseName + u'\n' + i.week + \
            u'周  ' + i.period + u'节\n' + i.place + u'\n\n'
    if not dayCourse:
        infor = u'没课哦'
    if infor[-2:] == u'\n\n':
        infor = infor[:-2]
    return infor


def getNextCourse(openId):
    w = getWeekDay()
    h = getHour()
    m = getMin()
    courses = Curriculum.objects.order_by('week').filter(openId=openId, day=w)
    nextCourse = ''

    if h < 8:
        for i in courses:
            if int(i.period[:1]) < 3 and i.period[1:2] == '-':
                nextCourse = i
                break
        if nextCourse == u'':
            nextCourse = u'none'
    elif (h < 9 or (h == 9 and m < 45)) or nextCourse == u'none':
        for i in courses:
            if int(i.period[:1]) > 2 and int(i.period[:1]) < 5:
                nextCourse = i
                break
        if nextCourse == u'':
            nextCourse = u'none'
    elif h < 14  or nextCourse == u'none':
        for i in courses:
            if int(i.period[:1]) >= 5 and int(i.period[:1]) < 9:
                nextCourse = i
                break
        if nextCourse == u'':
            nextCourse = u'none'
    elif (h < 15 or (h == 15 and m < 45)) or nextCourse == u'none':
        for i in courses:
            if int(i.period[:1]) >=9 and int(i.period[:1]) <10 :
                nextCourse = i
                break
        if nextCourse == u'':
            nextCourse = u'none'
    elif (h < 18 or (h == 18 and m < 30)) or nextCourse == u'none':
        for i in courses:
            try:
                if int(i.period[:2]) >= 10:
                    nextCourse = i
                    break
            except:
                continue
    infor = u''
    try:
        if i.strategy != u'全':
            infor += u'(' + i.strategy + u') '
        infor += nextCourse.courseName + u'\n' + nextCourse.week + \
            u'周  ' + nextCourse.period + u'节\n' + nextCourse.place
    except:
        infor = u'下节没课哦'
    return infor

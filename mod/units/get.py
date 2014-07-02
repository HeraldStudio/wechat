# -*- coding: utf-8 -*-
# @Date    : 2014-07-01 21:26:10
# @Author  : xindervella@gamil.com
from tornado.httpclient import HTTPRequest, HTTPClient
from ..models.course import Course
from ..models.gpa import Overview as GPAO
from ..models.srtp import Overview as SRTPO
from config import LOCAL, SERVICE, LIBRARY, TIME_OUT
import urllib
import json
import re


def curriculum(db, user, day):
    courses = db.query(Course).filter(
        Course.openid == user.openid, Course.day == day).all()
    p = re.compile(r'\[|\]|\(|\)')
    msg = u''
    for course in courses:
        msg += course.course + u'\n' + \
            '   '.join(p.split(course.period)).strip() + u'\n' + \
            '   '.join(p.split(course.place)).strip() + u'\n\n'
    if not msg:
        msg = u'没课哦'
    msg = msg.strip() + '\n\n' + \
        u'<a href="%s/curriculum/%s">查看课表</a>' % (
            LOCAL, user.openid)
    return msg


def pe_counts(user):
    client = HTTPClient()
    if user.pe_password:
        pwd = user.pe_password
    else:
        pwd = user.cardnum
    params = urllib.urlencode({
        'cardnum': user.cardnum,
        'pwd': pwd
    })
    request = HTTPRequest(SERVICE + 'pe', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except:
        return u'=。= 体育系暂时无法连接，不如待会再试试吧'
    if response.body == 'time out':
        return u'=。= 体育系暂时无法连接，不如待会再试试吧'
    elif response.body == 'wrong card number or password':
        return u'<a href="%s/register/%s">=。= 同学，密码错了吧，快点我重新绑定。</a>' % (
            LOCAL, user.openid)
    else:
        try:
            counts = int(response.body)
            return u'当前跑操次数 %d 次' % counts
        except:
            return u'=。= 出了点故障，不如待会再试试吧'


def rendered(user):
    client = HTTPClient()
    params = urllib.urlencode({
        'username': user.lib_username,
        'password': user.lib_password
    })
    request = HTTPRequest(LIBRARY, method='POST', body=params,
                          request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except:
        return u'=。= 图书馆暂时无法连接，不如待会再试试'
    if response.body == 'server error':
        return u'=。= 图书馆暂时无法连接，不如待会再试试'
    elif response.body == 'username or password error':
        return u'<a href="%s/register/%s">=。= 同学，用户名/密码错了吧，快点我重新绑定。</a>' % (
            LOCAL, user.openid)
    else:
        msg = u''
        try:
            books = json.loads(response.body)
            for book in books:
                detail = u'\n%s\n%s\n借书时间：%s\n到期时间：%s' % (
                    book['author'], book['place'],
                    book['render_date'], book['due_date'])
                if book['renew_time'] == u'0':
                    msg += u'<a href="%s/renew/%s/%s">《%s》</a>%s' % (
                        LOCAL, user.openid, book['barcode'],
                        book['title'], detail)
                else:
                    msg += u'《%s》%s\n续借次数：%s' % (
                        book['title'], detail, book['renew_time'])
                msg += u'\n\n'
            msg += u'如果要续借的话请戳书名'
            if not msg:
                msg = u'没有在图书馆借书哦'
            return msg.strip()
        except:
            return u'=。= 图书馆暂时无法连接，不如待会再试试'


def gpa(db, user):
    try:
        overview = db.query(GPAO).filter(
            GPAO.openid == user.openid).one()
        if overview.gpa:
            msg = u'总绩点：%s\n首修绩点：%s\n计算时间：%s\n\n' % (
                overview.gpa, overview.before_revamp,
                overview.calc_time.split(' ')[0])
            msg += u'<a href="%s/gpa/%s">GPA详情</a>' % (
                LOCAL, user.openid)
        else:
            msg = u'你们学院居然没有计算GPA？\n\n<a href="%s/gpa/%s">GPA详情</a>' % (
                LOCAL, user.openid)

    except:
        msg = u'<a href="%s/register/%s">居然没有绩点你敢信？你不是把一卡通/\
密码输错了吧，快点我修改。</a>' % (LOCAL, user.openid)
    finally:
        return msg


def srtp(db, user):
    try:
        overview = db.query(SRTPO).filter(
            SRTPO.openid == user.openid).one()
        msg = u'总分：%s\n成绩：%s\n\n' % (
            overview.total, overview.score)
        msg += u'<a href="%s/srtp/%s">SRTP详情</a>' % (
            LOCAL, user.openid)
    except:
        msg = u'<a href="%s/register/%s">=。= 同学，你不是把学号填错了，快点我修改。</a>' % (
            LOCAL, user.openid)
    finally:
        return msg

# -*- coding: utf-8 -*-
# @Date    : 2014-07-01 21:26:10
# @Author  : xindervella@gamil.com yml_bright@163.com
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from sqlalchemy.sql import or_
from ..models.course import Course
from ..models.gpa import Overview as GPAO
from ..models.srtp import Overview as SRTPO
from weekday import today, tomorrow
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

def new_curriculum(db, user):
    courses = db.query(Course).filter(
        Course.openid == user.openid, or_(Course.day == today(), Course.day == tomorrow())).all()
    p = re.compile(r'\[|\]|\(|\)')
    msg = u''
    for course in courses:
        msg += course.course + u'\n' + \
            '   '.join(p.split(course.period)).strip() + u'  ' + course.day + u'\n' + \
            '   '.join(p.split(course.place)).strip() + u'\n\n'
    if not msg:
        msg = u'没课哦'
    msg = msg.strip() + '\n\n' + \
        u'<a href="%s/curriculum/%s">查看课表</a>' % (
            LOCAL, user.openid)
    return msg


def pe_counts(user):
    client = HTTPClient()
    params = urllib.urlencode({
        'uuid': user.uuid
    })
    request = HTTPRequest(SERVICE + 'pe', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except HTTPError:
        self.write('<a href="%s/register/%s">你不是把一卡通密码输错了吧，快点我修改。</a>')
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
    params = urllib.urlencode({'uuid': user.uuid})
    request = HTTPRequest(SERVICE + 'library', method='POST', body=params,
                          request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except HTTPError:
        self.write('<a href="%s/register/%s">你不是把一卡通密码输错了吧，快点我修改。</a>')
    except:
        return u'=。= 暂时无法连接，不如待会再试试'
    if response.body == 'error':
        return u'=。= 暂时无法连接，不如待会再试试'
    elif response.body == 'wrong card number or password':
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
            if not msg:
                msg = u'没有在图书馆借书哦'
            else:
                msg += u'如果要续借的话请戳书名'
            return msg.strip()
        except:
            return u'=。= 暂时无法连接，不如待会再试试'


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
        msg = u'<a href="%s/register/%s">=。= 同学，你不是把学号填错了吧，快点我修改。</a>' % (
            LOCAL, user.openid)
    finally:
        return msg

def lecture(user):
    client = HTTPClient()
    params = urllib.urlencode({'uuid': user.uuid})
    request = HTTPRequest(SERVICE + 'lecture', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except HTTPError:
        self.write('<a href="%s/register/%s">你不是把一卡通密码输错了吧，快点我修改。</a>')
    except:
        return u'=。= 暂时无法连接，不如待会再试试吧'
    if response.body == 'time out':
        return u'=。= 暂时无法连接，不如待会再试试吧'
    elif response.body == 'wrong card number or password':
        return u'<a href="%s/register/%s">=。= 同学，密码错了吧，快点我重新绑定。</a>' % (
            LOCAL, user.openid)
    else:
        try:
            ret = json.loads(response.body)
            msg = u""
            for d in ret['detial']:
                msg += u"%s\n%s\n\n"%(d['date'], d['place'])
            msg += u'当前人文讲座次数 %s 次' % ret['count']
            return msg
        except:
            return u'=。= 出了点故障，不如待会再试试吧'

def nic(user):
    client = HTTPClient()
    params = urllib.urlencode({'uuid': user.uuid})
    request = HTTPRequest(SERVICE + 'nic', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except HTTPError:
        self.write('<a href="%s/register/%s">你不是把一卡通密码输错了吧，快点我修改。</a>')
    except:
        return u'=。= 暂时无法连接，不如待会再试试吧'
    if response.body == 'time out':
        return u'=。= 暂时无法连接，不如待会再试试吧'
    elif response.body == 'wrong card number or password':
        return u'<a href="%s/register/%s">=。= 同学，密码错了吧，快点我重新绑定。</a>' % (
            LOCAL, user.openid)
    else:
        try:
            ret = json.loads(response.body)
            return u'卡钱包余额:%s\n流量使用情况:\n brasa[%s]:%s\n brasb[%s]:%s\n web[%s]:%s' % (\
                ret['left'], 
                ret['a']['state'], ret['a']['used'],
                ret['b']['state'], ret['b']['used'],
                ret['web']['state'], ret['web']['used'])
        except:
            return u'=。= 出了点故障，不如待会再试试吧'

def card(user):
    client = HTTPClient()
    params = urllib.urlencode({'uuid': user.uuid})
    request = HTTPRequest(SERVICE + 'card', method='POST',
                          body=params, request_timeout=TIME_OUT)
    try:
        response = client.fetch(request)
    except HTTPError:
        self.write('<a href="%s/register/%s">你不是把一卡通密码输错了吧，快点我修改。</a>')
    except:
        return u'=。= 暂时无法连接，不如待会再试试吧'
    if response.body == 'time out':
        return u'=。= 暂时无法连接，不如待会再试试吧'
    elif response.body == 'wrong card number or password':
        return u'<a href="%s/register/%s">=。= 同学，密码错了吧，快点我重新绑定。</a>' % (
            LOCAL, user.openid)
    else:
        try:
            ret = json.loads(response.body)
            return u'一卡通余额:%s' % ret['left']
        except:
            return u'=。= 出了点故障，不如待会再试试吧'
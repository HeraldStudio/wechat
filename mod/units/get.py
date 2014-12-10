# -*- coding: utf-8 -*-
# @Date    : 2014-07-01 21:26:10
# @Author  : xindervella@gamil.com yml_bright@163.com
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from sqlalchemy.sql import or_
from ..models.course import Course
from ..models.gpa import Overview as GPAO
from ..models.srtp import Overview as SRTPO
from weekday import today, tomorrow, changedate
from config import LOCAL
from get_api_return import get_api_return
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
    daymap = {'Mon':u'周一', 'Tue':u'周二', 'Wed':u'周三', 'Thu':u'周四', 'Fri':u'周五', 'Sat':u'周六', 'Sun':u'周日'}
    courses = db.query(Course).filter(
        Course.openid == user.openid, Course.day == changedate()).all()
    p = re.compile(r'\[|\]|\(|\)')
    msg = u''
    for course in courses:
        msg += course.course + u'\n' + \
            '   '.join(p.split(course.period)).strip() + u'  ' + daymap[course.day] + u'\n' + \
            '   '.join(p.split(course.place)).strip() + u'\n\n'
    if not msg:
        msg = u'没课哦'
    msg = msg.strip() + '\n\n' + \
        u'<a href="%s/curriculum/%s">查看课表</a>' % (
            LOCAL, user.openid)
    return msg

def pe_counts(user):
    response = get_api_return('pe', user)
    if response['code'] == 200:
        return u'当前跑操次数 %s 次' % response['content']
    else:
        return response['content']


def rendered(user):
    response = get_api_return('library', user)
    msg = u''
    if response['code'] == 200:
        try:
            books = response['content']
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
            return u'=。= 出了点故障，不如待会再试试吧'
    else:
        return response['content']


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
    response = get_api_return('lecture', user)
    if response['code'] == 200:
        ret = response['content']
        msg = u""
        for d in ret['detial']:
            msg += u"%s\n%s\n\n"%(d['date'], d['place'])
        msg += u'当前人文讲座次数 %s 次' % ret['count']
        return msg
    else:
        return response['content']

def nic(user):
    response = get_api_return('nic', user)
    if response['code'] == 200:
        ret = response['content']
        return u'卡钱包余额:%s\n流量使用情况:\n brasa[%s]:%s\n brasb[%s]:%s\n web[%s]:%s' % (\
                ret['left'], 
                ret['a']['state'], ret['a']['used'],
                ret['b']['state'], ret['b']['used'],
                ret['web']['state'], ret['web']['used'])
    else:
        return response['content']

def card(user):
    response = get_api_return('card', user)
    if response['code'] == 200:
        ret = response['content']
        return u'一卡通余额:%s' % ret['left']
    else:
        return response['content']
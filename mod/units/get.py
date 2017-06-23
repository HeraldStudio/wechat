# -*- coding: utf-8 -*-
# @Date    : 2014-07-01 21:26:10
# @Author  : xindervella@gamil.com yml_bright@163.com
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from sqlalchemy.sql import or_
from ..models.course import Course
from ..models.gpa import Overview as GPAO
from ..models.srtp import Overview as SRTPO
from ..models.lecturedb import LectureDB
# from ..models.eat import Eat
from weekday import today, tomorrow, changedate, ismorning
from config import LOCAL,SERVICE,TIME_OUT
from get_api_return import get_api_return
import urllib
import json
import re,traceback
import datetime,time,sys
from time import strftime, mktime, localtime, strptime

from sqlalchemy.orm.exc import NoResultFound
reload(sys)
sys.setdefaultencoding('utf-8')

def curriculum(db, user, day):
    courses = db.query(Course).filter(
        Course.openid == user.openid, Course.day == day).all()
    p = re.compile(r'\[|\]|\(|\)')
    msg = u'<a href="%s/update/curriculum/%s">更新课表</a>\n\n' % (LOCAL, user.openid)
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
    msg = u'<a href="%s/update/curriculum/%s">更新课表</a>\n\n' % (LOCAL, user.openid)
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
    msg = u''
    response = get_api_return('pe', user)
    if response['code'] == 200:
        msg += u'当前跑操次数 %s 次' % response['content']
        msg += u'\n您的跑操次数击败了%s%%的人' % response['rank']
        msg += u'\n<a href="%s/pedetail/%s">跑操明细</a>' % (LOCAL, user.openid)
    else:
        msg += response['content']
    if ismorning():
        response = get_api_return('pc', user)
        if response['code'] == 201:
            msg += u'\n\n0.0, 早起有益健康，小猴正在获取跑操情报，等会再试试'
        else:
            msg += u'\n\n小猴猜测：' + response['content']
    msg += u'\n输入[预约]预约场馆'
    msg += u'\n输入[体测]查看体测成绩'
    return msg

def phylab(user):
    response = get_api_return('phylab',user)
    msg = u''
    if response['code'] ==200:
        content = response['content']
        for labType in content:
            if content[labType]!='':
                msg +=u'%s:\n' %labType
                for lab in content[labType]:
                    msg +=u'%s\n' %lab['name']
                    msg +=u'%s   ' %lab['Teacher']
                    if not lab['Grade']:
                        msg +=u'%s\n' %lab['Address']
                        msg +=u'%s %s\n' %(lab['Date'],lab['Day'])
                    else:
                        msg +=u'成绩:%s\n' %lab['Grade']
                msg +=u'\n\n'
        if not msg:
            return u'没有物理实验哦'
        return msg[:-2]
    elif response['code'] == 599:
        return u"正在获取最新数据，再点一次就有啦！"
    else:
        return response['content']
def exam(user):
    response = get_api_return('exam',user)
    if response['code'] == 200:
        msg = ''
        content = response['content']
        for item in content:
            msg += u'> %s\n' % item['course']
            msg += u'%s    %s分钟\n' % (item['teacher'],item['hour'])
            msg += u'%s\n' % item['location']
            msg += u'%s\n' % item['time']
            msg += u'\n'
        if not msg:
            msg = u'没有查询到考试安排哦'
        return msg
    elif response['code'] == 599:
        return u"正在获取最新数据，再点一次就有啦！"
    else:
        return response['content']

def tice(user):
    response = get_api_return('tice',user)
    if response['code'] == 200:
        msg = ''
        content = response['content']
        msg += u'总成绩:  %s\n' % content['score']
        msg += u'>身高,体重:  %s %s\n' %(content['height'],content['weight'])
        msg += u'>立定跳远: %s %s\n' % (content['jump']['comment'],content['jump']['value'])
        msg += u'>坐位体前屈: %s %s\n' % (content['zuoqian']['comment'],content['zuoqian']['value'])
        msg += u'>50米: %s %s\n' % (content['50meter']['comment'],content['50meter']['value'])
        msg += u'>1000(800)米: %s %s\n' % (content['1000meter']['comment'],content['1000meter']['value'])
        msg += u'>肺活量: %s %s\n' % (content['fei']['comment'],content['fei']['value'])
        msg += u'>仰卧起坐(引体向上): %s %s\n' % (content['up-down']['comment'],content['up-down']['value'])
        return msg
    elif response['code'] == 599:
        return u"正在获取最新数据，再点一次就有啦！"
    else:
        return response['content']
def room(user):
        response = get_api_return('room',user)
        msg = u''
        if response['code'] ==200:
            content = response['content']
            if u'园' in content['room']:
                msg += content['room']
                msg += content['bed']
            else:
                msg += u'宿舍信息可能还没公布~'
                return msg
            if not msg:
                return u'暂且没有查到数据 T_T'
            return msg
        elif response['code'] == 599:
            return u"正在获取最新数据，再发一次就有啦"
        elif response['code'] == 408:
            return u"正在获取最新数据，再发一次就有啦!"
        else:
            return response['content']

def schoolnumber(user):
    response = get_api_return('user',user)
    if response['code'] == 200:
        content = response['content']['schoolnum']
        if content != '00000000':
            msg = content
        else:
            msg = u'暂时没有查到学号哦~'
        return msg
    elif response['code'] == 599:
        return u"正在获取最新数据，再点一次就有啦！"
    else:
        return response['content']    

def rendered(user):
    response = get_api_return('library', user)
    msg = u''
    if response['code'] == 200:
        try:
            books = response['content']
            for book in books:
                detail = u'\n%s\n借书时间：%s\n到期时间：%s' % (
                    book['author'],
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
    msg = u'<a href="%s/update/gpa/%s">更新GPA</a>\n\n' % (LOCAL, user.openid)
    try:
        overview = db.query(GPAO).filter(
            GPAO.openid == user.openid).one()
        if overview.gpa:
            msg += u'总绩点：%s\n首修绩点：%s\n计算时间：%s\n\n' % (
                overview.gpa, overview.before_revamp,
                overview.calc_time.split(' ')[0])
            msg += u'<a href="%s/gpa/%s">GPA详情</a>' % (
                LOCAL, user.openid)
        else:
            msg += u'你们学院居然没有计算GPA？\n\n<a href="%s/gpa/%s">GPA详情</a>' % (
                LOCAL, user.openid)

    except:
        msg += u'居然没有绩点你敢信？<a href="%s/register/%s">你不是把一卡通/\
密码输错了吧，快点我修改。</a>还是没有更新过GPA？快点上方的更新吧。' % (LOCAL, user.openid)
    finally:
        return msg


def srtp(db, user):
    msg = u'<a href="%s/update/srtp/%s">更新SRTP</a>\n\n' % (LOCAL, user.openid)
    try:
        overview = db.query(SRTPO).filter(
            SRTPO.openid == user.openid).one()
        msg += u'总分：%s\n成绩：%s\n\n' % (
            overview.total, overview.score.decode('utf-8').encode('utf-8'))
        msg += u'<a href="%s/srtp/%s">SRTP详情</a>' % (
            LOCAL, user.openid)
    except Exception,e:
        print str(e)
        print traceback.print_exc()
        msg += u'<a href="%s/register/%s">=。= 同学，你不是把学号填错了吧，快点我修改。</a>还是没有更新过SRTP？快点上方的更新吧。' % (
            LOCAL, user.openid)
    finally:
        return msg




def grade(db, user):
    return gpa(db, user) + '\n\n\n' + srtp(db, user)

def lecture(user):
    response = get_api_return('lecture', user)
    if response['code'] == 200:
        ret = response['content']
        msg = u""
        for d in ret['detial']:
            msg += u"%s\n%s\n\n"%(d['date'], d['place'])
        msg += u'当前人文讲座次数 %s 次' % ret['count']
        msg += u'\n<a href="http://www.heraldstudio.com/wechat2/lecturequery">点我查询讲座信息~</a>'
        return msg
    elif response['code'] == 599:
        msg = u"正在获取最新数据，再点一次就有啦！"
        msg += u'\n<a href="http://www.heraldstudio.com/wechat2/lecturequery">点我查询讲座信息~</a>'
        return msg
    else:
		msg = response['content']
		msg += u'\n<a href="http://www.heraldstudio.com/wechat2/lecturequery">点我查询讲座信息~</a>'
		return msg

def lecturenotice(db,user):
    retjson = {'code':500, 'content':u'暂无'}
    date = mktime(strptime(strftime('%Y-%m-%d' ,localtime(time.time())), '%Y-%m-%d'))

    # read from db
    try:
        status = db.query(LectureDB).filter( LectureDB.date >=  date ).all()
        if len(status) > 0:
            ret = []
            for l in status:
                ret.append({
                    'date': l.time,
                    'topic': l.topic,
                    'speaker': l.speaker,
                    'location': l.location,
                    'detail': l.detail
                    })
            retjson['code'] = 200
            retjson['content'] = ret
    except NoResultFound:
        pass
    # response = get_api_return('lecturenotice', user)
    response = retjson
    if response['code'] == 500:
        return lecture(user)
    else:
        msg = u'人文讲座预告:\n'
        for lec in response['content']:
            msg += u"> %s\n> %s\n"%(lec['topic'], lec['speaker'])
            msg += u"> %s\n> %s\n\n"%(lec['date'], lec['location'])
            #msg += u'<a href="%s#%s">戳我查看详细信息</a>\n\n'%(lec['detail'],lec['topic'])
        msg += u"查询讲座次数请在非调戏状态输入[讲座次数]"
        msg += u'\n<a href="http://www.heraldstudio.com/wechat2/lecturequery">点我查询讲座信息~</a>'
        return msg

def nic(user):
    response = get_api_return('nic', user)
    if response['code'] == 200:
        ret = response['content']
        return u'卡钱包余额:%s\n流量使用情况:\n  web[%s]:%s' % (\
                ret['left'], 
                ret['web']['state'], ret['web']['used'])
    elif response['code'] == 599:
        return u"正在获取最新数据，再点一次就有啦！"
    else:
        return response['content']

def card(user):
    response = get_api_return('card', user)
    if response['code'] == 200:
        ret = response['content']
        msg = u'一卡通余额:%s' % ret['left']
        msg += u'\n\n<a href="%s/card/%s">一卡通交易明细</a>' % (
            LOCAL, user.openid)
        msg += u"\n\n<a href='http://58.192.115.47:8088/wechat-web/login/dologin.html'>点我进行充值</a>"
        msg += u"\n微信充值后需到食堂pos机上刷卡写卡，若失败，则请尝试在圈存机上转账少数钱写卡(此功能不由小猴开发,近期由于网络原因可能不太稳定~)"
	msg += u"\n<a href='http://url.cn/41x4fjh'>更多问题请戳我</a>"
        return msg
    elif response['code'] == 599:
        msg = u"\n\n<a href='http://58.192.115.47:8088/wechat-web/login/dologin.html'>点我进行充值</a>"
        return u"正在获取最新数据，再点一次就有啦！%s" % msg
    else:
        return response['content']




def jwc(user):
    response = get_api_return('jwc', user)
    if response['code'] == 200:
        msg = u'最新动态:\n'
        ret = response['content']
        for m in ret[u'最新动态']:
            msg += u'● <a href="%s">%s - %s</a>\n' % (m['href'], m['title'], m['date'][2:].replace('-',''))
        #msg += u'\n\n实践教学:\n'
        #for m in ret[u'实践教学']:
        #    msg += u'● <a href="%s">%s - %s</a>\n' % (m['href'], m['title'], m['date'][2:].replace('-',''))
        return msg[:-1]
    elif response['code'] == 201:
        return u'小猴正在获取教务信息，等会再试试'
    else:
        return response['content']

def searchlib(user, text):
    data = {'book': text.strip().encode('utf-8')}
    if len(data['book'])<2:
        return u'至少要输入两个关键字'
    response = get_api_return('search', user, data)
    if response['code'] == 200:
        ret = response['content']
        msg = u'搜索结果:\n'
        for m in ret:
            msg += u'●(%s)%s[%s/%s] - %s\n' % (
                    m['index'], m['name'],
                    m['left'], m['all'], m['author'])
        msg += u'\n大致藏书范围\nA~E: 中图1(二楼)\nF~G: 中图2(二楼)\nH: 中图3(二楼)\nI~J: 友丰(五楼)\
                 \nK~TF: 中图3(一楼)\nTG~TP311: 中图4(二楼)\nTP311~Z: 中图4(一楼)\n外文图书: 外图(四楼)'
        return msg
    else:
        return response['content']

def schoolbus(user):
    response = get_api_return('schoolbus', user)
    daymap = {'Mon':u'周一', 'Tue':u'周二', 'Wed':u'周三', 'Thu':u'周四', 'Fri':u'周五', 'Sat':u'周六', 'Sun':u'周日'}
    if response['code'] == 200:
        if today() in ['Sat', 'Sun']:
            ret = response['content']['weekend']
        else:
            ret = response['content']['weekday']
        msg = u'Tips:\n今天%s\n到地铁站时，乘车途中只上不下。到九龙湖时，乘车途中只下不上\n' % daymap[today()]
        msg += u'出九龙湖路线：\n校内停车场-->材料学院、图书馆-->文学院-->西门\n-->橘园-->行政楼-->电工电子\n-->梅园-->教八-->北门-->地铁停靠站'
        msg += u'\n前往地铁站:\n'
        for m in ret[u'前往地铁站']:
            msg += u'[%s] - %s\n' % ( m['time'], m['bus'] )
        msg += u'\n返回九龙湖:\n'
        for m in ret[u'返回九龙湖']:
            msg += u'[%s] - %s\n' % ( m['time'], m['bus'] )
        return msg[:-1]
    else:
        return response['content']


# def eatHandler(db):
#     msg = u''
#     hour = time.strftime('%H',time.localtime(time.time()))
#     day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
#     today = time.strftime('%Y-%m-%d-%H',time.localtime(time.time()))
#     try:
#         item = db.query(Eat).filter(Eat.day == day).one()
#         if item.status == 1:
#             msg +=u'据可靠情报，今晚会有美食哦~ --更新于%s时' % item.time
#         else:
#             msg +=u'据可靠情报，今晚他们不能来了T T --更新于%s时' % item.time
#     except:
#         msg +=u'暂时还没有信息哦~小猴正在积极联系他们'
#     finally:
#         return msg


def yuyue(user):
    msg = u'<a href="http://www.heraldstudio.com/heraldapp/#/yuyue/home">点我进行预约</a>近期有同学反馈预约有时会出现问题，如果大家发现，请及时反馈。谢谢大家'
    return msg


def dm(user,content):
    url = u'http://127.0.0.1:8080/'
    client = HTTPClient()
    nowtime = int(time.time())
    data = {
        'time':nowtime,
        'content':content.strip().encode('utf-8'),
        'movieid':'000000001',
        'studentNum':user.cardnum
    }

    if len(content.strip()) > 200:
        return u"弹幕发送失败, 长度过长"

    params = urllib.urlencode(data)
    request = HTTPRequest(url, method='POST',
                          body=params, request_timeout=4)
    try:
        response = client.fetch(request)
        return u"弹幕发送成功"
    except:
        return u"弹幕发送失败, 请稍后再试"



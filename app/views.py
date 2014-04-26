# -*- coding:utf-8 -*-
import hashlib
#import logging
import time
from django.shortcuts import render_to_response
from app.models import UserInfo, Curriculum
from app.tools.getCurriculum import getDayCourse, getNextCourse
from app.tools.getJwcInfor import getJwcInfor
from app.tools.getLibrary import getLibrary
from app.tools.getLost import getLost
from app.tools.getTime import getWeekDay
from app.tools.getTyxPc import getTyxPc
from app.tools.setCurriculum import setCurriculum
from app.tools.simisimi_api import simsimi, simsimi_back
#from tools.log import *
from xml.etree import ElementTree as ET
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#logger = logging.getLogger('xchat.app')


@csrf_exempt
def wechatService(request):
    try:
        if request.method == 'GET':
            try:
                token = 'xindervella'
                args = [token, request.GET['timestamp'], request.GET['nonce']]
                args.sort()
                echostr = request.GET['echostr']
                if hashlib.sha1("".join(args)).hexdigest() == request.GET['signature']:
                    return HttpResponse(echostr)
                return HttpResponse(echostr)
            except:
                return HttpResponse('Invalid request')

        if request.method == "POST":
            try:
                reply = '''
                        <xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                        <FuncFlag>0</FuncFlag>
                        </xml>
                        '''

                if request.body:
                    received_xml = ET.fromstring(request.body)
                    fromUserName = received_xml.find('ToUserName').text
                    toUserName = received_xml.find('FromUserName').text
                    postTime = str(int(time.time()))
                    msgtype = received_xml.find('MsgType').text
                    user = UserInfo.objects.filter(openId=toUserName)
                    chatStatus = charwithuser.GetStatus(toUserName)

                    if msgtype == u'event':
                        try:
                            event = received_xml.find('Event').text
                        except:
                            event = u''
                        if not event:
                            infor = '什么都没发送'
                        if event == 'subscribe':
                            infor = '<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>\n\n' \
                                    '\n点击相应标签或回复以下关键字会得到你想要的结果:' \
                                    '\n跑操  今天课表  明天课表  下节课 周X课表 借书信息  更新课表\n\n如果有任何未知错误请发邮件给我 xindervella@gmail.com ，十分感谢。' % toUserName
                        elif event == 'CLICK':
                            try:
                                eventKey = received_xml.find('EventKey').text
                            except:
                                eventKey = u''
                            if eventKey == 'CurriculumToday':
                                if user:
                                    infor = getDayCourse(
                                        user[0].openId, getWeekDay())
                                else:
                                    infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'CurriculumTomorrow':
                                if user:
                                    if getWeekDay() == 7:
                                        infor = getDayCourse(
                                            user[0].openId, 1)
                                    else:
                                        infor = getDayCourse(
                                            user[0].openId, getWeekDay() + 1)
                                else:
                                    infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'CurriculumNext':
                                if user:
                                    infor = getNextCourse(user[0].openId)
                                else:
                                    infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'Update':
                                if user:
                                    infor = u'当前绑定一卡通为：' + user[0].cardNumber + u'\n\n<a href="http://herald.seu.edu.cn/xchat/auth/'+ toUserName + u'">点这里更新绑定信息</a>\n'
                                else:
                                    infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'Library':
                                if user:
                                    if not (user[0].libUsername or user[0].libPwd):
                                        infor = '尚未绑定图书馆登陆信息，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                                    else:
                                        infor = getLibrary(user[0].openId)
                                    if infor == 'error':
                                        infor = '绑定图书馆登陆信息有误，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里更新</a>' % toUserName
                                else:
                                    infor = '尚未绑定图书馆登陆信息，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'TyxPc':
                                if user:
                                    if not user[0].pcPwd:
                                        infor = '尚未绑定跑操查询密码，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                                    else:
                                        infor = getTyxPc(user[0].openId)
                                        if infor == 'error':
                                            infor = '绑定跑操查询密码有误，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里更新</a>' % toUserName

                                else:
                                    infor = '尚未绑定跑操查询密码，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'Instruction':
                                infor = '提供日常校园信息查询服务，点击相应标签或回复以下关键字会得到想要的结果:' \
                                        '\n跑操  今天课表  明天课表  下节课 周X课表 借书信息  更新课表' \
                                        '\n\n网络环境影响可能会导致信息延迟或丢失，如果接收不到信息请重试一下。' \
                                        '\n\n更多功能正在玩命开发中... \n注：目前扩展的调戏功能是猴子请来的逗比并非小猴真身。' \
                                        '\n\n此账号由东南大学先声网 (SEU Herald) 维护\n\n如果你有好的建议或者意见请发邮件或者短信给我，\n目前不接受任何形式的广告合作还请理解。' \
                                        '\nEmail: \nxindervella@gmail.com\nTel: \n132 2208 6228 熊海潇\n\n五一期间小猴将下线升级，带来的不便还请理解么么哒！'
                            elif eventKey == 'UpdateCurriculum':
                                if user:
                                    try:
                                        curriculum = Curriculum.objects.filter(
                                            openId=user[0].openId)
                                        curriculum.delete()
                                        setCurriculum(user[0].openId)
                                        infor = '更新成功'
                                    except:
                                        infor = '更新失败，请重试，如果仍然失败请发邮件给我，我会及时修改相关bug。'
                                else:
                                    infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                            elif eventKey == 'JwcInfo':
                                infor = getJwcInfor();
                            elif eventKey == 'lost':
                                infor = getLost()
                            elif eventKey == 'OpenChatWithUser':
                                if chatStatus == 0:
                                    charwithuser.ChangeStatus(toUserName,1)
                                    charwithuser.OpenChat(toUserName)
                                    infor = '正在为你寻找小伙伴哦~'
                                elif chatStatus == 1:
                                    infor = '我们还在为你努力寻找中,不如先喝杯茶吧,不过你也可以点击退出取消配对哦.'
                                elif chatStatus == 11:
                                    charwithuser.ChangeStatus(toUserName,12)
                                    infor = '我们已经为你找到小伙伴啦!什么?不能让你满意?30秒内再次点击配对我们会为你重新寻找小伙伴呢.'
                                elif chatStatus == 12:
                                    charwithuser.DelChat(toUserName)
                                    charwithuser.OpenChat(toUserName)
                                    infor = '正在玩命为你重新寻找小伙伴哦~'
                                else:
                                    infor = "好像,似乎出了一点点小错误,点击退出然后重新寻找小伙伴吧."
                            elif eventKey == 'ExitChatWithUser':
                                charwithuser.DelChat(toUserName)
                                infor = '已经为你清除配对状态了哦~'
                    if msgtype == u'text':
                        try:
                            content = received_xml.find(
                                'Content').text.replace(' ', '')
                        except:
                            content = ''

                        if content == u'今天课表':
                            if user:
                                infor = getDayCourse(
                                    user[0].openId, getWeekDay())
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'教务信息':
                            infor = getJwcInfor();
                        elif content == u'下节课':
                            if user:
                                infor = getNextCourse(user[0].openId)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'跑操':
                            if user:
                                infor = getTyxPc(user[0].openId)
                            else:
                                infor = '尚未绑定跑操查询密码，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'明天课表':
                            if user:
                                if getWeekDay() == 7:
                                    infor = getDayCourse(user[0].openId, 1)
                                else:
                                    infor = getDayCourse(user[0].openId, getWeekDay() + 1)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName

                        elif content == u'借书信息':
                            if user:
                                infor = getLibrary(user[0].openId)
                            else:
                                infor = '尚未绑定图书馆登陆信息，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周一课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 1)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周二课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 2)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周三课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 3)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周四课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 4)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周五课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 5)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周六课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 6)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName
                        elif content == u'周日课表':
                            if user:
                                infor = getDayCourse(user[0].openId, 7)
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName

                        elif content == u'查看绑定信息':
                            if user:
                                infor = u'少年，你的绑定的一卡通是：' + user[0].cardNumber
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName

                        elif content == u'更新课表':
                            if user:
                                try:
                                    curriculum = Curriculum.objects.filter(
                                        openId=user[0].openId)
                                    curriculum.delete()
                                    setCurriculum(user[0].openId)
                                    infor = '更新成功'
                                except:
                                    infor = '更新失败，请重试，如果仍然失败请给我留言，我会及时修改相关bug。'
                            else:
                                infor = '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUserName

                        elif chatStatus==11 or chatStatus==12:
                            fromUserName = toUserName
                            toUserName = charwithuser.GetTarget(toUserName)
                            try:
                                infor = received_xml.find('Content').text
                            except:
                                infor = ''
                        else:
                            if user:
                                infor = "猴子请来的逗比出了点状况需要下线维护（好吧囧其实是我们的服务器出了点状况需要维护）" #simsimi(content)
                            else:
                                infor = "猴子请来的逗比出了点状况需要下线维护 (好吧囧其实是我们的服务器出了点状况需要维护)"

                    return HttpResponse(reply % (toUserName, fromUserName, postTime, infor))
            except Exception, e:
                raise e

    except Exception, e:
#        logException(e)
        return HttpResponse('Error')


def auth(request, offset):
    if request.method == "GET":
        return render_to_response('auth.html', {
            'openId': offset,
        })


@csrf_exempt
def register(request):
    if request.method == "POST":
        if request.POST.get('cardNumber'):
            openId = request.POST.get('openId')
            cardNumber = request.POST.get('cardNumber')
            user = UserInfo.objects.filter(openId=openId)
            try:
                pcPwd = request.POST.get('pcPwd')
            except:
                pcPwd = ''
            try:
                libUsername = request.POST.get('libUsername')
            except:
                libUsername = ''
            try:
                libPwd = request.POST.get('libPwd')
            except:
                libPwd = ''
            if user:
                user[0].cardNumber = cardNumber
                user[0].pcPwd = pcPwd
                user[0].libPwd = libPwd
                user[0].libUsername = libUsername
                user[0].save()
                curriculum = Curriculum.objects.filter(openId=openId)
                curriculum.delete()
                setCurriculum(openId)
                return HttpResponse('success')
            else:
                try:
                    UserInfo.objects.create(
                        openId=openId, cardNumber=cardNumber, pcPwd=pcPwd, libUsername=libUsername, libPwd=libPwd)
                    setCurriculum(openId)
                    return HttpResponse('success')
                except:
                    return HttpResponse('try again')

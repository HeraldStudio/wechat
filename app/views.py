# -*- coding:utf-8 -*-
import hashlib
#import logging
import time
import eventMap
from django.shortcuts import render_to_response
from app.models import UserInfo, Curriculum
#from tools.log import *
from xml.etree import ElementTree as ET
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from app.tools.charwithuser import GetStatus
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
                    chatStatus = GetStatus(toUserName)

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
                            infor = eventClickMap(eventKey,user,fromUserName,toUserName)
                    if msgtype == u'text':
                        try:
                            content = received_xml.find(
                                'Content').text.replace(' ', '')
                        except:
                            content = ''
                        if chatStatus==11 or chatStatus==12:
                            fromUserName = toUserName
                            toUserName = charwithuser.GetTarget(toUserName)
                            try:
                                infor = received_xml.find('Content').text
                            except:
                                infor = ''
                        else:
                            infor = eventTextMap(content,user,fromUserName,toUserName)
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

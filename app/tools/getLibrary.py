# -*- coding:utf-8 -*-
from app.models import UserInfo
import json
import urllib
import urllib2
import app_config

def getLibrary(openId):
    user = UserInfo.objects.filter(openId=openId)
    username = user[0].libUsername
    password = user[0].libPwd
    if user:
        if not (username or password):
            infor = ''
        else:
            userpage = [('username', username), ('password', password)]
            userpage = urllib.urlencode(userpage)
            req = urllib2.Request(
                app_config.LIBARY_REND_URL, userpage)
            infor = ''
            try:
                bookList = json.loads(urllib2.urlopen(req).read())
                for book in bookList:
                    infor += u'书名： ' + book['title'] + u'\n作者：' + book['author'] + book['place'] + u'\n借书时间：' + book['render_date'] + u'\n到期时间： ' + book['due_date']
                    if book['renew_time'] != u'0':
                        infor += u'\n续借次数：' + book['renew_time']
                    if book != bookList[-1]:
                        infor += u'\n\n'
                if infor == '':
                    infor = '没有在图书馆借书哦，或者也有可能是尚未登陆过数字图书馆未完成相关验证无法使用该功能，请使用电脑完成相关验证。'
            except:
                if urllib2.urlopen(req).read() == 'server error':
                    infor = '由于网络原因暂时无法使用，请稍后再试'
                elif urllib2.urlopen(req).read() == 'username or password error':
                    infor = '图书馆用户名密码错误'
    else:
        infor = '未知错误，请给我留言以便查找相关BUG，谢谢。'
    return infor

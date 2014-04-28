# -*- coding:utf-8 -*-
import urllib
from app.models import UserInfo
import app_config

def getTyxPc(openId):
    user = UserInfo.objects.filter(openId=openId)
    if user:
        cardNumber = user[0].cardNumber
        password = user[0].pcPwd
    uFile = urllib.urlopen(
        app_config.PAOCAO_URL+"%s/%s/" % (cardNumber, password))
    number = uFile.read()
    if number == '一卡通/密码不正确，跑操查询初始密码为一卡通号，请仔细检查哦':
        return 'error'
    elif number == 'Server Error':
        return '一卡通/密码不正确，跑操查询初始密码为一卡通号，请仔细检查哦'
    elif number == '体育系故障，请稍后再试':
        return ':( 暂时无法连接体育系服务器，可能是因为体育系服务器宕机。（体育系服务器经常抽风，一般一抽就是一天囧。)'
    elif len(number) > 4:
        return '尚未绑定跑操密码'
    return '已经跑操 ' + number + ' 次'

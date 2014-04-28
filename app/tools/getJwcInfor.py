# -*- coding:utf-8 -*-
import json
import urllib
import app_config

def getJwcInfor():
    uFile = urllib.urlopen(app_config.JWC_INFO_URL)
    inforList = json.loads(uFile.read())
    infor = ''
    for i in inforList:
        infor += i[2] + '\n' + i[1] + '  ' + i[0] + '\n'
        if i[3]:
            infor += u'附件:' + '\n'
            for j in i[3]:
                try:
                    infor += '<a href="'+j[1] + '">' + j[0] + '</a>' + '\n'
                except:
                    infor = infor[:-2]
        infor += '\n'
        if i is inforList[3]:
            break
    infor += u'点击标题下载相关附件'

    return infor

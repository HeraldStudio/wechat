# -*- encoding: utf-8 -*-
import cookielib
import urllib
import urllib2
import json
import time
import app_config

def getToken():
    try:
        reqjson = json.loads(urllib.urlopen(app_config.TOKEN_URL).read())
        return reqjson['access_token']
    except:
        return ''

def postMsg(toUserID,msg):
    storageToken = getStorageToken()
    if int(storageToken['date']) - time.time() > 7200:
        TOKEN = getToken()
        saveStorageToken(TOKEN,time.time())
    else:
        TOKEN = storageToken['token']
    if TOKEN == '':
        return False

    POST_URL = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token="+TOKEN

    pmsg =  '''
            {
                "touser":"%s",
                "msgtype":"text",
                "text":
                {
                    "content":"%s"
                }
            }
            '''
    try:
        req = urllib2.Request(POST_URL)  
        opener = urllib2.build_opener() 
        response = opener.open(req, pmsg % (toUserID,msg)) 
        return True
    except urllib2.HTTPError, e:
        return False
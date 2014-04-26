# -*- coding:utf-8 -*-

import urllib2
import json
import random
def simsimi_back(input):
    return "猴子请来的逗比需要下线维护一会"

def simsimi(input):
    url = "http://www.simsimi.com/func/reqN?lc=ch&ft=0.0&req=" + input.encode('utf-8')
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
        "Referer": "http://www.simsimi.com/talk_frameview.htm",
        "Cookie": "simsimi_uid=1; selected_nc=ch; selected_nc=ch; menuType=web; menuType=web; __utma=119922954.1279914442.1395033131.1395033131.1397235843.2; __utmb=119922954.55.9.1397237152475; __utmc=119922954; __utmz=119922954.1397235843.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)"
        }
    req = urllib2.Request(url, headers=headers)

    result = json.loads(urllib2.urlopen(req).read())
    if result[u'result'] == 200:
        message = result[u'sentence_resp'].encode('utf-8')
    elif result[u'result'] == 404:
        message = "我看不懂你说什么 T T"
    else:
        return 'T T 我出故障了。。你可以发邮件提醒主人一下么 xindervella@gmail.com'
    spam = ["我说日本你说槽", "贱女人", "我草你妈", "爱吃翔", "傻逼中的大傻逼", "微信搜", "有微信了", "深插!!!(快速深插", "在床上爽死", "我插进去了", "舔你的屁股", "就是木有被人日过的", "你妈逼", "草****逼*****滚***妈****f**k********操", "操翻我", "你麻痹", "尼玛比", "爱死你妈", "操婊子吧", "插我吧", "滚你妈逼", "加微信", "加我微信", "加我搜索", "贱鸡微信", "发语音", "微信号", "搜微信"]
    check_message = ''.join(message.split(' '))
    # print [i for i in spam if i not in check_message]
    flag = True
    for i in spam:
        if i in check_message:
            flag = False
            break
    if flag:
        if random.randint(1, 20) == 1:
            message += "\n该功能测试阶段，如果你发现有广告或者是很不文明的回复请连内容一起邮件发送给我 xindervella@gmail.com 或者短信发送给我 132 2208 6228，么么哒！"
        return message 
    else:
        return "么么哒"

if __name__ == '__main__':
    print simsimi(u'么么哒')

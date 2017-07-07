# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:21:55
# @Author  : xindervella@gamil.com yml_bright@163.com
import hashlib
import time
import xml.etree.ElementTree as ET 


class Message(object):

    TEXT_MSG = u"""
<xml>
<ToUserName><![CDATA[{to_user_name}]]></ToUserName>
<FromUserName><![CDATA[{from_user_name}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>
"""

    PIC_MSG = u"""
<xml>
<ToUserName><![CDATA[{to_user_name}]]></ToUserName>
<FromUserName><![CDATA[{from_user_name}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA[{title}]]></Title> 
<Description><![CDATA[{description}]]></Description>
<PicUrl><![CDATA[{picurl}]]></PicUrl>
<Url><![CDATA[{url}]]></Url>
</item>
</Articles>
</xml> 
"""

  PICTURE_MSG = u"""
<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>12345678</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[media_id]]></MediaId>
</Image>
</xml>
"""

    def __init__(self, token):
        self.token = token
        self.msg = {}

    def check_signature(self, signature, timestamp, nonce):
        tmplist = [self.token, timestamp, nonce]
        tmplist.sort()
        tmpstr = ''.join(tmplist)
        hashstr = hashlib.sha1(tmpstr).hexdigest()

        if hashstr == signature:
            return True
        else:
            return False

    def parse_msg(self, msg):
        root = ET.fromstring(msg)
        for child in root:
            self.msg[child.tag] = child.text
        return self.msg

    @property
    def msg_type(self):
        return self.msg.get('MsgType', None)

    @property
    def event(self):
        return self.msg.get('Event', None)

    @property
    def event_key(self):
        return self.msg.get('EventKey', None)

    @property
    def raw_content(self):
        return self.msg.get('Content', None)

    @property
    def sub_content(self):
        try:
            return self.msg.get('Content', None)[2:]
        except:
            return u''

    def check_user(self,content):
        key={
            'help' : False,
            'change-user': True,
            'srtp': True,
            'play':True,
            'card':True,
            'nic':True,
            'gpa':True,
            'grade':True,
            'lecture':True,
            'lecturenotice':True,
            'library':True,
            'searchlib':True,
            'pe':True,
            'tomorrow-curriculum':True,
            'new-curriculum':True,
            'update-curriculum':True,
            'update-gpa':True,
            'update-srtp':True,
            'jwc':True,
            'schoolbus':True,
            'phylab':True,
            'quanyi':False,
            'yuyue':False,
            'xiaoli':False,
            'exam':True,
            'feedback':True,
            'tice':True,
            'app':False,
            'xinli':False,
            'nothing':True,
            'room':True,
	    'schoolnum':True,
            'dm':False,
	    'newseu':False,
			'bonus':False
            'unicom':False
            }
        try:
            return key[content]
        except KeyError:
            return False

    def content_key(self,content):
        key={
            'help' : {'first':'', 'content': [u'怎么用' , u'怎么使用',u'说明']},
            'change-user': {'first':'', 'content': [u'改变用户',u'重新',u'绑定',u'用户']},
            'srtp': {'first':'', 'content': [u'SRTP' ,u'Srtp', u'srtp']},
            'play':{'first':'', 'content': [u'调戏']},
            'card':{'first':'', 'content': [u'一卡通',u'余额']},
            'nic':{'first':'', 'content': [u'流量',u'wed',u'Web',u'网络']},
            'gpa':{'first':'', 'content': [u'绩点', u'Gpa', u'gpa', u'GPA']},
            'grade':{'first':'', 'content': [u'成绩']},
            'lecture':{'first':u'讲座', 'content': [u'次数']},
            'lecturenotice':{'first':u'讲座', 'content': [u'播报',u'列表', u'预告']},
            'library':{'first':u'书', 'content': [u'借阅',u'查询']},
            'pe':{'first':'', 'content': [u'跑操']},
            'new-curriculum':{'first':'',u'更新':'', 'content': [u'课表']},
            'update-gpa':{'first':u'更新', 'content': [u'Gpa',u'GPA',u'绩点']},
            'update-srtp':{'first':u'更新', 'content': [u'srtp',u'Srtp',u'SRTP']},
            'jwc':{'first':'', 'content': [u'教务']},
            'schoolbus':{'first':'', 'content': [u'校车']},
            'phylab':{'first':'', 'content': [u'物理',u'实验']},
            'quanyi':{'first':'', 'content': [u'权益']},
            'yuyue':{'first':'','content':[u'预约']},
	    'xiaoli':{'first':'','content':[u'校历']},
	    'exam':{'first':'','content':[u'考试安排']},
	    'feedback':{'first':'','content':[u'反馈']},
	    'tice':{'first':'','content':[u'体测',u'体测成绩',u'体育成绩']},
	    'app':{'first':'','content':['app','APP','App']},
	    'newseu':{'first':'','content':[u'新生',u'指南']},
	    'xinli':{'first':'','content':['心理健康中心','绝望','心理健康中心预约']},
	    'schoolnum':{'first':'','content':[u'学号']},
		'bonus':{'first':'','content':['梁界','祁辉','冯裕浩','于海通']}
	    'unicom':{'first':'','content':{u'校园卡','办卡','联通','腾讯校园卡','手机卡'}}
            }

        ticket = [
            u'抢票测试'
        ]
        if not content:
            return 'nothing'
        if content in ticket:
            self.ticket_type = ticket.index(content) + 1
            return 'ticket'
        if content[0:2].lower() == u'ss':
            return 'searchlib'
        if content[0:2].lower() == u'dm':
            return 'dm'
        if u'宿舍' in content:
            return 'room'
        for func in key:
            try:
                if key[func]['first'] in content:
                    for k in key[func]['content']:
                            if k in content:
                                return func
            except KeyError:
                  for k in key[x]:
                        if k in content:
                              return func
        return 'nothing'

    @property
    def content(self):
        content = self.msg.get('Content', None)
        return content

    @property
    def voice_content(self):
        return self.msg.get('Recognition',None)

    @property
    def openid(self):
        return self.msg.get('FromUserName', None)

    def response_text_msg(self, content):
        return self.TEXT_MSG.format(to_user_name=self.msg['FromUserName'],
                                    from_user_name=self.msg['ToUserName'],
                                    create_time=str(int(time.time())),
                                    content=content)

    def response_pic_msg(self, title, pic_url, content, url):
        return self.PIC_MSG.format(to_user_name=self.msg['FromUserName'],
                                    from_user_name=self.msg['ToUserName'],
                                    create_time=str(int(time.time())),
                                    title=title,
                                    description=content,
                                    picurl=pic_url,
                                    url=url)
    def response_picture_msg(self, mediaId):
        return self.PICTURE_MSG.format(to_user_name=self.msg['FromUserName'],
                                    from_user_name=self.msg['ToUserName'],
                                    create_time=str(int(time.time())),
                                    MediaId=mediaId)

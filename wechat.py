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

    @property
    def content(self):
        content = self.msg.get('Content', None)

        key={
            'help' : {'first':'', 'content': [u'怎么用' , u'说明']},
            'change-user': {'first':'', 'content': [u'改变用户',u'重新',u'绑定']},
            'srtp': {'first':'', 'content': [u'SRTP' ,u'Srtp', u'srtp']},
            'play':{'first':'', 'content': [u'调戏']},
            'card':{'first':'', 'content': [u'一卡通',u'余额']},
            'nic':{'first':'', 'content': [u'流量',u'wed',u'Web',u'网络']},
            'gpa':{'first':'', 'content': [u'绩点', u'成绩', u'Gpa', u'gpa', u'GPA']},
            'lecture':{'first':'讲座', 'content': [u'次数']},
            'lecturenotice':{'first':'', 'content': [u'人文讲座', u'讲座']},
            'library':{'first':u'书', 'content': [u'借阅',u'查询']},
            'pe':{'first':'', 'content': [u'跑操']},
            'update-curriculum':{'first':'',u'更新':'', 'content': [u'课表']},
            'update-gpa':{'first':u'更新', 'content': [u'Gpa',u'GPA',u'绩点']},
            'update-srtp':{'first':u'更新', 'content': [u'srtp',u'Srtp',u'SRTP']},
            'jwc':{'first':'', 'content': [u'教务']},
            'schoolbus':{'first':'', 'content': [u'校车']},
            'phylab':{'first':'', 'content': [u'物理',u'实验']},
            'quanyi':{'first':'', 'content': [u'权益']},
            }

        if content[0:2].lower() == u'ss':
            return 'searchlib'

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
    def openid(self):
        return self.msg.get('FromUserName', None)

    def response_text_msg(self, content):
        return self.TEXT_MSG.format(to_user_name=self.msg['FromUserName'],
                                    from_user_name=self.msg['ToUserName'],
                                    create_time=str(int(time.time())),
                                    content=content)

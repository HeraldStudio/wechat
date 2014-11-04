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
    def content(self):
        content = self.msg.get('Content', None)
        if u'更新' in content:
            if u'课' in content:
                return 'update-curriculum'
            elif u'绩' in content:
                return 'update-gpa'
            elif u'gpa' in content:
                return 'update-gpa'
            elif u'GPA' in content:
                return 'update-gpa'
            elif u'Gpa' in content:
                return 'update-gpa'
            elif u'srtp' in content:
                return 'update-srtp'
            elif u'SRTP' in content:
                return 'update-srtp'
            elif u'Srtp' in content:
                return 'update-srtp'
        elif u'课' in content:
            if u'明' in content:
                return 'tomorrow-curriculum'
            else:
                return 'today-curriculum'
        elif u'跑' in content:
            if u'操' in content:
                return 'pe'
            elif u'次' in content:
                return 'pe'
            else:
                return 'nothing'
        elif u'书' in content:
            if u'借' in content:
                return 'library'
            elif u'图' in content:
                return 'library'
        elif u'GPA' in content:
            return 'gpa'
        elif u'Gpa' in content:
            return 'gpa'
        elif u'gpa' in content:
            return 'gpa'
        elif u'绩点' in content:
            return 'gpa'
        elif u'成绩' in content:
            return 'gpa'
        elif u'srtp' in content:
            return 'srtp'
        elif u'SRTP' in content:
            return 'srtp'
        elif u'Srtp' in content:
            return 'srtp'
        elif u'调戏' in content:
            return 'play'
        elif u'绑定' in content:
            return 'change-user'
        elif u'重新' in content:
            return 'change-user'
        elif u'换人' in content:
            return 'change-user'
        elif u'人文' in content:
            return 'lecture'
        elif u'讲座' in content:
            return 'lecture'
        elif u'流量' in content:
            return 'nic'
        elif u'网络' in content:
            return 'nic'
        elif u'Web' in content:
            return 'nic'
        elif u'web' in content:
            return 'nic'
        elif u'一卡通' in content:
            return 'card'
        elif u'余额' in content:
            return 'card'
        elif u'说明' in content:
            return 'help'
        elif u'怎么用' in content:
            return 'help'
        else:
            return 'nothing'

    @property
    def openid(self):
        return self.msg.get('FromUserName', None)

    def response_text_msg(self, content):
        return self.TEXT_MSG.format(to_user_name=self.msg['FromUserName'],
                                    from_user_name=self.msg['ToUserName'],
                                    create_time=str(int(time.time())),
                                    content=content)

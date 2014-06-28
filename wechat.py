# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:21:55
# @Author  : xindervella@gamil.com
import hashlib
import time
from xml.etree import ElementTree as ET


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

    def parser_msg(self, msg):
        root = ET.formstring(msg)
        for child in root:
            self.msg[child.tag] = child.text
        return self.msg

    @property
    def msg_type(self):
        return self.msg.get('MsgType', None)

    @property
    def event(self):
        return self.msg.get('Event', None)

    def response_text_msg(self, content):
        return self.TEXT_MSG.format(to_user_name=self.msg['FromUserName'],
                                    from_user_name=self.msg['ToUserName'],
                                    create_time=str(int(time.time())),
                                    content=content)

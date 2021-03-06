#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-04-18 16:41:24
# @Author  : yml_bright@163.com

import tornado.web
from ..models.ticket import TicketType, TicketUsed, TicketLeft
from config import LOCAL, TICKET_INSTRUCTION, TICKET_URL, QR_PATH
from sqlalchemy.orm.exc import NoResultFound
from random import random
from math import tanh
from time import time, localtime, mktime
import qrcode

def luck_check(time_now, time_enable):
    rate = tanh( (time_now - time_enable)/1800.0 )
    if random() < rate:
        return True
    else:
        return False

def ticket_handler(ticket_type, user, db, wx):
    # user check 
    if not user.uuid: 
        return wx.response_text_msg(
            u'<a href="%s/register/%s">=。= 不如先点我绑定一下？</a>' % (LOCAL, user.openid) )
    
    currentTime = mktime(localtime(time()))
    try:
        ticketInfo = db.query(TicketType).filter(TicketType.ticket_type == ticket_type).limit(1).all()[0]
        ticketInfo.click_count += 1
        db.add(ticketInfo)
        try:
            db.commit()
        except:
            db.rollback()
    except NoResultFound:
        return wx.response_text_msg(u'电子票类型错误,请联系小猴君！')

    # time check
    if currentTime < ticketInfo.ticket_enabletime:
        return wx.response_text_msg(
            u'%s\n%s\n%s' % (ticketInfo.ticket_title, ticketInfo.tag ,TICKET_INSTRUCTION) )
    elif currentTime > ticketInfo.ticket_starttime:
        return wx.response_text_msg(
            u'%s已经结束\n共发放 %s 张票\n响应 %s 次请求'% (ticketInfo.ticket_title, ticketInfo.ticket_count, ticketInfo.click_count))

    # has ticket check
    try:
        ticketCount = db.query(TicketUsed).filter(
            TicketUsed.ticket_type == ticket_type,
            TicketUsed.cardnum == user.cardnum).count()
        if ticketCount > 0:
            return wx.response_text_msg(u'=. = 一个人只能持有一张电子票.')
    except NoResultFound:
        pass
    
    # luck check
    if luck_check(currentTime, ticketInfo.ticket_enabletime):
        ticket = produce_ticket(user, db, ticket_type)
        if ticket == 0:
            return wx.response_text_msg(u'已经没有余票了...')
        elif ticket == -1:
            return wx.response_text_msg(u'运气不佳，再试一次吧')
        else:
            return_pic_ticket(ticket.ticket_id)
            return wx.response_pic_msg(ticketInfo.ticket_title, ticketInfo.ticket_background, u"恭喜，抢到票啦！ 座位：%s" % (ticket.ticket_seat), "%s/#/%s" % (TICKET_URL, ticket.ticket_id) )
    else:
        return wx.response_text_msg(u'运气不佳，再试一次吧')

def return_pic_ticket(ticket_id):
    code = qrcode.QRCode(version = None,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=5,border = 0)
    code.add_data("%s/check.php?token=%s" % (TICKET_URL, ticket_id) )
    code.make(fit=True)
    m = code.make_image()
    m.save("%s%s.png" % (QR_PATH, ticket_id) )
    # return "%s/image/%s.png" % (TICKET_URL, ticket_id)


def produce_ticket(user, db, ticket_type):
    try:
        ticket = db.query(TicketLeft).filter(TicketLeft.ticket_type == ticket_type).limit(1).all()[0]
    except NoResultFound:
        return 0
    except IndexError:
        return 0

    ticketUsed = TicketUsed(
            ticket_id = ticket.ticket_id,
            cardnum = user.cardnum,
            ticket_type = ticket.ticket_type,
            ticket_seat = ticket.ticket_seat
        )
    db.add(ticketUsed)
    try:
        db.commit() # async
    except:
        db.rollback()
        return -1

    db.delete(ticket)
    db.commit()
    return ticketUsed
    





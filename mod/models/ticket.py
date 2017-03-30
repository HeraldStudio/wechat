#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-12-12 12:42:38
# @Author  : yml_bright@163.com

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()

class TicketType(Base):
    __tablename__ = 'ticket_type'
    ticket_type = Column(Integer, nullable=False, primary_key=True)
    ticket_starttime = Column(Integer, nullable=False) # activity start time
    ticket_enabletime = Column(Integer, nullable=False) # get ticket start time
    ticket_title = Column(String(50), nullable=False)
    ticket_background = Column(String(256), nullable=True) # ticket background url
    click_count = Column(Integer, default=0)
    ticket_count = Column(Integer, nullable=False)
    tag = Column(String(100), nullable=True)

class TicketUsed(Base):
    __tablename__ = 'ticket_used'
    ticket_id = Column(String(40), nullable=False, primary_key=True)
    cardnum = Column(String(10), nullable=False)
    ticket_type = Column(ForeignKey(u'ticket_type.ticket_type'))
    ticket_seat = Column(String(50), nullable=False)
    ticket_state = Column(String(1), default='E') # F:freezed  E:enabled  D:disabled

class TicketLeft(Base):
    __tablename__ = 'ticket_left'
    ticket_id = Column(String(40), nullable=False, primary_key=True)
    ticket_type = Column(ForeignKey(u'ticket_type.ticket_type'), index=True)
    ticket_seat = Column(String(50), nullable=False)

def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()


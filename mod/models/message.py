#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-12-12 12:42:38
# @Author  : yml_bright@163.com

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()


class Messsage(Base):
    __tablename__ = 'message'
    openid = Column(String(50), nullable=False, primary_key=True)
    message = Column(String(500), nullable=False)
    timestamp = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    state = Column(Integer, nullable=False)


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()


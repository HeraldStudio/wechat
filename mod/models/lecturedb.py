#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-11-17 11:52:44
# @Author  : jerry.liangj@qq.com

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from db import engine
Base = declarative_base()
class LectureDB(Base):
    __tablename__ = 'db_lecture'
    lid = Column(Integer, primary_key=True)
    date = Column(Integer, index=True)
    speaker = Column(String(128))
    time = Column(String(128))
    location = Column(String(256))
    topic = Column(String(256))
    detail = Column(String(256))

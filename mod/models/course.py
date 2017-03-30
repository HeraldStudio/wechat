# -*- coding: utf-8 -*-
# @Date    : 2014-06-29 15:52:26
# @Author  : xindervella@gamil.com
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    openid = Column(String(50), nullable=True, index=True)
    course = Column(String(50), nullable=True)
    day = Column(String(50), nullable=True)
    place = Column(String(50), nullable=True)
    period = Column(String(50), nullable=True)

    def __repr__(self):
        return '<Course (%s, %s)>' % (self.openid, self.course)


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()

# -*- coding: utf-8 -*-
# @Date    : 2014-07-01 20:27:12
# @Author  : xindervella@gamil.com
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()


class Overview(Base):
    __tablename__ = 'gpa_overview'
    openid = Column(String(50), primary_key=True)
    gpa = Column(String(50), nullable=True)
    before_revamp = Column(String(50), nullable=True)
    calc_time = Column(String(50), nullable=True)

    def __repr__(self):
        return '<GPA (%s, %s)>' % (self.openid, self.gpa)


class Detail(Base):
    __tablename__ = 'gpa_detail'
    id = Column(Integer, primary_key=True)
    openid = Column(String(50), nullable=True, index=True)
    course = Column(String(50), nullable=True)
    credit = Column(String(50), nullable=True)
    semester = Column(String(50), nullable=True)
    score = Column(String(50), nullable=True)
    score_type = Column(String(50), nullable=True)
    extra = Column(String(50), nullable=True)

    def __repr__(self):
        return '<GPA (%s, %s)>' % (self.openid, self.course)


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()

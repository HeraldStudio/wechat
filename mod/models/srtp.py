# -*- coding: utf-8 -*-
# @Date    : 2014-07-02 01:20:10
# @Author  : xindervella@gamil.com
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()


class Overview(Base):
    __tablename__ = 'srtp_overview'
    openid = Column(String(50), primary_key=True)
    total = Column(String(50), nullable=True)
    score = Column(String(50), nullable=True)

    def __repr__(self):
        return '<SRTP (%s, %s)>' % (self.openid, self.total)


class Detail(Base):
    __tablename__ = 'srtp_detail'
    id = Column(Integer, primary_key=True)
    openid = Column(String(50), nullable=True, index=True)
    project = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    date = Column(String(50), nullable=True)
    project_type = Column(String(50), nullable=True)
    total_credit = Column(String(50), nullable=True)
    credit = Column(String(50), nullable=True)
    proportion = Column(String(50), nullable=True)

    def __repr__(self):
        return '<SRTP (%s, %s)>' % (self.openid, self.project)


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()

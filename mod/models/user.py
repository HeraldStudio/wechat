# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 20:03:30
# @Author  : xindervella@gamil.com
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    openid = Column(String(50), primary_key=True)
    cardnum = Column(String(50), nullable=False)
    number = Column(String(50), nullable=True)
    password = Column(String(50), nullable=True)
    pe_password = Column(String(50), nullable=True)
    lib_username = Column(String(50), nullable=True)
    lib_password = Column(String(50), nullable=True)
    uuid = Column(String(50), nullable=True)
    state = Column(Integer, nullable=False)


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()

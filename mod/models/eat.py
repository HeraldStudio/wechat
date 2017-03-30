# -*- coding: utf-8 -*-
# @Date    : 2015-05-28 

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from db import engine

Base = declarative_base()

class Eat(Base):
    __tablename__ = 'eat'
    day = Column(String(50), nullable=True,primary_key=True)
    time = Column(String(50),nullable = True)
    status = Column(Integer,nullable = True)



def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()

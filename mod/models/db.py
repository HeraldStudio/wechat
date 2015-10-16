# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:20:38
# @Author  : xindervella@gamil.com

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PWD = '084358'
DB_NAME = 'herald_wechat2'

from sqlalchemy import create_engine

engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' %
                       (DB_USER, DB_PWD, DB_HOST, DB_NAME),
                       encoding='utf-8', echo=False,
                       pool_size=100, pool_recycle=10)

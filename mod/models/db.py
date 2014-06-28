# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:20:38
# @Author  : xindervella@gamil.com

DB_HOST = ''
DB_USER = ''
DB_PWD = ''
DB_NAME = ''

from sqlalchemy import create_engine

engine = create_engine('mysql://%s:%s@%s/%s' %
                       (DB_USER, DB_PWD, DB_HOST, DB_NAME), echo=False)

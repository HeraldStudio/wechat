# -*- coding: utf-8 -*-
# @Date    : 2014-06-28 13:20:38
# @Author  : xindervella@gamil.com

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PWD = '5t@ihu@idi@nn@0'
DB_NAME = 'webservice'

from sqlalchemy import create_engine

engine = create_engine('mysql://%s:%s@%s/%s' %
                       (DB_USER, DB_PWD, DB_HOST, DB_NAME), echo=False)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging.config
import os

class Config(object):
    APP_NAME=''
    APP_HOST=''
    APP_NICKNAME = ''
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/db_name?charset=utf8&connect_timeout=30'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_TIMEOUT = 100
    SQLALCHEMY_POOL_RECYCLE = 30
    SQLALCHEMY_ECHO = False
    SECRET_KEY = ''
    TMP_FOLDER = '/tmp/public/'
    UPLOAD_FOLDER = 'public/' # 上传文件保存路径
    DEBUG=False
    ALLOWED_IMAGE_EXTENSIONS = set(['.png', '.jpg', '.jpeg', '.gif'])
    # 设置请求内容的大小限制，即限制了上传文件的大小
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MONGO_URI = 'mongodb://127.0.0.1:27017/taskdb'

    @staticmethod
    def init_app(app):
        pass

config = Config()

def config_logging(app):
    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "log.conf"))

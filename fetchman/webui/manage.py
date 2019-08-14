#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from flask_script import Manager

from  gevent import  monkey
#把当前程序的所有的IO操作 单独做上标记
monkey.patch_all()

from app import create_app

reload(sys)
sys.setdefaultencoding('utf8')

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()

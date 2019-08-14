# -*- coding: utf-8 -*-

import datetime
import time
import os
import uuid
import decimal

from app import config

def to_dict(cls, *args):
    if not args:
        args = cls.default_attrs

    result = {}
    for arg in args:
        result[arg] = getattr(cls, arg)
        try:
            # datetime转time
            if isinstance(result[arg], datetime.datetime):
                result[arg] = time.mktime(result[arg].timetuple())
            elif isinstance(result[arg], decimal.Decimal):
                result[arg] = float(result[arg])
        except:
            result[arg] = 0


    return result

def get_form_error(form):
    return form.errors[form.errors.keys()[0]][0]

def get_filepath(filename):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    if not ext:
        ext = '.jpg'

    return '%s%s%s' % (datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d/'),
            uuid.uuid4().hex, ext)

def get_unique_key():
    return uuid.uuid4().hex

def allowed_image(filename):
    """文件格式"""
    if filename == 'blob':
        return True
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    return ext in config.ALLOWED_IMAGE_EXTENSIONS

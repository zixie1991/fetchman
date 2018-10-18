#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import chardet
import hashlib

md5string = lambda x: hashlib.md5(x).hexdigest()

def text(string, encoding='utf8'):
    """
    Make sure string is unicode type, decode with given encoding if it's not.
    If parameter is a object, object.__str__ will been called
    """
    if isinstance(string, six.text_type):
        return string
    elif isinstance(string, six.binary_type):
        return string.decode(encoding)
    else:
        return six.text_type(string)


def text_for_charset(string, encoding='utf8'):
    """
    Make sure string is unicode type, decode with given encoding if it's not.
    If parameter is a object, object.__str__ will been called
    """
    if isinstance(string, six.text_type):
        # 如果是网页的话，尝试保证str的编码为utf-8
        # 基本思路为：str -decode('else charset')-> unicode -encode('utf-8')-> str
        # else charset detect by chardet
        try:
            result = chardet.detect(string)
            string = string.decode(result['encoding'])
        except:
            pass

        return string
    elif isinstance(string, six.binary_type):
        try:
            result = chardet.detect(string)
            return string.decode(result['encoding'])
        except:
            return string.decode(encoding)
    else:
        return six.text_type(string)


def pretty_unicode(string):
    """Make sure string is unicode, try to decode with utf8, or unicode escaped
    string if failed.
    """
    if isinstance(string, six.text_type):
        return string
    try:
        return string.decode("utf8")
    except UnicodeDecodeError:
        return string.decode('Latin-1').encode('unicode_escape')


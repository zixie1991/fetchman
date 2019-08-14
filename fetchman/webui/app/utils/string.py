# -*- coding: utf-8 -*-

import re
import time
import datetime

def get_text_from_html(html):
    p = re.compile('<[^>]+>')
    return p.sub('', html)

def str2time(s, time_format='%Y-%m-%d %H:%M:%S'):
    '''字符串转时间戳
    '''
    return time.mktime(time.strptime(s, time_format))

def time2str(tm, time_format='%Y-%m-%d %H:%M:%S'):
    '''时间戳转字符串
    '''
    return time.strftime(time_format, time.localtime(tm))

def datetime2str(dt, time_format='%Y-%m-%d %H:%M:%S'):
    '''日期转字符串
    '''
    return dt.strftime(time_format)

def str2datetime(s, time_format='%Y-%m-%d %H:%M:%S'):
    '''字符串转日期
    '''
    return datetime.datetime.strptime(s, time_format)

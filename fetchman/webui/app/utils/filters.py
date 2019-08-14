# -*- coding: utf-8 -*-

'''
jinja自定义过滤器
'''
import datetime
import re

def datetime_format(val, format='%Y-%m-%d %H:%M'):
    '''时间格式化
    val: datetime
    '''
    val = datetime.datetime.fromtimestamp(val)
    return val.strftime(format)

def friendly_datetime_format(val, format='%Y-%m-%d'):
    '''友好的时间显示
    val: time
    '''
    val = datetime.datetime.fromtimestamp(val)
    now = datetime.datetime.now()
    if now < val:
        now = val
    interval = now - val
    if interval.days:
        if interval.days <= 3:
            # 几天前（1-3）
            return u'%s天前' % interval.days
        else:
            return val.strftime(format)

    if interval.seconds < 60:
        return u'刚刚'
    elif interval.seconds < 60 * 60:
        return u'%s分钟前' % (interval.seconds / 60)
    else:
        return u'%s小时前' % (interval.seconds / 60 / 60)

def readable_num(x):
    if x >= 100000000:
        return u'%.1f亿' % (x / 100000000.)
    elif x >= 10000:
        return u'%.1f万' % (x / 10000.)

    return x

def category_name(x):
    if x == 1:
        return '电影'
    elif x == 2:
        return '电视剧'
    elif x == 3:
        return '动漫'
    elif x == 4:
        return '综艺'

    return '视频'

def redirect_image(html):
    html = re.sub(r'(.+? src=)"(\S+)"', '\\1/redirect/\\2', html)
    html = re.sub(r'(.+? srcset=)"(\S+)"', '\\1/redirect/\\2', html)
    return html


def init_jinja_filters(app):
    app.jinja_env.filters['datetime_format'] = datetime_format
    app.jinja_env.filters['friendly_datetime_format'] = friendly_datetime_format
    app.jinja_env.filters['readable_num'] = readable_num
    app.jinja_env.filters['category_name'] = category_name
    app.jinja_env.filters['redirect_image'] = redirect_image

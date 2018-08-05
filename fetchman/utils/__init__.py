# -*- coding: utf-8 -*-

import urlparse
import multiprocessing

from fetchman.utils import redismq
from fetchman.utils import rabbitmq
from fetchman.utils.urls import parse_dburl
from fetchman.scheduler.taskdb import TaskDB

def create_taskdb(url):
    return TaskDB(url)

def create_message_queue(url):
    scheme = urlparse.urlparse(url).scheme
    message_queue = None
    options = parse_dburl(url)

    if scheme == 'redismq':
        options['name'] = options['db']
        del options['db']
        message_queue = redismq.Queue(**options)
    elif scheme == 'rabbitmq':
        message_queue = rabbitmq.Queue(options['db'], url)
    else:
        message_queue = multiprocessing.Queue(**options)

    return message_queue

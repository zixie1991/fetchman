#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from UserDict import DictMixin
import Queue
import heapq
import threading
import time
import redis
import urlparse
log = logging.getLogger("scheduler")

from fetchman.scheduler.rate_limiter import TokenBucket
from fetchman import settings
from fetchman.utils.urls import parse_dburl

class RedisTaskQueue(object):
    def __init__(self, rate=0, burst=0):
        self._bucket = TokenBucket(rate=rate, burst=burst)
        options = parse_dburl(settings['scheduler']['task_queue'])
        self._name = options['db']
        host = options['host']
        port = options['port']
        # self._redis = redis.StrictRedis(host=host, port=port)
        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self._redis = redis.Redis(connection_pool=pool)
        if options.get('init'):
            self.init()

    def init(self):
        # 清除队列之前的数据
        self._redis.delete(self._name)

    def put(self, taskid, priority=0, exetime=0):
        self._redis.zadd(self._name, taskid, priority)

    def get(self):
        if not self._bucket.grant():
            return None

        taskid = self._redis.zrange(self._name, 0, 0)
        if taskid:
            taskid = taskid[0]

        if taskid:
            self._redis.zrem(self._name, taskid)

        return taskid

    def done(self, taskid):
        pass

    def __len__(self):
        return self._redis.zcard(self._name)

    def __contains__(self, taskid):
        if not self._redis.zrank(self._name, taskid):
            return False

        return True

    def fail(self):
        # 淘汰优先级的数据
        taskid = self._redis.zrevrange(self._name, 0, 0)
        if taskid:
            taskid = taskid[0]

        if taskid:
            self._redis.zrem(self._name, taskid)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

class ProxyPool(object):
    def __init__(self, name='newtask', host='localhost', port=6379, db=0, maxsize=0, lazy_limit=True):
        """
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is
                    used for better performance.
        """
        self.name = name
        # self.redis = redis.StrictRedis(host=host, port=port, db=db)
        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self._redis = redis.Redis(connection_pool=pool)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def init(self):
        # 清除队列之前的数据
        self._redis.delete(self.name)

    def get(self):
        value = self._redis.srandmember(name=self.name)
        if value is None:
            return ''
        return value

    def put(self, value):
        self._redis.sadd(self.name, value)

    def delete(self, value):
        self._redis.srem(self.name, value)


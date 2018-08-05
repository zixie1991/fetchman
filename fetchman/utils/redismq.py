#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import redis
import umsgpack
from six.moves import queue


class RedisQueue(object):
    """
    A Queue like message built over redis
    """
    Empty = queue.Empty
    Full = queue.Full
    max_timeout = 0.3

    def __init__(self, name='newtask', host='localhost', port=6379, db=0, maxsize=0, lazy_limit=True):
        """
        Constructor for RedisQueue
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is
                    used for better performance.
        """
        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.redis = redis.Redis(connection_pool=pool)
        # self.redis = redis.StrictRedis(host=host, port=port, db=db)
        self.name = name
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def init(self):
        # 清除队列之前的数据
        self.redis.delete(self.name)

    def qsize(self):
        self.last_qsize = self.redis.llen(self.name)
        return self.last_qsize

    def empty(self):
        if self.qsize() == 0:
            return True
        else:
            return False

    def full(self):
        if self.maxsize and self.qsize() >= self.maxsize:
            return True
        else:
            return False

    def put_nowait(self, obj):
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.rpush(self.name, umsgpack.packb(obj))
        return True

    def put(self, obj, block=True, timeout=None):
        if not block:
            return self.put_nowait(obj)

        start_time = time.time()
        while True:
            try:
                return self.put_nowait(obj)
            except self.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    def get_nowait(self):
        ret = self.redis.lpop(self.name)
        if ret is None:
            raise self.Empty
        return umsgpack.unpackb(ret)

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()

        start_time = time.time()
        while True:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

Queue = RedisQueue

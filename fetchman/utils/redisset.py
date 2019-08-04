#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

class RedisSet(object):
    def __init__(self, name='newtask', host='localhost', port=6379, db=0, maxsize=0, lazy_limit=True):
        """
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is
                    used for better performance.
        """
        self.name = name
        self.hash_name = '%s_hash' % self.name
        self.list_name = '%s_list' % self.name
        # self.redis = redis.StrictRedis(host=host, port=port, db=db)
        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self._redis = redis.Redis(connection_pool=pool)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def init(self):
        # 清除队列之前的数据
        self._redis.delete(self.hash_name)
        self._redis.delete(self.list_name)

    def get(self):
        return self.get_by_name(self.name)

    def put(self, value):
        self.put_by_name(self.name, value)

    def delete(self, value):
        self.delete_by_name(self.name, value)

    def get_by_name(self, name):
        hash_name = '%s_hash' % name
        list_name = '%s_list' % name
        value = self._redis.lpop(list_name)
        if value is None:
            return ''

        if self._redis.hexists(hash_name, value):
            self._redis.rpush(list_name, value)
            return value

        return ''

    def put_by_name(self, name, value):
        hash_name = '%s_hash' % name
        list_name = '%s_list' % name
        self._redis.hset(hash_name, value, 0)
        self._redis.rpush(list_name, value)

    def delete_by_name(self, name, value):
        hash_name = '%s_hash' % name
        list_name = '%s_list' % name
        self._redis.hdel(hash_name, value)

    def __contains__(self, value):
        if not self._redis.hexists(self.hash_name, value):
            return False

        return True

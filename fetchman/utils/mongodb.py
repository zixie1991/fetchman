# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import functools
import logging
import time

from pymongo.connection import MongoClient
import pymongo
from urls import parse_dburl

MAX_AUTO_RECONNECT_ATTEMPTS = 5

def safe_mongocall(call):
  def _safe_mongocall(*args, **kwargs):
    for i in range(5):
      try:
        return call(*args, **kwargs)
      except pymongo.errors.AutoReconnect:
        time.sleep(pow(2, i))
    print('Error: Failed operation!')
  return _safe_mongocall

class MongoDBClient(object):
    """save the data to mongodb.
    """
    def __init__(self, host='localhost', port=27017, db='taskdb', user='', password=None, coll='task', pool=100):
        """The only async framework that PyMongo fully supports is Gevent.
        Currently there is no great way to use PyMongo in conjunction with
        Tornado or Twisted. PyMongo provides built-in connection pooling, so
        some of the benefits of those frameworks can be achieved just by
        writing multi-threaded code that shares a MongoClient.
        """
        try:
            client = MongoClient(host, port, max_pool_size=pool)
            if user:
                client.the_database.authenticate(user, password, source=db)
            self.db = client[db]
            self.coll = self.db[coll]
        except Exception as e:
            print('connect to mongodb error.', e)

    @safe_mongocall
    def get(self, query={}):
        if type(query) is not dict:
            return None

        return self.coll.find_one(query)

    @safe_mongocall
    def count_all(self, query={}):
        if type(query) is not dict:
            return None

        return self.coll.find(query).count()

    @safe_mongocall
    def find_all(self, query={}, sort=None):
        if type(query) is not dict:
            return None

        if sort:
            return self.coll.find(query).sort(sort)

        return self.coll.find(query)

    @safe_mongocall
    def find(self, query={}, sort=None, offset=0, limit=20):
        if type(query) is not dict:
            return None

        if sort:
            return self.coll.find(query).sort(sort).skip(offset).limit(limit)

        return self.coll.find(query).skip(offset).limit(limit)

    @safe_mongocall
    def find_data(self, query={}, data={}):
        if type(query) is not dict or type(data) is not dict:
            return None

        return self.coll.find(query, data)

    @safe_mongocall
    def insert(self, data):
        if type(data) is not dict:
            return

        result = self.coll.insert(data)
        return result

    @safe_mongocall
    def remove(self, data={}):
        if type(data) is not dict:
            return

        result = self.coll.remove(data)
        return result

    @safe_mongocall
    def clear(self):
        # 清空一个集合中的所有数据
        self.coll.remove({})

    @safe_mongocall
    def update_inc(self, data, incdata):
        if type(data) is not dict or type(incdata) is not dict:
            return

        self.coll.update(data, {'$inc': incdata})

    @safe_mongocall
    def update_set(self, data, setdata):
        if type(data) is not dict or type(setdata) is not dict:
            return

        self.coll.update(data, {'$set': setdata}, upsert=True)

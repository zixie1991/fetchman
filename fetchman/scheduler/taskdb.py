#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from urlparse import urlparse
import time
import logging
log = logging.getLogger("scheduler")

from fetchman.utils.mongodb import MongoDBClient
from fetchman.utils.urls import parse_dburl
from fetchman import settings

# task schema
{'task':
    {'id': str,
     'url': str,
     'status': int,
     'schedule':
        {'priority': int,  # 优先级
         'retries': int,  # 重试次数
         'retried': int,
         'exetime': int,  # 执行时间
         'age': int,  # 生命周期
         },
     'fetch':
        {'method': str,
         'headers': dict,
         'data': str,  # HTTP 请求信息 body
         'timeout': int
         },
     'process':
        {'callback': str,
         'save': dict},
     'updatetime': int,
     },
 }


class TaskDB(object):
    ACTIVE = 1
    SUCCESS = 2
    FAILED = 3
    BAD = 4
    BAN = 5 # 被禁

    def __init__(self, url):
        options = parse_dburl(url)
        self._client = MongoDBClient(**options)

        # 刚开始没有为tasks建立索引，导致mongodb CPU一路飙升，成为系统瓶颈
        self._client.coll.ensure_index('id')
        self._client.coll.ensure_index('status')

    def load(self, status=None, count=-1):
        offset = 0
        limit = 1000

        if count < 0:
            if status is None:
                count = self._client.count_all()
            else:
                count = self._client.count_all({'status': status})
        log.info('load count=%s' % (count, ))

        while 1:
            if offset > count:
                break

            log.info('load offset=%s, limit=%s' % (offset, limit))
            if status is None:
                tasks = self._client.find(offset=offset, limit=limit)
            else:
                tasks = self._client.find({'status': status}, offset=offset,
                                          limit=limit)

            log.info('load done offset=%s, limit=%s' % (offset, limit))
            for task in tasks:
                yield self._parse(task)

            if not tasks:
                break

            offset += limit

    def get(self, taskid):
        try:
            task = self._client.get({'id': taskid})
            if task:
                return self._parse(task)
        except KeyError:
            pass

        return None

    def insert(self, task):
        self._client.update_set({'id': task.get('id')}, self._stringify(task))

    def update(self, task):
        try:
            self._client.update_set({'id': task.get('id')},
                    self._stringify(task))
        except Exception as e:
            print('update task {id: ' + task.get('id') + '}', e)

    def size(self, status=None):
        if status is None:
            return self._client.count_all()

        return self._client.count_all({'status': status})

    def clear(self):
        """Clear data
        """
        self._client.clear()

    def _parse(self, data):
        if '_id' in data:
            del data['_id']
        '''
        for each in ('schedule', 'fetch', 'process', 'track'):
            if each in data:
                if data[each]:
                    if isinstance(data[each], bytearray):
                        data[each] = str(data[each])
                    data[each] = json.loads(data[each], 'utf8')
                else:
                    data[each] = {}
        '''
        return data

    def _stringify(self, data):
        '''
        for each in ('schedule', 'fetch', 'process', 'track'):
            if each in data:
                data[each] = json.dumps(data[each])
        '''
        return data

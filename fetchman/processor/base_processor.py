#!/usr/bin/env python
# -*- coding: utf-8 -*-
from six.moves import queue

import logging
import time

logger = logging.getLogger('processor')

from fetchman.utils.response import rebuild_response

class BaseProcessor(object):

    def __init__(self, in_queue=None, donetask_queue=None, newtask_queue=None, out_queue=None, handler=None):
        self._in_queue = in_queue
        self._donetask_queue = donetask_queue
        self._newtask_queue = newtask_queue
        self._out_queue = out_queue
        self._handler = handler
        self._stop = True

    def set_in_queue(self, in_queue):
        self._in_queue = in_queue

    def set_donetask_queue(self, donetask_queue):
        self._donetask_queue = donetask_queue

    def set_newtask_queue(self, newtask_queue):
        self._newtask_queue = newtask_queue

    def set_out_queue(self, out_queue):
        self._out_queue = out_queue

    def run(self):
        self._stop = False
        logger.info('start processor')

        while not self._stop:
            try:
                task, result = self._in_queue.get(timeout=1)
                self.on_result(task, result)
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                logger.error('processor error', exc_info=True)
                continue

        logger.info('processor done')

    def on_result(self, task, result):
        response = rebuild_response(result)
        now = time.time()
        try:
            processed_result = self._handler.run(task, response)
            if processed_result.result:
                self._out_queue.put((task, processed_result.result))
        except Exception:
            logger.error('handler run error, taskid=%(id)s, url=%(url)s', task,
                    exc_info=True)
            return
        processed_time = time.time() - now # 处理时间

        if processed_result.follows:
            for each in (processed_result.follows[x:x + 1000] for x in range(0, len(processed_result.follows), 1000)):
                logger.debug('processor put new task [id=%(id)s, url=%(url)s]', task)
                self._newtask_queue.put([newtask for newtask in each])

        track_headers = {}

        if 200 <= response.status_code < 300:
            for name in ('Etag', 'Last-Modified', 'etag', 'last-modified'):
                if name not in response.headers:
                    continue
                track_headers[name.lower()] = response.headers[name]
        else:
            if task.get('track'):
                track_headers = task.get('track', {}).get('fetch', {}).get('headers') or {}

        done_task = {
                'id': task['id'],
                'url': task['url'],
                'track': {
                    'fetch': {'ok': response.isok(),
                        'status_code': response.status_code,
                        'headers': track_headers,
                        'encoding': response.encoding,
                        'time': response.time,
                                    },
                    'process': {'follows': len(processed_result.follows),
                        'time': processed_time,
                                }
                        }
                }

        logger.debug('processor put done task, taskid=%s, url=%s, processed_time=%f',
                task['id'], task['url'], processed_time)
        self._donetask_queue.put(done_task)

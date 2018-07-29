#!/usr/bin/env python
# -*- coding: utf-8 -*-

from six.moves import queue

import gevent
from gevent import monkey
monkey.patch_all() # 对所有io操作打上补丁，固定加这一句

import logging

logger = logging.getLogger('downloader')

class BaseDownloader(object):
    '''下载器
    '''

    def __init__(self, task_queue=None, result_queue=None):
        self._task_queue = task_queue
        self._result_queue = result_queue
        self._stop = True

    def set_task_queue(self, task_queue):
        self._task_queue = task_queue

    def set_result_queue(self, result_queue):
        self._result_queue = result_queue

    def run(self):
        self._stop = False
        logger.info('start downloader')

        while not self._stop:
            if self._result_queue.full():
                continue

            try:
                task = self._task_queue.get_nowait()
                gevent.joinall([gevent.spawn(self.download, task)])
            except KeyboardInterrupt:
                break
            except queue.Empty:
                continue
            except Exception:
                logger.error('downloader error', exc_info=True)
                continue

        logger.info('downloader done')

    def stop(self):
        self._stop = True

    def download(self, task):
        url = task.get('url', 'data:,')

        if url.startswith('data:'):
            fetch_type = 'data'
            result = self.data_fetch(task)
        elif task.get('fetch', {}).get('type') in ('js', ):
            fetch_type = 'js'
            result = self.js_fetch(task)
        else:
            fetch_type = 'http'
            result = self.http_fetch(task)

        self.send_task(task, result)
        self.on_result(task, result)

    def http_fetch(self, task):
        pass

    def data_fetch(self, task):
        pass

    def js_fetch(self, task):
        pass

    def send_task(self, task, result):
        try:
            self._result_queue.put((task, result))
        except Exception:
            pass

    def on_result(self, task, result):
        pass

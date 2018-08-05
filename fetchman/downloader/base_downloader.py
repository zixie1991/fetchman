#!/usr/bin/env python
# -*- coding: utf-8 -*-

from six.moves import queue
import urlparse
import time

import gevent
from gevent import monkey
monkey.patch_all() # 对所有io操作打上补丁，固定加这一句
import requests

import logging

logger = logging.getLogger('downloader')

from fetchman.downloader.selenium_downloader import SeleniumClient
from fetchman.downloader.requests_downloader import RequestsClient
from fetchman.downloader.middlewares import DefaultUserAgent
from fetchman.downloader.proxy_pool import ProxyPool
from fetchman.utils.urls import parse_dburl
from fetchman import settings

def create_obj(class_name, *args, **kwargs):
    import sys
    sys.path.append(settings['settings_module'])
    '''动态创建类的实例
    [Parameter]
    class_name - 类的全名（包括模块名）
    *args - 类构造器所需要的参数(list)
    *kwargs - 类构造器所需要的参数(dict)
    [Return]
    动态创建的类的实例
    [Example]
    class_name = 'knightmade.logging.Logger'
    logger = Activator.createInstance(class_name, 'logname')
    '''
    (module_name, class_name) = class_name.rsplit('.', 1)
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj

class BaseDownloader(object):
    '''下载器
    '''
    default_options = {'method': 'GET',
                       'headers': {},
                       'allow_redirects': True,
                       'use_gzip': True,
                       'timeout': 120}
    allowed_options = ['method', 'headers', 'data', 'timeout',
                       'allow_redirects', 'cookies', 'proxy_host', 'proxy_port']

    def __init__(self, task_queue=None, result_queue=None):
        self._task_queue = task_queue
        self._result_queue = result_queue
        self._stop = True
        self._proxy = None
        self._ua = None
        self._cookies = None
        self._selenium_client = None

    def set_task_queue(self, task_queue):
        self._task_queue = task_queue

    def set_result_queue(self, result_queue):
        self._result_queue = result_queue

    def run(self):
        self._stop = False
        logger.info('start downloader')

        batch_size = settings.get('downloader', {}).get('batch_size', 10)
        tasks = []

        while not self._stop:
            if self._result_queue.full():
                continue

            try:
                task = self._task_queue.get_nowait()
                tasks.append(task)
                if len(tasks) > batch_size:
                    gevent.joinall([gevent.spawn(self.download, task) for task in tasks])
                    tasks = []
            except KeyboardInterrupt:
                break
            except queue.Empty:
                if len(tasks) > 0:
                    gevent.joinall([gevent.spawn(self.download, task) for task in tasks])
                    tasks = []
                else:
                    time.sleep(0.1)

                continue
            except Exception:
                logger.error('downloader error', exc_info=True)
                time.sleep(0.1)
                continue

        logger.info('downloader done')

    def stop(self):
        self._stop = True

    def download(self, task):
        url = task.get('url', 'data:,')

        if url.startswith('data:'):
            fetch_type = 'data'
            result = self.data_fetch(task)
        elif task.get('fetch', {}).get('fetch_type') in ('js', ):
            fetch_type = 'js'
            result = self.js_fetch(task)
        else:
            fetch_type = 'http'
            result = self.http_fetch(task)

        self.send_task(task, result)
        self.on_result(task, result)

    def http_fetch(self, task):
        ua = DefaultUserAgent()
        if settings['downloader']['ua_middleware']:
            ua = create_obj(settings['downloader']['ua_middleware'])
        cookies = None
        if settings['downloader']['cookies_middleware']:
            cookies = create_obj(settings['downloader']['cookies_middleware'])
        proxy = None
        if settings['downloader']['proxy_pool']:
            options = parse_dburl(settings['downloader']['proxy_pool'])
            options['name'] = options['db']
            del options['db']

            proxy = ProxyPool(options)

        client = RequestsClient(ua=ua, proxy=proxy, cookies=cookies)
        result = client.download(task)

        return result

    def data_fetch(self, task):
        url = task.get('url')

        result = {}
        result['status_code'] = 200
        result['original_url'] = url
        result['url'] = url
        result['content'] = ''
        result['time'] = 0
        result['save'] = task.get('fetch', {}).get('save')

        return result

    def js_fetch(self, task):
        if not self._selenium_client:
            self._selenium_client = SeleniumClient()

        result = self._selenium_client.download(task)

        return result

    def send_task(self, task, result):
        try:
            self._result_queue.put((task, result))
        except Exception:
            pass

    def on_result(self, task, result):
        pass

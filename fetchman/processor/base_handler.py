#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import inspect
import time
import heapq
import functools
from six import add_metaclass

logger = logging.getLogger('processor')

from fetchman.utils.string import md5string
from fetchman.utils.urls import _build_url
from fetchman.utils.urls import quote_chinese

def every(minutes=0, seconds=0):
    """装饰器
    @every(minutes=0, seconds=0)
    """
    def wrapper(func):
        @functools.wraps(func)
        def cronjob(self, *args, **kwargs):
            print('wrapper %s()' % func.__name__)
            # 偏函数
            new_func = functools.partial(func, self, *args, **kwargs)
            now = time.time()
            interval = minutes * 60 + seconds
            tick = now  # 当前时间为起点
            func.is_cronjob = True
            heapq.heappush(self._funcs, (tick, interval, new_func))
            # 只对函数做预处理，不会执行该函数
            # return func(self, *args, **kwargs)
        return cronjob
    return wrapper

def config(_config=None, **kwargs):
    """装饰器
    @config
    """
    if _config is None:
        _config = {}
    _config.update(kwargs)

    def wrapper(func):
        func._config = _config
        return func
    return wrapper


class HandleResult(object):
    def __init__(self, result, follows):
        self.result = result
        self.follows = follows


class BaseHandler(object):
    def __init__(self):
        self._follows = []
        self._funcs = []
        self.on_start()

    @every()
    def on_start(self):
        pass

    def run(self, task, result):
        try:
            processed_result = self._run(task, result)
        except:
            logger.error("parse list error, [taskid=%(id)s, url=%(url)s]",
                          task, exc_info=True)
            processed_result = None

        self.on_result(processed_result)

        return HandleResult(processed_result, self._follows)

    def on_result(self, result):
        pass

    def _run(self, task, result):
        self._reset()

        # do not run_func when 304
        if result.status_code == 304:
            result.raise_for_status()
        callback = task.get('process', {}).get('callback', '__call__')
        if not hasattr(self, callback):
            logger.error("handler run callback [id=%(id)s, url=%(url)s, process=%(process)s] error", task,
                      exc_info=True)
            raise NotImplementedError("self.%s() not implemented!" % callback)

        func = getattr(self, callback)

        args, varargs, keywords, defaults = inspect.getargspec(func)
        if len(args) == 1:  # foo(self)
            return func()
        elif len(args) == 2:  # foo(self, response)
            return func(result)
        elif len(args) == 3:  # foo(self, task, response)
            return func(task, result)
        else:
            raise TypeError("self.%s() need at least 1 argument and lesser 3 "
                            "arguments: %s(self, [task], [response])"
                            % (func.__name__, func.__name__))

    def _reset(self):
        self._follows = []

    def on_cronjob(self, task, response):
        tick = response.save.get('tick', 0)
        if not tick:
            return

        logger.debug('processor on cronjob tick=%f, cron jobs=%d', tick, len(self._funcs))

        while len(self._funcs) > 0 and tick >= self._funcs[0][0]:
            _, interval, func = heapq.heappop(self._funcs)
            func()
            now = time.time()
            logger.debug('processor run cron job at %f' % now)
            if interval > 0:
                heapq.heappush(self._funcs, (now + interval, interval, func))


    def crawl(self, url, **kwargs):
        # init task
        task = {}

        # call callback
        if kwargs.get('callback'):
            callback = kwargs['callback']
            if isinstance(callback, basestring) and hasattr(self, callback):
                func = getattr(self, callback)
            elif hasattr(callback, 'im_self') and callback.im_self is self:
                func = callback
                kwargs['callback'] = func.__name__
            else:
                raise NotImplementedError("self.%s() not implemented!" %
                                          callback)
            if hasattr(func, '_config'):
                for k, v in func._config.iteritems():
                    kwargs.setdefault(k, v)

        # rewrite URL
        url = quote_chinese(_build_url(url.strip(), kwargs.get('params')))
        task['url'] = url

        # taskid
        task['id'] = md5string(url)

        # schedule
        schedule = {}
        for key in ('priority', 'retries', 'exetime', 'age', 'force_update'):
            if key in kwargs and kwargs[key]:
                schedule[key] = kwargs[key]
        if schedule:
            task['schedule'] = schedule

        # fetch
        fetch = {}
        for key in ('method', 'headers', 'data', 'timeout', 'allow_redirects',
                    'cookies', 'proxy_host', 'proxy_port', 'last_modifed', 'save', 'etag',
                    'last_modified', 'download_delay', 'fetch_type'):
            if key in kwargs and kwargs[key]:
                fetch[key] = kwargs[key]
        if fetch:
            task['fetch'] = fetch

        # process
        process = {}
        for key in ('callback',):
            if key in kwargs and kwargs[key]:
                process[key] = kwargs[key]
        if process:
            task['process'] = process

        self._follows.append(task)

        return task

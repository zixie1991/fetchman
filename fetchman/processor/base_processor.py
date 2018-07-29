#!/usr/bin/env python
# -*- coding: utf-8 -*-
from six.moves import queue

import logging

logger = logging.getLogger('processor')

class BaseProcessor(object):

    def __init__(self, in_queue=None, donetask_queue=None, newtask_queue=None, out_queue=None):
        self._in_queue = in_queue
        self._donetask_queue = donetask_queue
        self._newtask_queue = newtask_queue
        self._out_queue = out_queue
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
                task, result = self._in_queue.get(timeout=0.1)
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
        pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from six.moves import queue
import time
import logging

logger = logging.getLogger('scheduler')

class BaseScheduler(object):
    LOOP_LIMIT = 1000
    LOOP_INTERVAL = 0.1 # 单位:s

    def __init__(self, taskdb=None, donetask_queue=None, newtask_queue=None, out_queue=None):
        self._taskdb = taskdb
        self._donetask_queue = donetask_queue
        self._newtask_queue = newtask_queue
        self._out_queue = out_queue
        self._stop = True

    def set_taskdb(self, taskdb):
        self._taskdb = taskdb

    def set_donetask_queue(self, donetask_queue):
        self._donetask_queue = donetask_queue

    def set_newtask_queue(self, newtask_queue):
        self._newtask_queue = newtask_queue

    def set_out_queue(self, out_queue):
        self._out_queue = out_queue

    def run(self):
        self._stop = False
        logger.info('start scheduler')

        while not self._stop:
            try:
                self.run_once()
                time.sleep(self.LOOP_INTERVAL)
            except KeyboardInterrupt:
                break
            except Exception:
                continue

        logger.info('scheduler done')

    def run_once(self):
        self.check_task_done()
        self.check_task_new()
        self.check_task_select()
        self.check_task_cron()

    def check_task_done(self):
        pass

    def check_task_new(self):
        pass

    def check_task_select(self):
        pass

    def check_task_cron(self):
        pass

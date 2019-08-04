#!/usr/bin/env python
# -*- coding: utf-8 -*-

from six.moves import queue

import logging

logger = logging.getLogger('processor')

class BasePipeline(object):
    def __init__(self, in_queue=None):
        self._in_queue = in_queue
        self._stop = True

    def set_in_queue(self, in_queue):
        self._in_queue = in_queue

    def run(self):
        self._stop = False
        logger.info('start pipeline')

        while not self._stop:
            try:
                task, result = self._in_queue.get(timeout=1)
                self.on_result(task, result)
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                logger.error('pipeline run error, taskid=%(id)s, url=%(url)s',
                        task, exc_info=True)
                continue

        logger.info('pipeline done')

    def on_result(self, task, result):
        pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import time
import logging.config
import os

from fetchman import init_logger
from fetchman import load_config
from fetchman.utils.thread import run_in_subprocess
from fetchman.utils import redismq
from fetchman.scheduler.taskdb import TaskDB
from fetchman import settings
from fetchman.utils import create_taskdb
from fetchman.utils import create_message_queue

class BaseSpider(object):

    def __init__(self, conf_path='./settings.conf'):
        init_logger()
        load_config(conf_path)

        self._taskdb = create_taskdb(settings['scheduler']['taskdb'])
        self._donetask_queue = create_message_queue(settings['scheduler']['donetask_queue'])
        self._newtask_queue = create_message_queue(settings['scheduler']['newtask_queue'])
        self._scheduler_to_downloader = create_message_queue(settings['downloader']['message_queue'])
        self._downloader_to_processor = create_message_queue(settings['processor']['message_queue'])
        self._processor_to_pipeline = create_message_queue(settings['pipeline']['message_queue'])

        self._scheduler = None
        self._downloader = None
        self._processor = None
        self._pipeline = None

        self._threads = []
        self._stop = True

    def run(self):

        # 信号处理函数
        def sig_handler(sig, action):
            self.stop()
            sys.exit(0)

        # sigkill无法捕捉
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)

        if self._scheduler:
            self._scheduler.set_taskdb(self._taskdb)
            self._scheduler.set_donetask_queue(self._donetask_queue)
            self._scheduler.set_newtask_queue(self._newtask_queue)
            self._scheduler.set_out_queue(self._scheduler_to_downloader)

            def run_scheduler():
                self._scheduler.run()
            self._threads.append(run_in_subprocess(run_scheduler))

        if self._downloader:
            self._downloader.set_task_queue(self._scheduler_to_downloader)
            self._downloader.set_result_queue(self._downloader_to_processor)

            def run_downloader():
                self._downloader.run()
            self._threads.append(run_in_subprocess(run_downloader))

        if self._processor:
            self._processor.set_in_queue(self._downloader_to_processor)
            self._processor.set_donetask_queue(self._donetask_queue)
            self._processor.set_newtask_queue(self._newtask_queue)
            self._processor.set_out_queue(self._processor_to_pipeline)

            def run_processor():
                self._processor.run()
            self._threads.append(run_in_subprocess(run_processor))

        if self._pipeline:
            self._pipeline.set_in_queue(self._processor_to_pipeline)

            def run_pipeline():
                self._pipeline.run()
            self._threads.append(run_in_subprocess(run_pipeline))

        self._stop = False
        while not self._stop:
            try:
                for thread in self._threads:
                    if not thread.is_alive():
                        break
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break

    def stop(self):
        self._stop = True

    def set_scheduler(self, scheduler):
        self._scheduler = scheduler
        return self

    def set_downloader(self, downloader):
        self._downloader = downloader
        return self

    def set_processor(self, processor):
        self._processor = processor
        return self

    def set_pipeline(self, pipeline):
        self._pipeline = pipeline
        return self

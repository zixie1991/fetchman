#!/usr/bin/env python
# -*- coding: utf-8 -*-

from six.moves import queue
import time
import logging
from collections import deque

logger = logging.getLogger('scheduler')

from fetchman.scheduler import task_queue
from fetchman import settings

class BaseScheduler(object):
    LOOP_LIMIT = 1000
    LOOP_INTERVAL = 0.1 # 单位:s
    default_schedule = {'priority': 1,
                        'retires': 3,
                        'exetime': 0,
                        'age': 24 * 60 * 60,  # 每天
                        }

    def __init__(self, taskdb=None, donetask_queue=None, newtask_queue=None, out_queue=None):
        self._taskdb = taskdb
        self._donetask_queue = donetask_queue
        self._newtask_queue = newtask_queue
        self._out_queue = out_queue
        self._task_queue = task_queue.RedisTaskQueue(settings['scheduler']['rate'], settings['scheduler']['burst'])
        self._send_queue = deque()
        self._stop = True
        self._last_tick = 0
        self._last_taskdb_tick = 0

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

        # for task in self._taskdb.load(status=self._taskdb.ACTIVE):
            # schedule = task.get('schedule', self.default_schedule)
            # self._task_queue.put(task['id'], priority=schedule.get('priority', 0),
                                # exetime=schedule.get('exetime', 0))

        while not self._stop:
            try:
                self.run_once()
                time.sleep(self.LOOP_INTERVAL)
            except KeyboardInterrupt:
                break
            except Exception:
                logger.error('run error', exc_info=True)
                continue

        logger.info('scheduler done')

    def run_once(self):
        self.check_task_done()
        self.check_task_new()
        self.check_task_select()
        self.check_task_cron()

    def check_task_done(self):
        """检查已完成的任务
        """
        count = 0
        try:
            while 1:
                task = self._donetask_queue.get_nowait()
                logger.debug('scheduler get done task [id=%(id)s, url=%(url)s]'
                            % task)
                self.on_task_done(task)
                count += 1
        except queue.Empty:
            pass

        return count

    def on_task_done(self, task):
        """更新完成任务状态
        """
        status_code = task.get('track').get('fetch').get('status_code')
        if status_code >= 200 and status_code < 400:
            task['status'] = self._taskdb.SUCCESS
        elif status_code == 403:
            task['status'] = self._taskdb.BAN
        elif status_code >= 400 and status_code < 500:
            task['status'] = self._taskdb.BAD
        else:
            task['status'] = self._taskdb.FAILED

        task['updatetime'] = time.time()
        self._taskdb.update(task)

        logger.debug('scheduler has task done [id=%(id)s, url=%(url)s]' % task)
        return task

    def check_task_new(self):
        """检查新生成的任务
        """
        count = 0
        try:
            while count < self.LOOP_LIMIT:
                task = self._newtask_queue.get_nowait()
                if isinstance(task, list):
                    tasks = task
                else:
                    tasks = (task, )

                for task in tasks:
                    logger.debug('scheduler get new task [id=%(id)s, url=%(url)s]' %
                            task)

                    if task['id'] in self._task_queue:
                        if not task.get('schedule', {}).get('force_update', False):
                            continue

                    old_task = self._taskdb.get(task['id'])
                    if old_task:
                        self.on_task_old(old_task, task)
                    else:
                        self.on_task_new(task)
                    count += 1
        except queue.Empty:
            pass

        return count

    def on_task_old(self, old_task, new_task):
        now = time.time()
        new_schedule = new_task.get('schedule', self.default_schedule)
        restart = False

        try:
            new_schedule_age = new_schedule.get('age', self.default_schedule.get('age'))
            logger.debug('scheduler old task [id={}, updatetime={}, age={}, now={}]'.format(old_task['id'], old_task.get('updatetime', 0), new_schedule_age, now))
            if (new_schedule_age > 0 and (new_schedule_age + old_task.get('updatetime', 0)) < now):
                restart = True
            elif new_schedule.get('force_update', False):
                new_task['updatetime'] = now - new_schedule_age
                restart = True
            elif old_task['status'] == self._taskdb.FAILED or old_task['status'] == self._taskdb.BAN:
                # fix next restart would be ignored bug
                new_task['updatetime'] = now - new_schedule_age
                restart = True
        except KeyError:
            pass

        if not restart:
            logger.debug('scheduler ignore task [id=%(id)s, url=%(url)s' %
                      new_task)
            return

        new_task['status'] = self._taskdb.ACTIVE
        self.update_task(new_task)

        logger.debug('scheduler restart task [id=%(id)s, url=%(url)s]' % new_task)

        return new_task

    def on_task_new(self, task):
        task['status'] = self._taskdb.ACTIVE
        self.update_task(task)

        logger.debug('scheduler new task [id=%(id)s, url=%(url)s]' % task)

        return task

    def update_task(self, task):
        schedule = task.get('schedule', self.default_schedule)
        self._task_queue.put(task['id'], priority=schedule.get('priority', 0),
                             exetime=schedule.get('exetime', 0))
        self._taskdb.update(task)

    def check_task_select(self):
        """检查筛选的任务
        """
        count = 0
        while self._send_queue:
            task = self._send_queue.pop()
            try:
                self.send_task(task, force=False)
            except queue.Full:
                self._send_queue.append(task)
                break

        try:
            while 1:
                taskid = self._task_queue.get()
                if not taskid:
                    break

                task = self._taskdb.get(taskid)
                if not task:
                    continue

                # fix multi crawler compete one same task
                if task['status'] == self._taskdb.ACTIVE:
                    self.on_task_select(task)
                count += 1

                if count > self.LOOP_LIMIT:
                    break
        except queue.Empty:
            pass

        now = time.time()
        if count == 0 and now - self._last_taskdb_tick > 300:
            self._last_taskdb_tick = now
            for task in self._taskdb.load(status=self._taskdb.FAILED, count=self.LOOP_LIMIT - count):
                self.on_task_select(task)
                count += 1

            for task in self._taskdb.load(status=self._taskdb.BAN, count=self.LOOP_LIMIT - count):
                self.on_task_select(task)
                count += 1

        return count

    def on_task_select(self, task):
        self.send_task(task)

        logger.debug("scheduler select task [id=%(id)s, url=%(url)s]" % task)

    def send_task(self, task, force=True):
        """把任务插入到out_queue
        添加缓存队列_send_queue
        """
        logger.debug("scheduler put task [id=%(id)s, url=%(url)s]" % task)
        try:
            self._out_queue.put(task, timeout=1)
        except queue.Full:
            self._task_queue.fail() # 限流
            if force:
                self._send_queue.appendleft(task)
            else:
                raise

    def check_task_cron(self):
        """检查定时任务
        """
        now = time.time()
        if now - self._last_tick < 1:
            return False

        self._last_tick = now

        task = {
            "id": "data:,on_cronjob",
            "url": "data:,on_cronjob",
            "status": self._taskdb.ACTIVE,
            "process": {
                "callback": "on_cronjob",
                },
            "fetch": {
                "save": {
                    "tick": self._last_tick,
                    },
                },
            }

        self.on_task_select(task)

        logger.debug('scheduler cron task [id=%(id)s, url=%(url)s]' % task)

        return True

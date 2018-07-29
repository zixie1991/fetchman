#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
import Queue

import unittest2 as unittest
from fetchman.downloader.base_downloader import BaseDownloader

class TestBaseDownaloder(unittest.TestCase):
    def test_run(self):
        task_queue = Queue.Queue()
        result_queue = Queue.Queue()
        task_queue.put({'url': 'data:,'})
        task_queue.put({'url': 'http://movie.douban.com', 'fetch_type': 'http'})
        downloader = BaseDownloader(task_queue, result_queue)
        downloader.run()

if __name__ == '__main__':
    unittest.main()

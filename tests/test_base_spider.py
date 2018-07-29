#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

import unittest2 as unittest
from fetchman.spider.base_spider import BaseSpider
from fetchman.scheduler.base_scheduler import BaseScheduler
from fetchman.downloader.base_downloader import BaseDownloader
from fetchman.processor.base_processor import BaseProcessor
from fetchman.pipeline.base_pipeline import BasePipeline

class TestBaseSpider(unittest.TestCase):
    def test_run(self):
        BaseSpider().set_scheduler(BaseScheduler()).set_downloader(BaseDownloader()).set_processor(BaseProcessor()).set_pipeline(BasePipeline()).run()

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
sys.path.append('../')

import unittest2 as unittest
from fetchman.spider.base_spider import BaseSpider
from fetchman.scheduler.base_scheduler import BaseScheduler
from fetchman.downloader.base_downloader import BaseDownloader
from fetchman.processor.base_processor import BaseProcessor
from fetchman.pipeline.base_pipeline import BasePipeline
from fetchman.pipeline.console_pipeline import ConsolePipeline
from fetchman.processor.base_handler import BaseHandler
from fetchman.processor.base_handler import every
from fetchman.processor.base_handler import config

class TestHandler(BaseHandler):
    @every(seconds=60)
    def on_start(self):
        self.crawl('https://www.youku.com', priority=4, callback=self.detail_page, force_update=True, fetch_type='http')

    @config(priority=3)
    def detail_page(self, task, result):
        re_url = re.compile(r'https://v.youku.com/')
        for url in result.urls():
            if not re_url.match(url):
                continue

            self.crawl(url, callback=self.detail_page)

        return {'url': task['url']}

class TestBaseSpider(unittest.TestCase):
    def test_run(self):
        # BaseSpider().set_scheduler(BaseScheduler()).set_downloader(BaseDownloader()).set_processor(BaseProcessor(handler=TestHandler())).set_pipeline(BasePipeline()).run()
        BaseSpider().set_scheduler(BaseScheduler()).set_downloader(BaseDownloader()).set_processor(BaseProcessor(handler=TestHandler())).set_pipeline(ConsolePipeline()).run()
        # BaseSpider().set_scheduler(BaseScheduler()).run()

if __name__ == '__main__':
    unittest.main()

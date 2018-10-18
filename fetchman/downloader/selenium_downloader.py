#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging

logger = logging.getLogger('downloader')

from selenium import webdriver
from pyvirtualdisplay import Display

class SeleniumClient(object):
    def __init__(self):
        self._display = Display(visible=0, size=(800, 600))
        self._display.start()

        chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.managed_default_content_settings.images':2,
                'browser.cache.memory.enable': False,
                'browser.cache.disk.enable': False,
                'network.http.use-cache': False,
                }
        chrome_options.add_experimental_option("prefs", prefs)

        self._driver = webdriver.Chrome(chrome_options=chrome_options)

    def download(self, task):
        url = task['url']
        result = {}
        now = time.time()
        try:
            download_delay = task.get('fetch', {}).get('download_delay', 60)
            self._driver.implicitly_wait(download_delay) # 等待js执行
            self._driver.get(url)
            # self._driver.execute_script('window.localStorage.clear();')
            result['status_code'] = 200
            result['content'] = self._driver.page_source
        except:
            logger.error('selenium error, taskid=%(id)s, url=%(url)s', task,
                    exc_info=True)
            result['status_code'] = 599
            result['content'] = ''

        processed_time = time.time() - now

        result['url'] = url
        result['original_url'] = url
        result['time'] = processed_time
        result['save'] = task.get('fetch', {}).get('save')

        logger.info("[%d] %s %.2fs" %
                    (result['status_code'], url, result['time']))

        return result


    def __del__(self):
        if self._driver:
            self._driver.close()
            self._driver.stop()

        if self._display:
            self._display.stop()


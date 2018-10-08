#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse
import time
import logging

logger = logging.getLogger('downloader')

import requests

class RequestsClient(object):
    default_options = {'method': 'GET',
                       'headers': {},
                       'allow_redirects': True,
                       'use_gzip': True,
                       'timeout': 60}
    allowed_options = ['method', 'headers', 'data', 'timeout',
                       'allow_redirects', 'cookies', 'proxy_host', 'proxy_port']

    def __init__(self, ua=None, proxy=None, cookies=None):
        self._ua = ua
        self._proxy = proxy
        self._cookies = cookies

    def download(self, task):
        def make_request():
            '''获取HTTPHeaders
            '''
            options = dict(self.default_options)

            options.setdefault('url', url)

            for key in self.allowed_options:
                if key in task_fetch:
                    options[key] = task_fetch[key]

            # proxy
            if self._proxy:
                proxy_string = self._proxy.get()
                if proxy_string:
                    if '://' not in proxy_string:
                        proxy_string = 'http://' + proxy_string
                    proxy_splited = urlparse.urlsplit(proxy_string)
                    options['proxy_host'] = proxy_splited.hostname.encode('utf8')
                    options['proxy_port'] = proxy_splited.port or 8080

                    task_fetch['proxy_host'] = options['proxy_host']
                    task_fetch['proxy_port'] = options['proxy_port']
                    logger.info('fetcher proxy_host=%(proxy_host)s, proxy_port=%(proxy_port)s', options)

            if not options.get('headers', {}).get('User-Agent') and self._ua:
                options['headers']['User-Agent'] = self._ua.get()

            options['allow_redirects'] = False

            # fix requests
            if options.get('proxy_host'):
                proxy_string = 'http://' + options['proxy_host'] + ':' + str(options['proxy_port'])
                options['proxies'] = {'http': proxy_string, 'https': proxy_string}
                del options['proxy_host']
                del options['proxy_port']

            if options.get('use_gzip'):
                if options['use_gzip']:
                    options['headers']['Accept-Encoding'] = 'identity, deflate, compress, gzip'

                del options['use_gzip']

            if not options.get('cookies') and self._cookies:
                options['cookies'] = self._cookies.get()
                options['headers']['Cookie'] = ';'.join([k+'='+v for k, v in options['cookies'].iteritems()])

            # SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:581)
            options['verify'] = False

            return options

        def handle_response(response, **kwargs):
            """Response回调函数
            注意：handle_response并不是在client抓取完网页之后，才调用的；而是在一次网络I/O通信完成后调用的
            """
            result = {}
            result['status_code'] = response.status_code
            result['original_url'] = url
            result['url'] = response.url or url
            result['headers'] = dict(response.headers)
            result['content'] = response.content or ''
            result['time'] = time.time() - start_time
            result['cookies'] = response.cookies.get_dict()
            result['save'] = task_fetch.get('save')

            # retry fetch
            if response.status_code == 599:
                logger.info("[%d] %s %.2fs" %
                         (response.status_code, url, result['time']))
            else:
                logger.warning("[%d] %s %.2fs" %
                            (response.status_code, url, result['time']))

            return result

        start_time = time.time()
        url = task.get('url')
        if not task.get('fetch'):
            task['fetch'] = {}

        task_fetch = task.get('fetch', {})
        options = make_request()
        # options['hooks'] = dict(response=handle_response)

        try:
            response = requests.request(**options)
            result = handle_response(response)
        except Exception as e:
            response = requests.Response()
            response.status_code = 599
            response.headers = {}
            response._content = ''
            result = handle_response(response)
            logger.warning("[%d] %s %s" % (response.status_code, url, str(e)))

        return result

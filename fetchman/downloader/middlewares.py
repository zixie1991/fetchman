#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import os
import urlparse

from fetchman import settings

class DefaultUserAgent(object):
    '''
    default user-agent
    '''
    def __init__(self, user_agent='fetchman'):
        self._user_agent = user_agent

    def get(self):
        return self._user_agent


class RandomUserAgent(object):
    '''
    @par the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,
        netscape for more user agent strings,you can find it in
        http://www.useragentstring.com/pages/useragentstring.php
    @sa http://www.useragentstring.com/pages/useragentstring.php
    '''
    def __init__(self, user_agent='', useragent_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloader/useragent.list')):
        self.user_agent_list = []
        self._user_agent = user_agent
        if useragent_path:
            with open(useragent_path, 'r') as f:
                while 1:
                    line = f.readline()
                    if not line:
                        break
                    self.user_agent_list.append(line.strip())

    def get(self):
        '''获取User-Agent
        '''
        if self._user_agent:
            return self._user_agent

        ua = random.choice(self.user_agent_list)
        return ua

class RandomMobileUserAgent(RandomUserAgent):
    def __init__(self):
        super(RandomMobileUserAgent, self).__init__(useragent_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloader/useragent-mobile.list'))


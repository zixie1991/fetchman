#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class TokenBucket(object):
    """令牌桶
    rate - 每秒抓取网页的个数
    burst - 并发度控制
    """
    def __init__(self, rate=1, burst=10):
        self.burst = burst
        self.num_tokens = 0
        self.rate = float(rate)
        self.last_update = time.time()

    def grant(self):
        now = time.time()
        self.num_tokens += self.rate * (now - self.last_update)
        self.last_update = now
        if (self.num_tokens > self.burst):
            self.num_tokens = self.burst

        if self.num_tokens < 1:
            return False

        self.num_tokens -= 1
        return True

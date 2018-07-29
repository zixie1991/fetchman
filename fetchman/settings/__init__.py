#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修改自 /usr/local/lib/python2.7/dist-packages/scrapy/settings
"""

import six
import json
from importlib import import_module


class Settings(object):
    def __init__(self, values=None):
        self.attributes = {}
        if values is not None:
            self.setdict(values)

    def __getitem__(self, name):
        value = None
        if name in self.attributes:
            return self.attributes[name]
        return value

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def getbool(self, name, default=False):
        """
        True is: 1, '1', True
        False is: 0, '0', False, None
        """
        return bool(int(self.get(name, default)))

    def getint(self, name, default=0):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))

    def getlist(self, name, default=None):
        value = self.get(name)
        if value is None:
            return default or []
        elif hasattr(value, '__iter__'):
            return value
        else:
            return str(value).split(',')

    def getdict(self, name, default=None):
        value = self.get(name)
        if value is None:
            return default or {}
        if isinstance(value, six.string_types):
            value = json.loads(value)
        if isinstance(value, dict):
            return value
        raise ValueError("Cannot convert value for setting '%s' to dict: '%s'"
                         % (name, value))

    def set(self, name, value):
        self.attributes[name] = value

    def setdict(self, values):
        for name, value in values.iteritems():
            self.set(name, value)

    def setmodule(self, module):
        if isinstance(module, six.string_types):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))


import sys
sys.modules[__name__] = Settings()

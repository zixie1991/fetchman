#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse

def parse_dburl(url):
    parse = urlparse.urlparse(url)
    options = {}
    options['host'] = parse.hostname
    options['port'] = parse.port
    if parse.username:
        options['user'] = parse.username
    if parse.password:
        options['password'] = parse.password
    options['db'] = parse.path.strip('/')
    qs = dict((k, v[0]) for k, v in urlparse.parse_qs(parse.query).items())
    options.update(qs)

    return options

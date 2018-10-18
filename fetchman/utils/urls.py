#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse
import mimetypes
from urllib import urlencode
import base64

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


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def _encode_params(data):
    """Encode parameters in a piece of data.

    Will successfully encode parameters when passed as a dict or a list of
    2-tuples. Order is retained if data is a list of 2-tuples but abritrary
    if parameters are supplied as a dict.
    """

    if isinstance(data, basestring):
        return data
    elif hasattr(data, 'read'):
        return data
    elif hasattr(data, '__iter__'):
        result = []
        for k, vs in data.iteritems():
            for v in isinstance(vs, list) and vs or [vs]:
                if v is not None:
                    result.append(
                        (k.encode('utf-8') if isinstance(k, unicode) else k,
                         v.encode('utf-8') if isinstance(v, unicode) else v))
        return urlencode(result, doseq=True)
    else:
        return data


def _utf8(key):
    if not isinstance(key, basestring):
        key = str(key)
    return key.encode('utf-8') if isinstance(key, unicode) else key


def _encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files Return (content_type, body) ready for httplib.HTTP
    instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for key, value in fields.iteritems():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % _utf8(key))
        L.append('')
        L.append(_utf8(value))
    for key, (filename, value) in files.iteritems():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"'
                 % (_utf8(key), _utf8(filename)))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value.read() if hasattr(value, "read") else _utf8(value))
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def _build_url(url, _params):
    """Build the actual URL to use."""

    # Support for unicode domain names and paths.
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    netloc = netloc.encode('idna').decode('utf-8')
    if not path:
        path = '/'

    if isinstance(scheme, unicode):
        scheme = scheme.encode('utf-8')
    if isinstance(netloc, unicode):
        netloc = netloc.encode('utf-8')
    if isinstance(path, unicode):
        path = path.encode('utf-8')
    if isinstance(params, unicode):
        params = params.encode('utf-8')
    if isinstance(query, unicode):
        query = query.encode('utf-8')
    if isinstance(fragment, unicode):
        fragment = fragment.encode('utf-8')

    enc_params = _encode_params(_params)
    if enc_params:
        if query:
            query = '%s&%s' % (query, enc_params)
        else:
            query = enc_params

    # url = (urlunparse([scheme, netloc, path, params, query, fragment]))
    # 忽略锚(fragment)
    url = (urlparse.urlunparse([scheme, netloc, path, params, query, '']))
    return url


def quote_chinese(url, encodeing="utf-8"):
    if isinstance(url, unicode):
        return quote_chinese(url.encode("utf-8"))
    res = [b if ord(b) < 128 else '%%%02X' % (ord(b)) for b in url]
    return "".join(res)


def xunlei_url_decode(url):
    url = url.split('&')[0]
    url = url[10:].decode('base64')
    assert url.startswith('AA') and url.endswith('ZZ'), \
        'xunlei url format error'
    return url[2:-2]


def flashget_url_decode(url):
    url = url.split('&')[0]
    url = url[11:].decode('base64')
    assert url.startswith('[FLASHGET]') and url.endswith('[FLASHGET]'), \
        'flashget url format error'
    return url[10:-10]


def flashgetx_url_decode(url):
    url = url.split('&')[0]
    name, size, hash, end = url.split('|')[2:]
    assert end == '/', 'flashgetx url format error'
    return 'ed2k://|file|'+name.decode('base64')+'|'+size+'|'+hash+'/'


def qqdl_url_decode(url):
    url = url.split('&')[0]
    return base64.decodestring(url[7:])


def url_unmask(url):
    url_lower = url.lower()
    if url_lower.startswith('thunder://'):
        url = xunlei_url_decode(url)
    elif url_lower.startswith('flashget://'):
        url = flashget_url_decode(url)
    elif url_lower.startswith('flashgetx://'):
        url = flashgetx_url_decode(url)
    elif url_lower.startswith('qqdl://'):
        url = qqdl_url_decode(url)

    return quote_chinese(url)


def get_domain(url):
    return urlparse(url)[1]

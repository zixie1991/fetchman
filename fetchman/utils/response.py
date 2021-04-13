#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import chardet
import six
import lxml.html
import lxml.etree
from urlparse import urljoin
from pyquery import PyQuery
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers
try:
    from requests.utils import get_encodings_from_content
except ImportError:
    get_encodings_from_content = None
from requests import HTTPError

from fetchman.utils.string import pretty_unicode


class Response(object):
    def __init__(self):
        self.status_code = None
        self.url = None
        self.original_url = None
        self.headers = CaseInsensitiveDict()
        self.content = ''
        self.cookies = {}
        self.error = None
        self.save = None
        self.time = 0

    def __repr__(self):
        return '<Response [%d]>' % self.status_code

    def __bool__(self):
        """Returns true if :attr:`status_code` is 'OK'."""
        return self.ok

    def __nonzero__(self):
        """Returns true if :attr:`status_code` is 'OK'."""
        return self.ok

    @property
    def ok(self):
        try:
            self.raise_for_status()
        except HTTPError:
            return False
        return True

    @property
    def encoding(self):
        """
        encoding of Response.content.
        if Response.encoding is None, encoding will be guessed
        by header or content or chardet if available.
        """
        if hasattr(self, '_encoding'):
            return self._encoding

        # content is unicode
        if isinstance(self.content, six.text_type):
            return 'unicode'

        # Try charset from content-type
        encoding = get_encoding_from_headers(self.headers)
        if encoding == 'ISO-8859-1':
            encoding = None

        # Try charset from content
        if not encoding and get_encodings_from_content:
            if six.PY3:
                encoding = get_encodings_from_content(pretty_unicode(
                    self.content[:100]))
            else:
                encoding = get_encodings_from_content(self.content)
            encoding = encoding and encoding[0] or None

        # Fallback to auto-detected encoding.
        if not encoding and chardet is not None:
            encoding = chardet.detect(self.content)['encoding']

        if encoding and encoding.lower() == 'gb2312':
            encoding = 'gb18030'

        self._encoding = encoding or 'utf-8'
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value
        self._text = None

    @property
    def text(self):
        """Content of the response, in unicode.

        if Response.encoding is None and chardet module is available, encoding
        will be guessed.
        """
        if hasattr(self, '_text') and self._text:
            return self._text
        if not self.content:
            return u''
        if isinstance(self.content, unicode):
            return self.content

        content = None
        encoding = self.encoding

        # Decode unicode from given encoding.
        try:
            content = self.content.decode(encoding, 'replace')
        except LookupError:
            # A LookupError is raised if the encoding was not found which could
            # indicate a misspelling or similar mistake.
            #
            # So we try blindly encoding.
            content = self.content.decode('utf-8', 'replace')

        self._text = content
        return content

    @property
    def json(self):
        """Returns the json-encoded content of a request, if any."""
        if hasattr(self, '_json'):
            return self._json
        try:
            self._json = json.loads(self.text or self.content)
        except ValueError:
            self._json = None
        return self._json

    @property
    def xml(self):
        """Returns the xml-encoded content of a request, if any."""
        if hasattr(self, '_xml'):
            return self._xml

        try:
            self._xml = lxml.etree.fromstring(self.content)
        except ValueError:
            self._xml = None
        return self._xml

    @property
    def doc(self):
        """Returns a PyQuery object of the response's content"""
        if hasattr(self, '_doc'):
            return self._doc

        elements = self.html
        doc = self._doc = PyQuery(elements)
        try:
            doc.make_links_absolute(self.url)
        except ValueError:
            # ignore ValueError("Invalid IPv6 URL")
            pass
        return doc

    @property
    def html(self):
        """Returns document_fromstring or fragment_fromstring, based on whether
        the string looks like a full document, or just a fragment.
        """
        if hasattr(self, '_html'):
            return self._html
        try:
            parser = lxml.html.HTMLParser(encoding=self.encoding)
            elements = lxml.html.fromstring(self.text, parser=parser)
        except LookupError:
            # lxml would raise LookupError when encoding not supported
            # try fromstring without encoding instead.
            # on windows, unicode is not availabe as encoding for lxml
            elements = lxml.html.fromstring(self.text)
        except:
            elements = lxml.html.fromstring(self.content)

        _html = self._html = elements

        return _html

    def urls(self):
        """Return urls in the html
        """
        for x in self.html.xpath('//a/@href'):
            if not x:
                continue
            if not x.startswith('http') and not x.startswith('https'):
                x = urljoin(self.url, x)
            # filter link like thunder://, ftp://
            if not x.startswith('http') and not x.startswith('https'):
                continue
            yield x

    def raise_for_status(self, allow_redirects=True):
        """Raises stored :class:`HTTPError` or :class:`URLError`, if one occurred.
        """
        if self.status_code == 304:
            return

        if self.error:
            http_error = HTTPError(self.error)
        elif (self.status_code >= 300) and (self.status_code < 400) and not \
                allow_redirects:
            http_error = HTTPError('%s Redirection' % (self.status_code))
        elif (self.status_code >= 400) and (self.status_code < 500):
            http_error = HTTPError('%s Client Error' % (self.status_code))
        elif (self.status_code >= 500) and (self.status_code < 600):
            http_error = HTTPError('%s Server Error' % (self.status_code))
        else:
            return

        http_error.response = self
        raise http_error

    def isok(self):
        try:
            self.raise_for_status()
            return True
        except:
            return False


def rebuild_response(result):
    response = Response()

    response.status_code = result.get('status_code', 599)
    response.url = result.get('url', '')
    response.headers = CaseInsensitiveDict(result.get('headers', {}))
    response.content = result.get('content', '')
    response.cookies = result.get('cookies', {})
    response.error = result.get('error')
    response.time = result.get('time', 0)
    response.original_url = result.get('original_url', response.url)
    response.save = result.get('save')

    return response

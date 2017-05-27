# -*- coding: utf-8 -*-
"""
create on 2017-05-27 下午12:57

author @heyao
"""

import cookielib
import httplib
import urllib2
from urllib import urlencode
from urlparse import urljoin


class Downloader(object):
    def __init__(self, cookie_enable=False):
        self.cookie_enable = cookie_enable
        self.cookie = cookielib.CookieJar()
        self.opener = self.general_opener(self.cookie)

    def download(self, url, payload=None, headers=None, formdata=None, **options):
        # TODO: add gzip support.
        headers = headers or {}
        cookie = self._cookie(self.cookie, only_keys=('tt_webid',))
        if self.cookie_enable and cookie:
            headers['Cookie'] = cookie
        if isinstance(formdata, dict):
            formdata = self.urlencode(formdata)
        if payload:
            url = '%s%s' % (url, self.urlencode(payload))
        request = urllib2.Request(
            url,
            data=formdata,
            headers=headers
        )
        try:
            response = self.opener.open(request)
        except urllib2.HTTPError as e:
            response = {
                'status': e.code,
                'url': url,
            }

        rep = Response(response)
        if not isinstance(response, dict):
            response.close()
        return rep

    def general_opener(self, cookie, url=None):
        handlers = [urllib2.HTTPHandler]
        if self.cookie_enable:
            handlers.append(urllib2.HTTPCookieProcessor(cookie))
        opener = urllib2.build_opener(*tuple(handlers))
        if url:
            try:
                opener.open(url)
            except Exception as e:
                raise RuntimeError("error acc while download '%s', %s" % (url, e))
        return opener

    def reset_cookie(self, url=None):
        self.cookie = cookielib.CookieJar()
        self.general_opener(self.cookie, url)

    def urlencode(self, data):
        return urlencode(data)

    def _cookie(self, cookie, only_keys=None):
        if only_keys:
            cookie_str = ';'.join('%s=%s' % (cook.name, cook.value) for cook in cookie if cook.name in only_keys)
        else:
            cookie_str = ';'.join('%s=%s' % (cook.name, cook.value) for cook in cookie)
        return cookie and cookie_str or ''


class Response(object):
    def __init__(self, response):
        self.response = response
        self.rep = {}
        self.init_rep()

    def init_rep(self):
        body = ''
        if not isinstance(self.response, dict):
            try:
                body = self.response.read()
            except httplib.IncompleteRead as e:
                body = e.partial
        self.rep.update(not isinstance(self.response, dict) and dict(
            url=self.response.url,
            status=self.response.code,
            body=body,
            headers=self.response.headers.dict
        ) or self.response)

    def __getattr__(self, item):
        try:
            value = self.rep[item]
        except KeyError:
            raise AttributeError("'%s' object has not attribute '%s'" % (self, item))
        return value

    def urljoin(self, url):
        return urljoin(self.url, url)


if __name__ == '__main__':
    downloader = Downloader()
    response = downloader.download('http://www.baidu.com')
    headers = response.headers
    status = response.status
    body = response.body
    pass

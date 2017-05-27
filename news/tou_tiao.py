# -*- coding: utf-8 -*-
"""
create on 2017-05-27 下午1:19

author @heyao
"""

import json
import time
import hashlib
import random

from lxml import etree

from http.downloader import Downloader
from collection.queue.redis_queue import RedisSetQueue


class TouTiaoSpider(object):
    def __init__(self, server, key):
        self.running = True
        self.downloader = Downloader(cookie_enable=True)
        self.data_queue = RedisSetQueue(server, key)
        self.host = '.toutiao.'
        self.query_params = {
            'category': 'news_finance',
            'utm_source': 'toutiao',
            'widen': 1,
            'max_behot_time': 0,
            'max_behot_time_tmp': 0,
            'tadrequire': True,
            'as': '',
            'cp': ''
        }
        self.url_base = 'https://www.toutiao.com/api/pc/feed/?'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }

    def parse_content(self):
        item = self.data_queue.pop()
        while item:
            url = item['url']
            response = self.downloader.download(url, headers=self.headers)
            if self.host not in url:
                print 'not in host.', url
                item = self.data_queue.pop()
                continue
            status = response.status
            if status >= 300:
                self.downloader.reset_cookie(url=url)
                self.data_queue.push(item)
                print 'forbidden', url, status
                item = self.data_queue.pop()
                continue
            sel = etree.HTML(response.body.decode('utf-8', 'ignore'))
            try:
                item.update(dict(
                    content='\n'.join(p for p in sel.xpath('//div[@class="article-content"]//p//text()')),
                    published_at=sel.xpath('//div[@class="articleInfo"]/span[last()]/text()')[0].strip()
                ))
            except IndexError:
                # print 'parse content error.', url
                item = self.data_queue.pop()
                continue
            print status, url
            yield item
            item = self.data_queue.pop()

    def start(self):
        as_, cp = self._general_as_cp()
        self.query_params['as'] = as_
        self.query_params['cp'] = cp
        response = self.downloader.download(self.url_base, self.query_params)
        data = json.loads(response.body)
        for i in data.get('data', []):
            if i['tag'] in ('ad',) or i['source'] == u'头条问答':
                continue
            item = dict(
                title=i['title'],
                url=response.urljoin(i['source_url']),
                relate_id=i['source_url'].split('/')[-2],
                tag=i['tag'],
                comments_count=i.get('comments_count', 0),
                source=i['source'],
                article_genre=i['article_genre']
            )
            self.data_queue.push(item)
        if 'next' in data:
            next_timestamp = data['next']['max_behot_time']
        else:
            print 'no next'
        self.query_params['max_behot_time'] = next_timestamp
        self.query_params['max_behot_time_tmp'] = next_timestamp

    def stop(self):
        self.running = False
        self.data_queue.clear()

    def _general_as_cp(self):
        t = int(time.time())
        e = hex(t).upper()
        i = hashlib.md5(e).hexdigest().upper()
        if 8 != len(e):
            return '479BB4B7254C150', '7E0AC8874BB0985'
        n = i[:5]
        a = i[-5:]
        s = ''.join(n[o] + e[o] for o in range(5))
        r = ''.join(e[c + 3] + a[c] for c in range(5))
        return 'A1%s%s' % (s, e[-3:]), '%s%sE1' % (e[:3], r)

    def result(self):
        try:
            while self.running:
                self.start()
                for item in self.parse_content():
                    yield item
        except KeyboardInterrupt:
            self.stop()


if __name__ == '__main__':
    import redis
    import pymongo

    con = pymongo.MongoClient()
    db = con['text']


    def save(data):
        db['news'].update({'_id': data['relate_id']}, {'$setOnInsert': data}, True)


    r = redis.StrictRedis()
    key = 'text:toutiao'
    toutiao = TouTiaoSpider(r, key)

    row = 1
    for item in toutiao.result():
        if row % 10 == 1:
            print 'process:', row
        row += 1
        save(item)

    con.close()

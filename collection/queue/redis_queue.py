# -*- coding: utf-8 -*-
"""
create on 2017-05-22 下午1:08

author @heyao
"""

from .base_queue import BaseQueue, BaseSignalQueue


class RedisSetQueue(BaseQueue):
    def __len__(self):
        return self.server.scard(self.key)

    def pop(self):
        value = self.server.spop(self.key)
        return value and self._decode_value(value) or None

    def push(self, value):
        return self.server.sadd(self.key, self._encode_value(value))

    def has_value(self, value):
        return self.server.sismember(self.key, self._encode_value(value))


class RedisSignalQueue(BaseSignalQueue):
    def __init__(self, server, key, serializer=None):
        super(RedisSignalQueue, self).__init__(server, key, serializer)

    def start(self):
        self.p = self.server.pubsub()
        self.p.subscribe(self.key)

    def stop(self):
        self.p.unsubscribe(self.key)
        self.p = None

    def pub(self, value):
        if self.p is not None:
            raise AttributeError("please run 'stop' function first")
        result = self.server.publish(self.key, value)
        return result

    def sub(self):
        if self.p is None:
            raise AttributeError("please run 'start' function first")
        msgs = self.p.listen()
        for msg in msgs:
            if msg['type'] == 'message':
                data = msg['data']
                return data

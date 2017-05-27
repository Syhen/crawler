# -*- coding: utf-8 -*-
"""
create on 2017-05-25 下午4:04

author @heyao
"""

from . import picklecompact


class Base(object):
    def __init__(self, server, key, serializer=None):
        self.server = server
        self.key = key
        if serializer is None:
            serializer = picklecompact
        self.serializer = serializer

    def _decode_value(self, encoded_value):
        return self.serializer.loads(encoded_value)

    def _encode_value(self, value):
        return self.serializer.dumps(value)


class BaseQueue(Base):
    def __init__(self, server, key, serializer=None):
        super(BaseQueue, self).__init__(server, key, serializer)

    def __len__(self):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def push(self, value):
        raise NotImplementedError

    def has_value(self, value):
        pass

    def clear(self):
        self.server.delete(self.key)


class BaseSignalQueue(Base):
    def __init__(self, server, key, serializer=None):
        super(BaseSignalQueue, self).__init__(server, key, serializer)
        self.p = None

    def start(self):
        pass

    def stop(self):
        pass

    def pub(self, value):
        pass

    def sub(self):
        pass

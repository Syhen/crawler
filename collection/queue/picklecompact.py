# -*- coding: utf-8 -*-
"""
create on 2017-05-22 下午1:22

author @heyao
"""


try:
    import cPickle as pickle  # PY2
except ImportError:
    import pickle


def loads(s):
    return pickle.loads(s)


def dumps(obj):
    return pickle.dumps(obj, protocol=-1)

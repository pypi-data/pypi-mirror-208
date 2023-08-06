# -*- coding: utf-8 -*-

import json
from inspect import isfunction


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """

    def __init__(self, *args, **kwargs):
        for k, v in self.__class__.__dict__.items():
            if not k.startswith('_') and not isfunction(v) and not isinstance(v, classmethod) and not isinstance(v, staticmethod) and not isinstance(v, property):
                self[k] = v
        super(ObjectDict, self).__init__(*args, **kwargs)

    __setattr__ = dict.__setitem__

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            return super(ObjectDict, self).__getattribute__(name)

    def from_json(self, json_data, json_loads=json.loads):
        self.update(json_loads(json_data))
        return self


def sort_set_list(l):
    new_list = list(l)
    set_list = list(set(new_list))
    set_list.sort(key=new_list.index)
    return set_list

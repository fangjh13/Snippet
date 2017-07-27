#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' 利用递归合并配置文件 '''


def merge(default, override):
    r = {}
    for k, v in default.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


configs = {
    'debug': True,
    'db': {
        'host': 'localhost',
        'port': 3306,
        'user': 'www-data',
        'password': 'www-data',
        'db': 'awesome',
        'test': {
            'a': 1,
            'b': 2
        }
    },
    'session': {
        'secret': 'Awesome'
    }
}

configs_override = {
    'db': {
        'host': '127.0.0.1'
    }
}

print(merge(configs, configs_override))

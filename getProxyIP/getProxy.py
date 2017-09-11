#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import config
import subprocess
import os
import random
from proxyDB import HandlerDB

if not os.path.exists(config.database):
    subprocess.call(['python3', './main.py'])

h = HandlerDB(config.database)
proxys = h.fetch_many()


def get_proxy():
    return random.choice(proxys)


def get_proxys():
    return proxys

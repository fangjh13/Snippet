# -*- coding: utf-8 -*-

import requests
import re
import random
from proxyDB import db
import config
from threading import Thread


class IPTool(object):
    def __init__(self, url, regexp):
        self.ip_pools = []
        self.true_ip = []
        self.url = url
        self.regexp = regexp

    def crawl_page(self):
        headers = config.headers
        headers['user-agent'] = random.choice(config.user_agent)
        try:
            r = requests.get(self.url, headers=headers)
        except BaseException as e:
            print(e)
        if r.status_code != requests.codes.ok:
            print('获取页面失败，错误代码 {}'.format(r.status_code))
        else:
            ip_addrs = re.findall(self.regexp, r.text)
            self.ip_pools.extend(ip_addrs)

    def verify(self, ip, port):
        headers = config.headers
        headers['user-agent'] = random.choice(config.user_agent)
        try:
            g = requests.get('http://www.baidu.com',
                             timeout=5,
                             proxies={'http': 'http://{}:{}'.format(ip, port),
                                      'https': 'https://{}:{}'.format(ip, port)})
        except BaseException as e:
            return
        if g.status_code == 200:
            print('检测到可用代理 ({}, {})'.format(ip, port))
            self.true_ip.append((ip, port))

    def handler(self):
        self.crawl_page()
        thread_list = []
        for i in c.ip_pools:
            thread_list.append(Thread(target=self.verify, args=(*i,)))
        for i in thread_list:
            i.start()
        for i in thread_list:
            i.join()

    def get_useful(self):
        return self.true_ip

    def save(self):
        pass


c = IPTool('http://www.xicidaili.com/nn/',
           "<td>([\d\.]+)</td>\s*<td>(\d+)</td>")
c.handler()

print(c.get_useful())

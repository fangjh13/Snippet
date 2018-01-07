# -*- coding: utf-8 -*-

import requests
import re
import random
from proxyDB import HandlerDB
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
            return
        if r.status_code != requests.codes.ok:
            print('获取页面{}失败，错误代码 {}'.format(self.url, r.status_code))
        else:
            ip_addrs = re.findall(self.regexp, r.text)
            if not ip_addrs:
                print('页面{}获取不到ip，检查网址和正则'.format(self.url))
            self.ip_pools.extend(ip_addrs)

    def verify(self, ip, port):
        headers = config.headers
        headers['user-agent'] = random.choice(config.user_agent)
        try:
            g = requests.get('https://httpbin.org/get?show_env=1',
                             timeout=config.timeout,
                             proxies={'http': 'http://{}:{}'.format(ip, port),
                                      'https': 'https://{}:{}'.format(ip, port)})
        except BaseException:
            return
        if ip in g.text:
            try:
                h = requests.get('https://www.bing.com/',
                                 timeout=config.timeout,
                                 proxies={'http': 'http://{}:{}'.format(ip, port),
                                          'https': 'https://{}:{}'.format(ip, port)})
            except BaseException:
                return
            if h.status_code == requests.codes.ok:
                print('检测到可用代理 ({}, {})'.format(ip, port))
                self.true_ip.append((ip, port))

    def handler(self):
        self.crawl_page()
        thread_list = []
        for i in self.ip_pools:
            thread_list.append(Thread(target=self.verify, args=(*i,)))
        for i in thread_list:
            i.start()
        for i in thread_list:
            i.join()

    def get_useful(self):
        return self.true_ip

    def save_to_db(self):
        print("在{}抓取到{}个可用ip，开始写入数据庫...".format(self.url, len(self.true_ip)))
        db = HandlerDB(config.database)
        db.insert_many(self.true_ip)
        db.close()


# 单独测试一个页面
# c = IPTool("http://www.mimiip.com/",
#            "<tr>\s+<td>([\d\.]+)</td>\s+<td>(\d+)</td>")
# c.handler()

# print(c.get_useful())

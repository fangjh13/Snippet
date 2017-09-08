#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import config
import os
from crawl import IPTool
from proxyDB import init_db, HandlerDB
from threading import Thread


def parser(url, regExp):
    print("获取{}页可用代理".format(url))
    process = IPTool(url, regExp)
    process.handler()
    process.save_to_db()


if __name__ == '__main__':
    if not os.path.exists(config.database):
        print("初始化数据庫...")
        init_db(config.database)
    else:
        print("清洗旧数据庫...")
        db = HandlerDB(config.database)
        db.clean_data()
        db.close()

    thread_list = []
    queue = list(config.url_and_RegExp.items())

    while queue:
        for i in range(20):
            thread_list.append(Thread(target=parser, args=queue.pop()))
            if not queue:
                break
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        thread_list.clear()

    db = HandlerDB(config.database)
    sum_items = len(db.fetch_many())
    db.close()
    print('程序运行完毕，总共找到{}个可用代理ip'.format(sum_items))

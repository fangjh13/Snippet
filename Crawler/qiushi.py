#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import threading

''' 爬取糗事百科的内容 每按一次回车出现一篇文章 '''

class QSPedia(object):
    def __init__(self):
        self.page = 1
        self.sum_page_articles = []
        self.enable = True

    def get_one_page(self, index):
        headers = {'user-agent': "Mozilla/5.0 (X11; Linux x86_64)"}
        url = 'https://www.qiushibaike.com/8hr/page/' + str(index)
        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        # every article all content RegExp
        partial_pattern = re.compile(r'clearfix">(.*?contentHerf.*?)<div class="article',
                re.S)
        partial_content = re.findall(partial_pattern, r.text)
        if not partial_content:
            raise ValueError('no content fetched')
        # every article parser RegExp
        rs_pattern = re.compile(r'<h2>(.*?)</h2>.*?<span>(.*?)</span>.*?number">(\d*?)</i>.*?number">(\d*?)</i>',
                re.S)
        # every article content
        rs = []
        for item in partial_content:
            # filter picture article and hided article
            if '<div class="thumb">' in item:
                continue
            if '<span class="contentForAll">' in item:
                continue
            parser = re.findall(rs_pattern, item)
            if not parser:
                raise ValueError('parser every article failed')
            for name, txt, likes, comments in parser:
                rs.append(
                    dict(name=name.strip(),
                        txt=txt.strip().replace('<br/>','\n'),
                        likes=likes.strip(),
                        comments=comments.strip()))
        return rs

    # ensure two pages in list
    def page_list(self):
        while len(self.sum_page_articles) < 3:
            p = self.get_one_page(self.page)
            self.sum_page_articles.append(p)
            self.page += 1

    # print every article in one page
    def print_one_article(self, one_page_articles, page_number):
        for i in one_page_articles:
            stdin = input()
            if stdin == 'Q':
                self.enable = False
                break
            print('page: {}\nauthor: {}\nlikes: {}\ncomments: {}\n{}'.format(
                page_number, i['name'], i['likes'], i['comments'], i['txt']))

    def main(self):
        self.page_list()
        # display current page
        current_page = 1
        print('爬虫已经开始工作.....')
        print('按回车开始阅读，`Q`键退出程序')
        while self.enable:
            articles = self.sum_page_articles[0]
            # delete first page content
            del self.sum_page_articles[0]
            # load another page article
            t = threading.Thread(target=lambda: self.page_list())
            t.start()
            self.print_one_article(articles, current_page)
            current_page += 1


if __name__ == '__main__':
    q = QSPedia()
    q.main()

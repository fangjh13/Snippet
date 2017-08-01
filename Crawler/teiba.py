#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import re


class TieBa(object):
    '''
    爬取百度贴吧
    地址如：https://tieba.baidu.com/p/5176659692
    '''

    def set_url(self, url, see_lz=True):
        if see_lz:
            self.base_url = url + '?see_lz=1&pn='
        else:
            self.base_url = url + '?pn='

    def get_page_soup(self, page):
        html = requests.get(self.base_url + str(page))
        soup = BeautifulSoup(html.text, 'lxml')
        return soup

    def sum_page_navigation(self, soup):
        p = list(soup.find('li', class_='l_reply_num').children)[2].string
        return int(p)

    def get_page_title(self, soup):
        return str(soup.title.string)

    def get_page_content(self, soup):
        main_contents = soup.find_all('div', class_='d_post_content_main')
        # [[floor, content]]
        contents = []
        for p in main_contents:
            floor = str(p.find('span', class_='tail-info',
                               string=re.compile(r'\d+楼')).string)
            post = p.find('div', class_='d_post_content')
            content = '\n'.join(list(post.stripped_strings))
            contents.append([floor, content])
        return contents

    def print_page_content(self, contents):
        for i in contents:
            print(i[0], end=' ')
            print('-' * 30)
            print(i[1])
            print()

    def save(self, contents, filename):
        with open('{}.txt'.format(filename), 'a') as f:
            for i in contents:
                f.write(i[0] + ' ' + '-' * 30 + '\n')
                f.write(i[1] + '\n' * 2)

    def main(self):
        url = input('贴吧地址： ').strip()
        see_lz = int(input('是否只看楼主(是：1，否：0)： '))
        try:
            assert see_lz in (0, 1)
        except AssertionError:
            raise KeyError('请输入0或1')
        self.set_url(url, see_lz)
        soup = self.get_page_soup(1)
        title = self.get_page_title(soup)
        sum_p = self.sum_page_navigation(soup)
        for i in range(1, sum_p + 1):
            soup = self.get_page_soup(i)
            contents = self.get_page_content(soup)
            print('第{}页，正在写入文件 ....'.format(i))
            self.save(contents, title)
            # self.print_page_content(contents)


if __name__ == '__main__':
    TieBa().main()

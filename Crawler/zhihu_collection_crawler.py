#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import re
import os


class ZhiHuCollection(object):
    ''' 知乎收藏夹图片下载需要手动传入cookie '''

    def __init__(self, collection, cookie):
        self.url = 'https://www.zhihu.com/collection/' + str(collection)
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
        # 浏览器模拟登录cookie，只需`z_c0`, 需要手动复制
        self.cookie = dict(z_c0=cookie)

    def get_page(self, **kw):
        ''' 获取整个页面 '''
        r = requests.get(self.url, headers=self.headers,
                         cookies=self.cookie, **kw)
        return r.text

    def get_page_count(self):
        ''' 分析页码 '''
        mark_up = self.get_page()
        soup = BeautifulSoup(mark_up, 'lxml')
        nav = soup.find('div', class_='zm-invite-pager')
        count = str(nav.find_all('span')[-2].string)
        return int(count)

    def get_page_items(self, page):
        ''' 获取每页的问题id和第一个回答的id '''
        payload = {'page': page}
        mark_up = self.get_page(params=payload)
        soup = BeautifulSoup(mark_up, 'lxml')
        items = soup.find_all('div', class_='zm-item')
        rs = []
        for i in items:
            # [question tile, question id, first answer id]
            temp = []
            title_tag = i.find(class_='zm-item-title')
            if title_tag:
                temp.append(str(title_tag.string).strip())
                try:
                    string = i.find('a', class_='toggle-expand')['href']
                except TypeError:
                    continue
                re_rs = re.search(r'/\w+/(\d+)/\w+/(\d+)', string)
                if re_rs:
                    qs_id, asr_id = re_rs.groups()
                    temp.extend([qs_id, asr_id])
                    rs.append(temp)
        return rs

    def get_answer_pictures(self, qus_id, ans_id):
        ''' 获取一个问题回答的所有图片地址 '''
        url = 'https://www.zhihu.com/question/{}/answer/{}'.format(
            qus_id, ans_id)
        print('获取回答图片并保存本地 {}'.format(url))
        html = requests.get(url, headers=self.headers,
                            cookies=self.cookie).text
        soup = BeautifulSoup(html, 'lxml')
        rs = []
        for i in soup.find_all('img',
                               class_='origin_image zh-lightbox-thumb lazy'):
            rs.append(i['data-original'])
        return rs

    def save_to_local(self, path, address):
        ''' 保存图片到本地 '''
        data = requests.get(address, headers=self.headers,
                            cookies=self.cookie).content
        file_name = address.rsplit('/')[-1]
        with open(os.path.join(path, file_name), 'wb') as f:
            f.write(data)

    def main(self):
        pages = self.get_page_count()
        print('获取总页数，一个有{}页'.format(pages))
        path_dir = os.path.abspath(os.path.dirname(__file__))
        for p in range(1, pages + 1):
            items = self.get_page_items(p)
            for i in items:
                file_target = os.path.join(path_dir, i[0])
                if not os.path.exists(file_target):
                    os.mkdir(file_target)
                for pic in self.get_answer_pictures(i[1], i[2]):
                    self.save_to_local(file_target, pic)


# example:69135664, 102112319, 25971719, 38624707, 61913303, 72114548, 30256531
if __name__ == '__main__':
    collection_id = input('请输入收藏夹id: ')
    cookie_z_c0 = input('模拟登录手动复制`z_c0`的cookie: ')
    drive = ZhiHuCollection(collection_id, cookie_z_c0)
    drive.main()

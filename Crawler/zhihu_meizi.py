#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import re
import os


class ZhiHuCollection(object):
    def __init__(self, collection):
        self.url = 'https://www.zhihu.com/collection/' + str(collection)
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)'}

    def get_page(self, **kw):
        r = requests.get(self.url, headers=self.headers, **kw)
        return r.text

    def get_page_count(self):
        mark_up = self.get_page()
        soup = BeautifulSoup(mark_up, 'lxml')
        nav = soup.find('div', class_='zm-invite-pager')
        count = str(nav.find_all('span')[-2].string)
        return int(count)

    def get_page_items(self, page):
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
        url = 'https://www.zhihu.com/question/{}/answer/{}'.format(
            qus_id, ans_id)
        print(url)
        cookie = dict(
            z_c0="2|1:0|10:1502678061|4:z_c0|92:Mi4xX1hVWkFBQUFBQUFBRUFMbFlMazNEQ2NBQUFDRUFsVk5MWm00V1FBQjl2WkVrWkszNS1TNFZoektiYjhMb2FmYjBR|85e18f906ab23fc3ba65b46119e40702705dae755fd926981325a9c5e2f90228")
        html = requests.get(url, headers=self.headers, cookies=cookie).text
        soup = BeautifulSoup(html, 'lxml')
        rs = []
        for i in soup.find_all('img',
                               class_='origin_image zh-lightbox-thumb lazy'):
            rs.append(i['data-original'])
        return rs

    def save_to_local(self, path, address):
        data = requests.get(address, headers=self.headers).content
        file_name = address.rsplit('/')[-1]
        with open(os.path.join(path, file_name), 'wb') as f:
            f.write(data)

    def main(self):
        pages = self.get_page_count()
        path_dir = os.path.abspath(os.path.dirname(__file__))
        for p in range(1, 3):
            items = self.get_page_items(p)
            for i in items:
                file_target = os.path.join(path_dir, i[0])
                if not os.path.exists(file_target):
                    os.mkdir(file_target)
                for pic in self.get_answer_pictures(i[1], i[2]):
                    self.save_to_local(file_target, pic)




zhihu = ZhiHuCollection(69135664)
# print(zhihu.get_page_items(1))
zhihu.main()
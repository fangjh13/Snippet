#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
抓取"http://www.51voa.com/VOA_Standard_1_archiver.html"的文本
以日期标题命名
输入页码指定抓取的页数
需要安装goose模块
'''


from goose import Goose
from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse, urljoin
import re
import datetime
import os


def get_body(url):
    headers = {'User-Agent':
               "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36"}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    return response.read()


# {page_number: page_link, ...}
def get_every_page_link(url):
    body = get_body(url)
    url = "http://" + urlparse(url)[1]
    soup = BeautifulSoup(body, 'lxml')
    rs = {}
    page_all = soup.find(id="pagelist").find_all('a')
    for i in page_all:
        rs[i.string[1:-1]] = urljoin(url, i.get('href'))
    return rs


# [[article_title, article_link], ... ]
def get_every_article_link(every_url):
    body = get_body(every_url)
    url = "http://" + urlparse(every_url)[1]
    soup = BeautifulSoup(body, 'lxml')
    rs = []
    article_all = soup.find(id="list").find_all('li')
    for i in article_all:
        date = '20' + \
            re.search(r'.*?\((\d{1,2}-\d{1,2}-\d{1,2})\)', i.text).group(1)
        date_f = date.strip().split('-')
        date = datetime.date(int(date_f[0]), int(date_f[1]), int(date_f[-1]))
        name = i.a.string.strip()
        # remove ':' in filename
        if ':' in name:
            index = name.index(':')
            name = name[:index] + ' ' + name[index + 1:]
        # remove '/' in filename
        if '/' in name:
            index = name.index('/')
            name = name[:index] + ' ' + name[index + 1:]
        link = urljoin(url, i.a.get('href'))
        rs.append([date.strftime('%Y-%m-%d') + name, link])
    return rs


def extractor_txt(url):
    g = Goose()
    article = g.extract(url=url)
    return article.cleaned_text


if __name__ == '__main__':
    start = raw_input('Page start <enter a number>: ')
    end = raw_input('Page end <enter a number>: ')
    url = "http://www.51voa.com/VOA_Standard_1_archiver.html"
    basedir = os.path.abspath(os.path.dirname(
        __file__)) + os.path.sep + 'VOA_Artical'

    if os.path.isdir(basedir):
        os.chdir(basedir)
    else:
        os.makedirs(basedir)
        os.chdir(basedir)

    page_source = get_every_page_link(url)

    if not ((start in page_source) & (end in page_source)):
        raise Exception('The number of pages is out of range.')

    print '-' * 10 + ' start ' + '-' * 10
    for page in range(int(start), int(end) + 1):
        article_source = get_every_article_link(page_source[str(page)])
        for article_title, article_link in article_source:
            plain = extractor_txt(article_link)
            with open(article_title + '.txt', 'w') as f:
                print 'Saving {0}....'.format(article_title.encode('utf-8'))
                f.write(plain.encode('utf-8'))
    print '-' * 10 + ' end  ' + '-' * 10
    print 'Every file saved in VOA_Artical folder'

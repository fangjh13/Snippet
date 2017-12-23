#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from functools import partial
from datetime import datetime
from collections import deque
import re
import time
from bs4 import BeautifulSoup
from lxml.html import fromstring


def download(url, user_agent, num_retries=2):
    headers = {'User-Agent': user_agent}
    request = Request(url, headers=headers)
    try:
        print('Downloading ', url)
        html = urlopen(request).read().decode('utf-8')
    except URLError as e:
        print('Error: ', e.reason, e.code)
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= getattr(e, 'code') < 600:
                return download(url, user_agent, num_retries - 1)
        html = None
    except BaseException as e:
        print(e)
    return html


def get_links(html, org_link):
    regex = re.compile(r'<a[^>]*?href=[\"\'](.*?)[\"\'].*?>', re.IGNORECASE)
    my_urljoin = partial(urljoin, org_link)
    links = map(my_urljoin, re.findall(regex, html))
    links = [link.rsplit('?', maxsplit=1)[0] for link in links]

    def same_domain(url_1, url_2):
        return urlparse(url_1).netloc == urlparse(url_2).netloc

    return [l for l in links if same_domain(l, org_link)]


FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent',
          'tld', 'currency_code', 'currency_name', 'phone',
          'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')


def scrape_callback_1(html):
    soup = BeautifulSoup(html, 'lxml')
    result = {}
    for i in FIELDS:
        # result[i] = soup.find('table').find(
        #     'tr', id="places_{}__row".format(i)).find(
        #     'td', class_="w2p_fw").text
        result[i] = soup.select('table > tr#places_{}__row > td.w2p_fw'.format(i))[0].text
    return result


def scrape_callback_2(html):
    tree = fromstring(html)
    result = {}
    for i in FIELDS:
        # result[i] = tree.cssselect(
        #     'table > tr#places_{}__row > td.w2p_fw'.format(i))[0].text_content()
        result[i] = tree.xpath('//table/tr[@id="places_{}__row"]/td[@class="w2p_fw"]'.format(i))[0].text_content()
    return result


class Throttle(object):
    """add a delay between downloads for each domain"""

    def __init__(self, delay_time):
        self.delay_time = delay_time
        self.domain = {}

    def wait(self, url):
        netloc = urlparse(url).netloc
        if self.domain.get(netloc, None) and self.delay_time > 0:
            delta = (datetime.now() - self.domain[netloc]).seconds
            if 0 < delta < 2:
                time.sleep(self.delay_time)
        self.domain[netloc] = datetime.now()


def main(url, link_regex, delay=-1, retries=2, max_depth=-1, max_download=-1, user_agent='Mozilla'):
    """
    :param url: url
    :param link_regex: filter link
    :param delay: less than zero unlimted
    :param retries: how many retry a url
    :param max_depth: rember url depth if max_depth is less than zero unlimted
    :param max_download: download pages if less than zero behalf unlimted
    :param user_agent: User-Agent
    """
    crawl_queue = deque([url])
    # check weather crawled and depth
    seen = {url: 0}
    slow = Throttle(delay)
    downloaded = 0

    while crawl_queue:
        link = crawl_queue.pop()
        # current page depth
        depth = seen[link]
        if depth > max_depth:
            continue

        slow.wait(link)
        html = download(link, user_agent, retries)
        # get this page all links
        links = get_links(html, link)

        for l in links:
            if l not in seen and re.search(link_regex, l):
                # add crawl queue
                crawl_queue.append(l)
                # set seen
                seen[l] = depth + 1

        # increase download number
        downloaded += 1
        if downloaded == max_download:
            break

    # print(seen)
    # print(downloaded)


if __name__ == '__main__':
    html = download(
        'http://example.webscraping.com/places/default/view/China-47', 'Mozilla')
    for name, scrape in [('bs4', scrape_callback_1), ('lxml', scrape_callback_2)]:
        start = time.time()
        for i in range(1000):
            result = scrape(html)
            assert result['iso'] == 'CN'
        end = time.time()
        print(name, "{:.5f}".format(end-start))




    # main('http://example.webscraping.com/',
    #      '/places/default/(view|index)', max_depth=3, max_download=50, delay=2)

    # https://bitbucket.org/wswp/code/src/9e6b82b47087c2ada0e9fdf4f5e037e151975f0f/chapter01/link_crawler3.py?at=default&fileviewer=file-view-default

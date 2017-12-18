#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from functools import partial
from datetime import datetime
import re
import time


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
    return html


def link_crawler(seed_url, link_regex):
    link_queue = [seed_url]
    seen = set(link_queue)

    while link_queue:
        link = link_queue.pop()
        for l in get_links(link):
            if re.search(link_regex, l):
                if l not in seen:
                    seen.add(l)
                    link_queue.append(l)


def get_links(link):
    html = download(link, 'Mozilla')
    regex = re.compile(r'<a[^>]*?href=[\"\'](.*?)[\"\'].*?>', re.IGNORECASE)
    my_urljoin = partial(urljoin, link)
    return map(my_urljoin, re.findall(regex, html))


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

# https://bitbucket.org/wswp/code/src/9e6b82b47087c2ada0e9fdf4f5e037e151975f0f/chapter01/link_crawler3.py?at=default&fileviewer=file-view-default
link_crawler('http://example.webscraping.com/', '/places/default/(view|index)')

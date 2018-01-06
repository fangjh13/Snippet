#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse, urldefrag
from functools import partial
from datetime import datetime, timedelta
from collections import deque
import re
import time
import lxml.html
import csv
import os
import pickle
import zlib


class Download(object):
    """download object can use `__call__`, exclusive use `get` method"""

    def __init__(self, user_agent, delay=3, num_retries=1, cache=None):
        self.user_agent = user_agent
        self.delay = delay
        self.num_retries = num_retries
        self.cache = cache
        self.throttle = Throttle(delay)

    def __call__(self, url):
        url, _ = urldefrag(url)
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # url is not available in cache
                pass
            else:
                # server error so re-download
                if self.num_retries > 0 and result['code'] >= 500:
                    result = None
        if result is None:
            # result was not loaded from cache
            # so still need to download
            result = self.download(url, self.num_retries)
            if result['html'] and self.cache:
                # save result to cache
                self.cache[url] = result
        return result['html']

    def download(self, url, num_retries):
        url, _ = urldefrag(url)
        headers = {'User-Agent': self.user_agent}
        request = Request(url, headers=headers)
        html = ''
        status_code = 600
        try:
            self.throttle.wait(url)
            print('Downloading ', url)
            response = urlopen(request)
            status_code = response.code
            html = response.read()
            if html:
                # html is not none decode
                html = html.decode('utf-8')
        except Exception as e:
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.download(url, num_retries - 1)
            else:
                status_code = e.code if hasattr(e, 'code') else 600
        return {'html': html, 'code': status_code}


def get_links(html, org_link):
    regex = re.compile(r'<a[^>]*?href=[\"\'](.*?)[\"\'].*?>', re.IGNORECASE)
    my_urljoin = partial(urljoin, org_link)
    # handle if html is None
    if not html:
        return []

    links = map(my_urljoin, re.findall(regex, html))
    links = [link.rsplit('?', maxsplit=1)[0] for link in links]

    def same_domain(url_1, url_2):
        return urlparse(url_1).netloc == urlparse(url_2).netloc

    return [l for l in links if same_domain(l, org_link)]


class ScrapeCallback(object):
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital',
                       'continent', 'tld', 'currency_code', 'currency_name',
                       'phone', 'postal_code_format', 'postal_code_regex',
                       'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        # filter url and handle if html is None
        if html and re.search(r'/view/', url):
            tree = lxml.html.fromstring(html)
            result = []
            for i in self.fields:
                r = tree.xpath(
                    '''//table/tr[@id="places_{}__row"]/td[@class="w2p_fw"]
                    '''.format(i))[0].text_content()
                result.append(r)
            self.writer.writerow(result)


class Throttle(object):
    """add a delay between downloads for each domain"""

    def __init__(self, delay_time):
        self.delay_time = delay_time
        self.domain = {}

    def wait(self, url):
        netloc = urlparse(url).netloc
        if self.domain.get(netloc, None) and self.delay_time > 0:
            delta = (datetime.now() - self.domain[netloc]).total_seconds()
            if 0 < delta < 3:
                time.sleep(self.delay_time)
        self.domain[netloc] = datetime.now()


class DiskCache(object):
    def __init__(self, cache_dir, expires=timedelta(days=30)):
        self.cache_dir = cache_dir
        self.expires = expires

    def url_to_path(self, url):
        parse_result = urlparse(url)
        path = parse_result.path
        if not path:
            file_name = parse_result.netloc + '/index.html'
        elif path.endswith('/'):
            file_name = parse_result.netloc + path + 'index.html'
        else:
            file_name = parse_result.netloc + path
        file_name = re.sub(r'[^/a-zA-Z0-9\.,;:_\-]', '_', file_name)
        file_name = '/'.join(i[:255] for i in file_name.split('/'))
        return os.path.join(self.cache_dir, file_name)

    def __setitem__(self, url, result):
        """save data to disk for this url"""
        file_name = self.url_to_path(url)
        folder = os.path.dirname(file_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # if same directory name change it
        if os.path.isdir(file_name):
            file_name += '.html'
        with open(file_name, 'wb') as f:
            data = pickle.dumps((result, datetime.now()))
            f.write(zlib.compress(data))

    def __getitem__(self, url):
        """load data from disk for this url"""
        file_name = self.url_to_path(url)
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as f:
                result, timestamp = pickle.loads(zlib.decompress(f.read()))
                if self.has_expired(timestamp):
                    raise KeyError(url + ' expired')
                return result
        # if is directory try add '.html'
        elif os.path.isdir(file_name):
            file_name += '.html'
            try:
                with open(file_name, 'rb') as f:
                    result, timestamp = pickle.loads(zlib.decompress(f.read()))
                    if self.has_expired(timestamp):
                        raise KeyError(url + ' expired')
                    return result
            except Exception:
                raise KeyError(url + ' does not exists')
        else:
            raise KeyError(url + ' does not exists')

    def has_expired(self, timestamp):
        return datetime.now() > self.expires + timestamp


def main(url, link_regex, delay=-1, retries=2, max_depth=-1, max_download=-1, user_agent='Mozilla', cache=None, callback=None):
    """
    :param url: url
    :param link_regex: filter link
    :param delay: less than zero unlimted
    :param retries: how many retry a url
    :param max_depth: rember url depth if max_depth is less than zero unlimted
    :param max_download: download pages if less than zero behalf unlimted
    :param user_agent: User-Agent
    """
    url, _ = urldefrag(url)
    crawl_queue = deque([url])
    # check weather crawled and depth
    seen = {url: 0}
    downloaded = 0
    d = Download(user_agent, delay, retries, cache)

    while crawl_queue:
        link = crawl_queue.pop()
        # current page depth
        depth = seen[link]
        if depth > max_depth and max_depth > 0:
            continue

        html = d(link)
        # get this page all links
        links = get_links(html, link)

        # execute callback functions
        if callback:
            # can add callback return links
            links.extend(callback(link, html) or [])

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
    main('http://example.webscraping.com/',
         '/places/default/(view|index)', max_depth=-1, max_download=-1, delay=2, callback=ScrapeCallback(), cache=DiskCache('cache_folder'))

# https://bitbucket.org/wswp/code/src/9e6b82b47087c2ada0e9fdf4f5e037e151975f0f/chapter02/scrape_callback2.py?at=default&fileviewer=file-view-default

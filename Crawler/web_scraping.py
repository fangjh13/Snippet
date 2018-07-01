#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse, urldefrag
from functools import partial
from datetime import datetime, timedelta
from collections import deque
from pymongo import MongoClient, errors
from bson.binary import Binary
from zipfile import ZipFile
from io import BytesIO, TextIOWrapper
from threading import Thread
from multiprocessing import Process, cpu_count
import re
import time
import lxml.html
import csv
import os
import pickle
import zlib
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *


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
            response = urlopen(request, timeout=3)
            status_code = response.code
            html = response.read()
            if html:
                # html is not none decode
                html = html.decode('utf-8')
        except Exception as e:
            print('Exception: {} url: {}'.format(str(e), url))
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


class AlexaCallback(object):
    """ download Alexa websites may need cross GFW """

    def __init__(self, max_urls=40):
        self.max_urls = max_urls
        self.seed_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

    def __call__(self, url, data):
        if url == self.seed_url:
            with ZipFile(BytesIO(data)) as z:
                filename = z.namelist()[0]
                urls = []
                n = 0
                for _, website in csv.reader(TextIOWrapper(z.open(filename))):
                    url = 'http://' + website
                    urls.append(url)
                    n += 1
                    if n >= self.max_urls:
                        break
            return urls


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


class MongoCache(object):
    """save cache into MongoDB"""

    def __init__(self, client=None, expires=timedelta(days=30)):
        self.client = client if client else MongoClient(
            host='localhost', port=27017)
        self.db = self.client['cache']
        # create expired index
        self.db.webpage.create_index('timestamp',
                                     expireAfterSeconds=expires.total_seconds())

    def __setitem__(self, url, result):
        """save value for this url"""
        save_data = {
            'result': Binary(zlib.compress(pickle.dumps(result))),
            'timestamp': datetime.utcnow()}
        self.db.webpage.update_one({'_id': url},
                                   {'$set': save_data},
                                   upsert=True)

    def __getitem__(self, url):
        """load value at this url"""
        r = self.db.webpage.find_one({'_id': url})
        if r:
            return pickle.loads(zlib.decompress(r['result']))
        else:
            raise KeyError(url + ' does not exists')

    def has_expired(self, timestamp):
        return datetime.now() > self.expires + timestamp


class MongoQueue:
    # possible states of a download
    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, client=None, timeout=300):
        self.client = MongoClient() if client is None else client
        self.db = self.client.cache
        self.timeout = timeout

    def __bool__(self):
        """ Return True if there are more jobs to process """
        record = self.db.crawl_queue.find_one(
            {'status': {'$ne': self.COMPLETE}}
        )
        return True if record else False

    def push(self, url):
        """ add new URL to queue if does not exist """
        try:
            self.db.crawl_queue.insert_one(
                {'_id': url, 'status': self.OUTSTANDING}
            )
        except errors.DuplicateKeyError:
            pass

    def pop(self):
        """ Get an outstanding URL from the queue and set its
            status to processing. If the queue is empty a KeyError
            exception is raised """
        record = self.db.crawl_queue.find_one_and_update(
            {'status': self.OUTSTANDING},
            {'$set': {'status': self.PROCESSING, 'timestamp': datetime.now()}}
        )
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError()

    def complete(self, url):
        self.db.crawl_queue.update(
            {'_id': url}, {'$set': {'status': self.COMPLETE}})

    def repair(self):
        record = self.db.crawl_queue.update_many(
            {'timestamp': {'$lt': datetime.now() - timedelta(seconds=self.timeout)},
             'status': {'$ne': self.COMPLETE}},
            {'$set': {'status': self.OUTSTANDING}})
        if record.modified_count:
            print('Released: {} urls'.format(record.modified_count))


class BrowserRender(QWebView):
    def __init__(self, show=True):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        if show:
            self.show()

    def download(self, url, timeout=60):
        """ wait for download to complete and return result """
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        self.loadFinished.connect(loop.quit)
        self.load(QUrl(url))
        timer.start(timeout * 1000)

        loop.exec_()  # delay here until download finished

        if timer.isActive():
            # downloaded successfully
            timer.stop()
            return self.html()
        else:
            # timeout
            print('Request timeout: ' + url)

    def html(self):
        """Shortcut to return the current HTML"""
        return self.page().mainFrame().toHtml()

    def find(self, pattern):
        """Find all elements that match the pattern"""
        return self.page().mainFrame().findAllElements(pattern)

    def attr(self, pattern, name, value):
        """set attribute for matching elements"""
        for e in self.find(pattern):
            e.setAttribute(name, value)

    def text(self, pattern, value):
        """set attribute for matching elements"""
        for e in self.find(pattern):
            e.setPlainText(value)

    def click(self, pattern):
        """click matching elements"""
        for e in self.find(pattern):
            e.evaluateJavaScript("this.click()")

    def wait_load(self, pattern, timeout=60):
        """wait until pattern is found and return matches"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.app.processEvents()
            matches = self.find(pattern)
            if matches:
                return matches
        print('wait load timed out')


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
        link = crawl_queue.popleft()
        # current page depth
        depth = seen[link]
        if depth > max_depth and max_depth > 0:
            continue

        html = d(link)
        links = []

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


def thread_crawler(seed_url, max_threads=10, callback=None):
    # the queue of URL's that still need to be crawled
    crawl_queue = MongoQueue(timeout=300)
    crawl_queue.push(seed_url)

    d = Download(user_agent='Mozilla')

    # process worker
    def process_queue():
        while True:
            try:
                url = crawl_queue.pop()
            except KeyError:
                break
            else:
                html = d(url)
                if callback:
                    links = callback(url, html)
                    if links:
                        for URL in links:
                            crawl_queue.push(URL)
                crawl_queue.complete(url)

    threads = []
    while threads or crawl_queue:
        for t in threads:
            if not t.is_alive():
                # remove the stopped thread
                threads.remove(t)
        while len(threads) < max_threads and crawl_queue:
            thread = Thread(target=process_queue, args=())
            thread.daemon = True
            thread.start()
            threads.append(thread)
        # all threads have been processed
        # sleep temporarily so CPU can focus execution elsewhere
        time.sleep(1)


def multiprocess_crawl(url, max_threads, callback):
    cpus = cpu_count()
    print('Starting {} process'.format(cpus))
    processes = []
    for i in range(cpus):
        p = Process(target=thread_crawler, args=[url, max_threads, callback])
        p.start()
        processes.append(p)
    # wait for processes to complete
    for p in processes:
        p.join()


if __name__ == '__main__':
    br = BrowserRender()
    br.download('http://example.webscraping.com/places/default/search')
    br.attr('#search_term', 'value', '.')
    br.text('#page_size option:checked', '1000')
    br.click('#search')
    elements = br.wait_load('#results a')
    contries = [e.toPlainText().strip() for e in elements]
    print(contries)

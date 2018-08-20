import json
import logging
import os
from pathlib import Path
from urllib.request import urlopen, Request
import logging
from time import time
from threading import Thread
from queue import Queue
from multiprocessing import Pool
from functools import partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from PIL import Image
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

types = {'image/jpeg', 'image/png'}


def get_links(client_id):
    headers = {'Authorization': 'Client-ID {}'.format(client_id)}
    req = Request('https://api.imgur.com/3/gallery/random/random/', headers=headers, method='GET')
    with urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return [item['link'] for item in data['data'] if 'type' in item and item['type'] in types]


def download_link(directory, link):
    download_path = directory / os.path.basename(link)
    with urlopen(link) as image, download_path.open('wb') as f:
        f.write(image.read())
    logger.info('Downloaded %s', link)


def setup_download_dir():
    download_dir = Path('images')
    if not download_dir.exists():
        download_dir.mkdir()
    return download_dir

def main():
    ts = time()
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")
    download_dir = setup_download_dir()
    links = get_links(client_id)
    for link in links:
        download_link(download_dir, link)
    logging.info('download {0} links, Took {1:.5f} seconds'.format(len(links), time()-ts))

def main1():
    ts = time()
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")
    download_dir = setup_download_dir()
    links = get_links(client_id)
    queue = Queue()
    for i in range(8):
        t = ImgurDownloader(queue)
        t.daemon = True
        t.start()
    for link in links:
        queue.put((download_dir, link))
    queue.join()
    logging.info('download {0} links, Took {1:.5f} seconds'.format(len(links), time()-ts))

    

class ImgurDownloader(Thread):
    def __init__(self, q):
        super(ImgurDownloader, self).__init__()
        self.queue = q

    def run(self):
        while True:
            directory, link = self.queue.get()
            try:
                download_link(directory, link)
            finally:
                self.queue.task_done()

def main2():
    ts = time()
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")
    download_dir = setup_download_dir()
    links = get_links(client_id)
    download = partial(download_link, download_dir)
    with Pool(8) as p:
        p.map(download, links)
    logging.info('download {0} links, Took {1:.5f} seconds'.format(len(links), time()-ts))


def main3():
    ts = time()
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")
    download_dir = setup_download_dir()
    links = get_links(client_id)
    download = partial(download_link, download_dir)
    with ThreadPoolExecutor(8) as t:
        t.map(download, links)
    logging.info('download {0} links, Took {1:.5f} seconds'.format(len(links), time()-ts))

def create_thumbnail(size, path):
    image = Image.open(path)
    image.thumbnail(size)
    path = Path(path)
    image_name = path.stem + '_thumbnail' + path.suffix
    image.save(path.with_name(image_name))

def main4():
    time_start = time()
    path = Path('images')
    for image in path.iterdir():
        create_thumbnail((128,128), image)
    logging.info('cost time {:.5f}'.format(time() - time_start))

def main5():
    time_start = time()
    images = Path('images').iterdir()
    thumbnail = partial(create_thumbnail, (128, 128))
    with ProcessPoolExecutor(8) as p:
        p.map(thumbnail, images)
    logging.info('cost time {:.5f}'.format(time() - time_start))

async def async_download_link(session, direcotry, link):
    download_path = direcotry / os.path.basename(link)
    async with session.get(link) as resp:
        with download_path.open('wb') as f:
            while True:
                chunck = await resp.content.read(1024)
                if not chunck:
                    break
                f.write(chunck)
    logger.info('Downloaded %s', link)

async def main6():
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")
    download_dir = setup_download_dir()
    
    async with aiohttp.ClientSession() as session:
        tasks = [async_download_link(session, download_dir, l) for l in get_links(client_id)]
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    time_start = time()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main6())
    finally:
        loop.close()
    logging.info('cost time {:.5f}'.format(time() - time_start))
    # main3()

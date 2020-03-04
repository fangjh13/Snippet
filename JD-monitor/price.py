#!/usr/bin/env python3.8

import asyncio
import re
import os
import time
import logging
from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout, ClientError
from aiohttp.http_exceptions import HttpProcessingError
from lxml import html

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def parse_price(page_html: str) -> dict:
    """ from html text pasre item info """
    result: Dict(str, str) = {}
    tree = html.fromstring(page_html)
    name = tree.xpath('//title')[0].text
    result['name'] = name

    price = tree.xpath('//*[@id="priceSale"]')
    if price:
        content = price[0].text_content()
        extract = re.findall(r'\d*\.\d+', content)
        if not extract:
            raise ValueError("match price number failed.")
        result['price'] = extract[0]
    else:
        raise ValueError("price string not find.")
    logger.debug(f"{result['name']} current price: {result['price']}")
    return result


async def fetch_page(url: str, session: ClientSession) -> str:
    """crawl raw page text"""
    resp = await session.get(url)
    resp.raise_for_status()
    logger.debug(f'crawled {url}, response code: {resp.status}')
    return await resp.text()


async def push_wechat(text: str, desc: str) -> None:
    """ push message to wechat use Server酱 """
    # SCKEY需要从环境变量中引用，没有的到Server酱自行申请
    base_url = "https://sc.ftqq.com/{}.send".format(os.getenv('SCKEY'))
    params = {'text': text, 'desp': f"{desc}\n\nAt: {time.ctime()}"}
    timeout = ClientTimeout(total=2 * 30)
    async with ClientSession(timeout=timeout) as session:
        async with session.get(base_url, params=params) as resp:
            resp.raise_for_status()
            # disable check content type
            return await resp.json(content_type=None)


async def worker(item: dict, session: ClientSession) -> str:
    """ fetch page text parser item price and push notification """
    url = f"https://item.m.jd.com/product/{item['id']}.html"
    html = None

    try:
        html = await fetch_page(url, session)
    except (ClientError, HttpProcessingError) as e:
        logger.error(f"fetch page {url} error: {e.status} message: {e.message}")
    except Exception as e:
        logger.error(f"fetch page {url} error: {str(e)}")

    if html:
        try:
            info = parse_price(html)
        except Exception as e:
            logger.error(f"get price failed: {str(e)}")
        else:
            if float(info.get('price')) <= item['target']:
                logger.info(f'item [{info.get("name")}]({url}) prices is {info.get("price")} less than {item["target"]} will send notification')
                text = item['name']
                desc = f'[{info.get("name")}]({url}) 当前价格：{info.get("price")} 小于目标价：{item["target"]}'
                try:
                    ret_info = await push_wechat(text, desc)
                except Excepition as e:
                    logger.error(f"push info failed, error: {str(e)}, or check server酱")
                else:
                    logger.info(f"push return {ret_info}")


async def main() -> None:
    db: List[dict] = [
        {"name": "欧乐B p4000 黑色 旅行装", "id": "100002540995", "target": 350},
        {"name": "欧乐B p4000 白色 旅行装", "id": "100003895610", "target": 350},
        {"name": "欧乐B P4000 蓝色 机皇款", "id": "1834943", "target": 330},
        {"name": "飞利浦 hx6803/02 蓝色", "id": "7045617", "target": 330},
    ]
    timeout = ClientTimeout(total=3 * 30)
    async with ClientSession(timeout=timeout) as session:
        tasks = [worker(i, session) for i in db]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
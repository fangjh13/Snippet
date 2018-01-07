#! -*- coding: utf-8 -*-

headers = {
    'connection': 'keep-alive',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2'
}

user_agent = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'
]

# 代理网页地址和正则，如需增加，手动增加地址和正则
url_and_RegExp = {
    'http://www.66ip.cn/nmtq.php?getnum=512&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip': "([\d\.]+):(\d+)",
    'http://www.xicidaili.com/nn/': "<td>([\d\.]+)</td>\s*<td>(\d+)</td>",
    'http://www.ip3366.net/free/': "<td>([\d\.]+)</td>\s*<td>(\d+)</td>",
    'http://www.proxy360.cn/Region/China': ">\s*([\d\.]+)\s*</span>\s*.*width:50px;\">\s*(\d+)\s*</span>",
    "http://www.data5u.com/free/index.shtml": "<li>([\d\.]+)</li></span>\s+<span style=\"width: 100px;\"><li class=\".*\">(\d+)</li>",
    "http://www.kxdaili.com/": "<tr.*>\s+<td>([\d\.]+)</td>\s+<td>([\d]+)</td>",
    "http://www.mimiip.com/": "<tr>\s+<td>([\d\.]+)</td>\s+<td>(\d+)</td>",
    "http://www.kxdaili.com/ipList/2.html#ip": "<tr.*>\s+<td>([\d\.]+)</td>\s+<td>([\d]+)</td>",
    "http://www.kxdaili.com/ipList/3.html#ip": "<tr.*>\s+<td>([\d\.]+)</td>\s+<td>([\d]+)</td>"
}

# 用于存放数据库的sqlite数据库名，自动生成在当前目录下
database = "ProxyAddress.db"

# 测试代理timeout
timeout = 3

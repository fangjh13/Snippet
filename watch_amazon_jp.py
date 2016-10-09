#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
监视日亚某一商品的价格，达到期望的价格就发送邮件给自己
会在当前目录生成watch_amazon.log日志文件
配合crontab使用
'''

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import codecs
import time
import urllib2
import re

# 发送邮件
def send_mail(body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = formataddr(
        (Header('管理员', 'utf-8').encode(), 'YOUR EMAIL ADDR'))
    msg['To'] = formataddr(
        (Header('qq邮箱', 'utf-8').encode(), 'TO EMAIL'))
    msg['Subject'] = Header('日亚降价提醒', 'utf-8').encode()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('YOUR EMAIL ADDR', 'YOUR EMAIL PASSWORD')
    server.sendmail('YOUR EMAIL ADDR', [
                    'TO EMAIL'], msg.as_string())


# 记录日志
def log(s):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    f = codecs.open('watch_amazon.log', 'a', 'utf-8')
    f.write('[%s] %s\n' % (t, s))
    f.close()


# 查询当前商品价格
def parse_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}
    request = urllib2.Request(url, headers=headers)
    try:
        response = urllib2.urlopen(request)
        # 使用正则筛选出价格
        rule = r'<span id="priceblock_ourprice" class="a-size-medium a-color-price">(.+?)<'
        rs = re.search(rule, response.read()).group(1)
        price_now = int(''.join(rs.split(' ')[1].split(',')))
    except Exception, e:
        log('Error: %s' % e)  # 如果出现错误会记录错误日志
        price_now = 99999999  # 如果程序出错就设定一个最大价格
    return price_now


if __name__ == '__main__':
    # 商品地址
    url = 'https://www.amazon.co.jp/dp/B00M1EC4WA?t=ca_ht_b-22&tag=ca_ht_b-22'
    price = parse_html(url)
    content = '''
    当前价格: %d
    地址： %s''' % (price, url)
    # 小于期望价格就发送邮件
    if price < 1600:
        send_mail(content)
        log('OK This good price: %d' % price)
    else:
        log('PASS price: %d' % price)

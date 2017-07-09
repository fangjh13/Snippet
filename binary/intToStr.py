#!/usr/bin/evn python3
# -*- coding: utf-8 -*-


def intToStr(n):
    ''' 手动实现整数转换成字符串,效果类似str(n) '''
    if n == 0:
        return '0'
    digital = '0123456789'
    rs = ''
    while n > 0:
        # 取末尾数字
        rs = digital[n % 10] + rs
        # 整个数字右移一位
        n = n // 10
    return rs

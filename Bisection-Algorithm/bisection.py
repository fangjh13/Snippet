#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def get_approximate(n, k):
    '''使用二分查找找出n的k次根'''
    # 负数无偶数次根
    if n < 0 and k % 2 == 0:
        return 'Error'
    epsilon = 0.001
    # 保证计算负数、小数、整数的根
    low = min(n, -1)
    high = max(n, 1)
    rs = ((high + low) / 2)
    while abs(rs ** k - n) > epsilon:
        if rs ** k > n:
            high = rs
        else:
            low = rs
        rs = ((high + low) / 2.0)
    return rs

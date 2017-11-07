# -*- coding: utf-8 -*-


import time
from functools import lru_cache


def fib1(n):
    ''' 递归法 '''
    if n < 2:
        return n
    return fib1(n - 2) + fib1(n - 1)


@lru_cache(128)
def fib2(n):
    ''' 使用LRU缓存递归 '''
    if n < 2:
        return n
    return fib1(n - 2) + fib1(n - 1)


def fib3(n):
    ''' 序列解包 '''
    a, b = 0, 1
    for i in range(n):
        b, a = a, a + b
    return a


def fib4(n):
    ''' 使用generator '''
    def hidden():
        a, b = 0, 1
        while True:
            b, a = a, a + b
            yield b
    temp = hidden()
    for i in range(n):
        next(temp)
    return next(temp)


# 测试 可以适当增加n
# 结果会发现fib1是最慢的，fib3和fib4很快fib4可以无限大
n = 10
for f in fib1, fib2, fib3, fib4:
    start = time.time()
    print(f.__name__, f(n), sep=':', end=':')
    print(time.time() - start)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def get_root(n):
	'''使用牛顿拉弗森算法计算平方根'''
	apsilon = 0.001
	guess = n // 2
	while abs(guess**2 - n) >= apsilon:
		guess = guess - (guess**2 - n) / (2 * guess)
	return guess

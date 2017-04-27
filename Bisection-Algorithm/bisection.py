#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def get_approximate(n):
	'''使用二分查找找出n平方根的近似值'''
	epsilon = 0.01
	low = .0
	high = float(n)
	rs = ((high + low) / 2)
	while abs(rs ** 2 - n) > epsilon:
		if rs ** 2 > n:
			high = rs
		else:
			low = rs
		rs = ((high + low) / 2.0)
	return rs

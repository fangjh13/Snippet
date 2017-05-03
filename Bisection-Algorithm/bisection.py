#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def get_approximate(n):
	'''使用二分查找找出n平方根的近似值'''
	epsilon = 0.01
	num_guess = 0
	low = .0
	high = float(n)
	rs = ((high + low) / 2)
	while abs(rs ** 2 - n) > epsilon:
		print('low: ' + str(low) + ' high: ' + str(high))
		num_guess += 1
		if rs ** 2 > n:
			high = rs
		else:
			low = rs
		rs = ((high + low) / 2.0)
	print(num_guess)
	return rs

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def dec2bin(n):
	'''十进制整数转换成二进制 类似与Python内置函数`bin()`'''
	rs = ''
	negative = False
	# 标记是否为负数
	if n < 0:
		negative = True
		n = abs(n)
	if n == 0:
		rs = '0'
	while n > 0:
		# 末尾一定是被2整除之后的余数
		r = n % 2
		rs = str(r) + rs
		n = n // 2
	if negative:
		return '-' + rs
	return rs


def frac2bin(n):
	'''十进制小数转换成二进制小数'''
	negative = False
	if n < 0:
		negative = True
		n = float(abs(n))
	i = 0
	# 找出一个能使这个n乘以2的i次方为整数的数
	while (n * (2 ** i)) % 1 != 0:
		i += 1
	# 把这个整数用上面的函数转换成二进制
	rs = dec2bin(int(n * (2 ** i)))
	# 补前面的零
	for x in range(i - len(rs)):
		rs = '0' + rs
	# 之后要除以刚才乘上的2的i次方，二进制也就是小数点往左移动i位
	if negative:
		return '-' + rs[:-i] + '.' + rs[-i:]
	return rs[:-i] + '.' + rs[-i:]

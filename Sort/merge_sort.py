#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' merge sort '''

import operator


def merge(left, right, compare):
	a, b = 0, 0
	rs = []
	while a < len(left) and b < len(right):
		if compare(left[a], right[b]):
			rs.append(left[a])
			a += 1
		else:
			rs.append(right[b])
			b += 1
	while a < len(left):
		rs.append(left[a])
		a += 1
	while b < len(right):
		rs.append(right[b])
		b += 1
	return rs


def merge_sort(L, compare=operator.lt):
	if len(L) < 2:
		return L[:]
	i = len(L) // 2
	left = merge_sort(L[:i], compare)
	right = merge_sort(L[i:], compare)
	return merge(left, right, compare)


print(merge_sort([1, 3, 4, 2, 55, 3]))

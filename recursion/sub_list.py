#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def gen_sub_list(L):
	''' 生成L列表的所有子列表 '''
	# 递归结束条件,返回一个元素为空列表的列表
	if len(L) == 0:
		return [[]]
	# 获取除了最后一个元素列表的所有子列表
	subs = gen_sub_list(L[:-1])
	# 只有最后一个元素的列表
	last = L[-1:]
	# 初始化一个空列表
	new = []
	for i in subs:
		# 连接最后一个元素的列表
		new.append(i + last)
	return subs + new


print(gen_sub_list([1, 2, 3]))

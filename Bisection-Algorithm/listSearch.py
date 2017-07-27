#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def list_search(L, e):
    ''' 给定一个正序排列好的整数列表L，使用二分查找是否存在元素e '''
    def binary_search(L, e, low, high):
        # 判断是否只有一个元素
        if low == high:
            return L[low] == e
        # 处理下面mid-1 导致low > high的情况
        if low > high:
            return L[low] == e
        mid = (low + high) // 2
        if L[mid] == e:
            return True
        # 注意下面的+1和-1
        if L[mid] < e:
            return binary_search(L, e, mid + 1, high)
        if L[mid] > e:
            return binary_search(L, e, low, mid - 1)
    # 列表为空
    if len(L) == 0:
        return False
    return binary_search(L, e, 0, len(L) - 1)

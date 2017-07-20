#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' selection sort '''


def sel_sort(L):
    for i in range(len(L) - 1):
        small_index = i
        small_value = L[i]
        j = i + 1
        while j < len(L):
            if L[j] < small_value:
                small_index = j
                small_value = L[j]
            j += 1
        temp = L[i]
        L[i] = L[small_index]
        L[small_index] = temp
    return L


print(sel_sort([1, 34, 4, 5, 1, 1, 4]))

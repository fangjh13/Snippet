#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class SpiralMatrix(object):
    '''
    旋转矩阵的一个解法
    思路：数字从左上角顺时针也就是`右下左上`的方向依次向内旋转
         首先定义一个值为None的二维数组(N*N)框架用于填充数字
         遇到边界和已填充了的数字的位置改变方向
    '''

    def __init__(self, N):
        # 定义一个二维数组
        self.matrix = [[None for y in range(N)] for x in range(N)]
        # 横坐标
        self.row = 0
        # 纵坐标
        self.col = 0
        # 边界
        self.border = N
        # 是否需要改变方向的标记
        self.mark = 0

    def change_direction(self, mark):
        '''根据`mark`返回特定方向的坐标'''
        direction = [
            # 右
            [self.row, self.col + 1],
            # 下
            [self.row + 1, self.col],
            # 左
            [self.row, self.col - 1],
            # 上
            [self.row - 1, self.col]
        ]
        return direction[mark % 4]

    def next_coordinate(self):
        '''更新下一坐标点'''
        coordinate = self.change_direction(self.mark)
        # 判断是否到达边界
        if self.border not in coordinate:
            # 判断此位置是否被填充
            if self.matrix[coordinate[0]][coordinate[1]] is None:
                # 更新位置
                self.row, self.col = coordinate
                return
        # 否则标记改变方向
        self.mark += 1
        return self.next_coordinate()

    def exec(self):
        '''按坐标依次赋值到定义的数组'''
        for i in range(1, self.border ** 2 + 1):
            self.matrix[self.row][self.col] = i
            # 到最后一个坐标退出循环
            if i == self.border ** 2:
                break
            self.next_coordinate()

        # 打印结果
        for x in self.matrix:
            for y in x:
                print('{0:^{1}}'.format(
                    y, len(str(self.border**2)) + 3), end=' ')
            print()


spiral = SpiralMatrix(5)
spiral.exec()

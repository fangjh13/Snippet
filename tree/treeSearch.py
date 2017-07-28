#!/usr/bin/evn python3
# -*- coding: utf-8 -*-


class BinaryTree(object):
    def __init__(self, value):
        self.value = value
        self.left_branch = None
        self.right_branch = None
        self.parent = None

    def set_left_branch(self, node):
        self.left_branch = node

    def set_right_branch(self, node):
        self.right_branch = node

    def set_parent(self, node):
        self.parent = node

    def get_value(self):
        return self.value

    def get_left_branch(self):
        return self.left_branch

    def get_right_branch(self):
        return self.right_branch

    def get_parent(self):
        return self.parent

    def __str__(self):
        return self.value


def dfs_binary(root, fc):
    ''' Depth first serach '''
    # LIFO
    stack = [root]
    while len(stack) > 0:
        # print search path
        print(stack[0].get_value())
        if fc(stack[0]):
            return True
        temp = stack.pop(0)
        if temp.get_right_branch():
            stack.insert(0, temp.get_right_branch())
        if temp.get_left_branch():
            stack.insert(0, temp.get_left_branch())
    return False


n5 = BinaryTree(5)
n2 = BinaryTree(2)
n1 = BinaryTree(1)
n4 = BinaryTree(4)
n8 = BinaryTree(8)
n6 = BinaryTree(6)
n7 = BinaryTree(7)
n3 = BinaryTree(3)

n5.set_left_branch(n2)
n2.set_parent(n5)
n5.set_right_branch(n8)
n8.set_parent(n5)
n2.set_left_branch(n1)
n1.set_parent(n2)
n2.set_right_branch(n4)
n4.set_parent(n2)
n4.set_left_branch(n3)
n3.set_parent(n4)
n8.set_left_branch(n6)
n6.set_parent(n8)
n6.set_right_branch(n7)
n7.set_parent(n6)

print(dfs_binary(n5, lambda x: x.get_value() == 6))


def bfs_binary(root, fc):
    ''' Breadth first search '''
    # FIFO
    queue = [root]
    while len(queue) > 0:
        # print search path
        print(queue[0].get_value())
        if fc(queue[0]):
            return True
        temp = queue.pop(0)
        if temp.get_left_branch():
            queue.append(temp.get_left_branch())
        if temp.get_right_branch():
            queue.append(temp.get_right_branch())
    return False


print(bfs_binary(n5, lambda x: x.get_value() == 6))


def dfs_binary_ordered(root, fc, ltfc):
    ''' Depth first ordered search '''
    stack = [root]
    while len(stack) > 0:
        print(stack[0].get_value())
        if fc(stack[0]):
            return True
        elif ltfc(stack[0]):
            temp = stack.pop(0)
            if temp.get_right_branch():
                stack.insert(0, temp.get_right_branch())
        else:
            temp = stack.pop(0)
            if temp.get_left_branch():
                stack.insert(0, temp.get_left_branch())
    return False


print(dfs_binary_ordered(n5, lambda x: x.get_value() == 6,
    lambda x: x.get_value() < 6))


def bfs_binary_ordered(root, fc, ltfc):
    queue = [root]
    while len(queue) > 0:
        print(queue[0].get_value())
        if fc(queue[0]):
            return True
        elif ltfc(queue[0]):
            temp = queue.pop(0)
            if temp.get_right_branch():
                queue.append(temp.get_right_branch())
        else:
            temp = queue.pop(0)
            if temp.get_left_branch():
                queue.append(temp.get_left_branch())
    return False

print(bfs_binary_ordered(n5, lambda x: x.get_value() == 6,
    lambda x: x.get_value() < 6))





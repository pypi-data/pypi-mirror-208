#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/8/12 10:40
# @Author  : 熊利宏
# @project : 多线程类
# @Email   : xionglihong@163.com
# @File    : xthread.py
# @IDE     : PyCharm
# @REMARKS : 多线程类

import threading


# 多线程基类
class MyThread(threading.Thread):

    def __init__(self, func, args=None):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            # 如果子线程不使用join方法，此处可能会报没有self.result的错误
            return self.result
        except Exception:
            return None


# 多线程
def xthreading(*args):
    """
    # 函数一
    def function_1(a, b, c):
    time.sleep(1)
    return a * 2, b * 2, c * 2

    # 函数二
    def function_2(a, b):
        time.sleep(1)
        return a * 2, b * 2

    # 函数三
    def function_3(a):
        time.sleep(1)
        return a * 2

    # 函数四
    def function_4():
        time.sleep(1)
        return 0

    # 调用方法
    xthreading([function_1, 1, 1, 1], [function_2, 2, 2], [function_3, 2], [function_4])

    # 返回结果
    [(2, 2, 2), (4, 4), 4, 0]
    """

    # 初始化返回值
    result = []

    # 临时列表
    li = []
    for i in args:
        t = MyThread(i[0], args=i[1:])
        li.append(t)
        t.start()

    for t in li:
        # 一定要join，不然主线程比子线程跑的快，会拿不到结果
        t.join()
        result.append(t.get_result())

    return result

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 16:28
# @Author  : 熊利宏
# @project : 列表基础模块
# @Email   : xionglihong@163.com
# @File    : dispose.py
# @IDE     : PyCharm
# @REMARKS : 列表基础模块

# 科学计算库
import numpy
import pandas


# 列表基础处理
class Dispose(object):
    """
    列表基础处理
    """

    def __init__(self, mark):
        self.__mark = mark

    # 值的频率
    def values_count(self, *args):
        """
        统计值得出现次数（字典）
        """
        return pandas.value_counts(self.__mark).to_dict()

    # 字典列表值替换
    def dict_to_value(self, *args, **kwargs):
        """
        1.字典型列表，值整体替换
        2.要求传入参数格式为 [{"id": None, "name": "wuhan"}, {"id": 5, "name": "中国"}, {"id": 25, "name": "上号"}, {"id": 5, "name": "测试"}]
        3.这种形状的参数即可，比如可以传入 django 的 QuerySet 等
        4.参数：
            1.需要替换的对象
            2.kwargs["rules"] 要求元祖，比如 ((None, ''), (45, 47)))
        """
        target = self.__mark

        # 把对象转换为pandas对象
        result = pandas.DataFrame(target)
        # 进行值替换
        for key in kwargs["rules"]:
            if key[0] is None:
                result = result.where(result.notnull(), ''.format(key[1]))
            else:
                result = result.where(result != key[0], key[1])

        # 把pandas格式转换为列表型字典
        return result.to_dict("records")

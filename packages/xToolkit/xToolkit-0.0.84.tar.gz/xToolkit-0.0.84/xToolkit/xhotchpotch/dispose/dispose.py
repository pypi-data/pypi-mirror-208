#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 16:28
# @Author  : 熊利宏
# @project : 一些扩展功能，大杂烩
# @Email   : xionglihong@163.com
# @File    : dispose.py
# @IDE     : PyCharm
# @REMARKS : 大杂烩基础模块

from math import sin, asin, cos, radians, fabs, sqrt


# 经纬度二点距离
class DistanceHav:
    """
    计算经纬度二点距离
    """

    def __init__(self):
        self.earth_radius = 6371  # 地球平均半径，6371km

    @staticmethod
    def hav(theta):
        s = sin(theta / 2)
        return s * s

    def get_distance_hav(self, start, end):
        """
        用haversine公式计算球面两点间的距离

        start和end的格式为元祖
        """

        if not (isinstance(start, tuple) and isinstance(end, tuple)):
            return "start或end 格式错误，必须为元祖格式"

        # 经纬度转换成弧度
        lat0, lat1, lng0, lng1 = radians(start[0]), radians(end[0]), radians(start[1]), radians(end[1])

        h = self.hav(fabs(lat0 - lat1)) + cos(lat0) * cos(lat1) * self.hav(fabs(lng0 - lng1))
        distance = 2 * self.earth_radius * asin(sqrt(h))

        # 单位为m
        return distance * 1000


# 大杂烩基础处理
class Dispose(object):
    """
    大杂烩基础处理
    """

    def __init__(self, mark=None):
        self.__mark = mark

    # 经纬度二点距离
    @staticmethod
    def distance_hav(*args):
        """
        传值要求元祖，参数格式：（纬度，经度）,(3.6546879, 4.5879546), (6.5879546, 5.1123654)
        """
        dh = DistanceHav()
        start, end = args[0], args[1]
        return dh.get_distance_hav(start, end)

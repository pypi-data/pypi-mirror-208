#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/07/06 16:26
# @Author  : 熊利宏
# @project : 一些扩展功能，大杂烩
# @Email   : xionglihong@163.com
# @File    : api.py
# @IDE     : PyCharm
# @REMARKS : 大杂烩的对外接口

# 总基类
from ..xtoolkit import XToolkit

# 大杂烩基础功能
from .dispose.dispose import Dispose


# 大杂烩基类
class XHotchpotch(XToolkit):

    def __init__(self, dispose=Dispose):
        # 继承父类的init方法
        super(XHotchpotch, self).__init__()

        # 基础处理
        self.__disposes = dispose

    # 经纬度二点距离
    def distance_hav(self, *args):
        """
        经纬度二点距离
        传值要求元祖，参数格式：（纬度，经度）,(3.6546879, 4.5879546), (6.5879546, 5.1123654)
        """
        return self.__disposes.distance_hav(*args)

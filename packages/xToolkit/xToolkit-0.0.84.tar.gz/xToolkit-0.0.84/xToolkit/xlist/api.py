#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 16:26
# @Author  : 熊利宏
# @project : 列表模块
# @Email   : xionglihong@163.com
# @File    : api.py
# @IDE     : PyCharm
# @REMARKS : 列表模块的对外接口

# 总基类
from ..xtoolkit import XToolkit

# 列表基础功能
from .dispose.dispose import Dispose


# 字符串基类
class XLise(XToolkit):

    def __init__(self, dispose=Dispose):
        # 继承父类的init方法
        super(XLise, self).__init__()

        # 基础处理
        self.__disposes = dispose

    # 基本功能
    def basics(self, *args, **kwargs):
        """
        基本功能
        """
        if len(args) == 1:
            mark = args[0]
            return self.__disposes(mark)
        else:
            raise ValueError("basics() 方法暂时只支持一个参数并且不能为空")

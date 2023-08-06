#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/15 17:41
# @Author  : 熊利宏
# @project : 文件模块
# @Email   : xionglihong@163.com
# @File    : api.py
# @IDE     : PyCharm
# @REMARKS : 文件模块的对外接口

# 总基类
from ..xtoolkit import XToolkit

# 文件读取类
from ..xfile.dispose.dispose import FileRead


# 字符串基类
class XFile(XToolkit):

    def __init__(self, reads=FileRead):
        # 继承父类的init方法
        super(XFile, self).__init__()
        # self.judge->类型判断

        # 读取文件
        self.__read = reads

    # 读取文件
    def read(self, *args):
        """
        读取文件，args第一个参数为要读取文件的地址
        """
        read_file = args[0]

        if read_file:
            return self.__read(read_file)
        else:
            raise ValueError("需要读取的文件不能为空地址（空二进制对象）")

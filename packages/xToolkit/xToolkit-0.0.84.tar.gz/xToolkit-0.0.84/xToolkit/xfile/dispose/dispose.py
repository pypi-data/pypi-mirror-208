#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/15 17:47
# @Author  : 熊利宏
# @project : 文件模块
# @Email   : xionglihong@163.com
# @File    : 文件模块.py
# @IDE     : PyCharm
# @REMARKS : 文件模块的基础处理

# excel 读取库
import xlrd

# 时间库
from datetime import datetime

# 系统文件库
import os.path


# 文件读取
class FileRead(object):
    """
    进行文件读取
    """

    def __init__(self, mark):
        self.__mark = mark

    # excel转dict
    def excel_to_dict(self, *args, **kwargs):
        """
        excel转dict

        1.传来的文件可以是文件路径，也可以是二进制文件
        2.传来的可以是二进制文件，这里以django接收前端传来文件为例：
            接收用 request.FILES.get("fileName", None) 传入 my_file 即可

        kwargs接收的参数有:
            sheet索引，0代表第一个表，1代表第二个表，默认0
            max表格最大的行数，默认2000行
            min表格最小的行数，默认1行
            title 表头(用于表头校验)
        """
        # excel 文件
        excel_file = self.__mark
        # sheet 索引
        _sheet = kwargs.get("sheet", 0)
        # max 最大条数
        _max = kwargs.get("max", 2000)
        # min 最小条数
        _min = kwargs.get("min", 0)
        # 表头 传入类型为列表list
        _title = kwargs.get("title", [])

        if isinstance(excel_file, str):
            # 判断路径是否正确
            if not os.path.exists(excel_file):
                return {"code": "0001", "msg": "文件路径错误", "data": None}

            # 判断文件类型是否正确
            if os.path.splitext(excel_file)[1] not in [".xlsx", ".xls"]:
                return {"code": "0001", "msg": "只支持后缀为.xlsx和.xls的文件", "data": None}

        # 判断是否为文件路径
        if os.path.exists(excel_file):
            workbook = xlrd.open_workbook(excel_file)
        else:
            # 上传的文件不保存，直接在内存中读取文件
            workbook = xlrd.open_workbook(filename=excel_file.name, file_contents=excel_file.read())

        # 根据sheet索引或者名称获取sheet内容
        data_sheet = workbook.sheets()[_sheet]
        # 获取sheet名称，行数，列数据
        sheet_name = data_sheet.name
        sheet_nrows = data_sheet.nrows
        sheet_ncols = data_sheet.ncols

        # 校验表头
        if _title:
            title = []
            for key in range(sheet_ncols):
                title.append(data_sheet.cell_value(0, key))

            for key in range(len(kwargs.get("title"))):
                if title[key] != kwargs.get("title")[key]:
                    return {
                        "code": "0001",
                        "msg": "表头第 {} 列错误，错误值为 {} 应该为 {}".format(key + 1, title[key], kwargs.get("title")[key]),
                        "data": {"data": None}
                    }

        # 文件记录不得大于2000条
        if sheet_nrows > _max:
            return {"code": "0001", "msg": "文件记录大于{}条，请修改max值".format(_max), "data": None}

        # 判断是否为空数据
        if sheet_nrows <= _min:
            return {"code": "0001", "msg": "空数据表格,停止导入", "data": None}

        # excel转dict
        get_data = []
        for i in range(1, sheet_nrows):
            # 定义一个空字典
            sheet_data = {}
            for j in range(sheet_ncols):
                # 获取单元格数据类型
                c_type = data_sheet.cell(i, j).ctype
                # 获取单元格数据
                c_cell = data_sheet.cell_value(i, j)
                if c_type == 2 and c_cell % 1 == 0:  # 如果是整形
                    c_cell = int(c_cell)
                elif c_type == 3:
                    # 转成datetime对象
                    c_cell = datetime(*xlrd.xldate_as_tuple(c_cell, 0)).strftime('%Y-%m-%d %H:%M:%S')
                elif c_type == 4:
                    c_cell = True if c_cell == 1 else False
                sheet_data[data_sheet.row_values(0)[j]] = c_cell
                # 循环每一个有效的单元格，将字段与值对应存储到字典中
                # 字典的key就是excel表中每列第一行的字段
                # sheet_data[self.keys[j]] = self.table.row_values(i)[j]
            # 再将字典追加到列表中
            get_data.append(sheet_data)
        # 返回从excel中获取到的数据：以列表存字典的形式返回
        return get_data

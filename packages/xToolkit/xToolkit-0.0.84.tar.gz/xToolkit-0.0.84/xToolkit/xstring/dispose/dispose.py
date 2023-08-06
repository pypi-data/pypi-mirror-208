#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/19 7:07
# @Author  : 熊利宏
# @project : 字符串处理模块
# @Email   : xionglihong@163.com
# @File    : dispose.py
# @IDE     : PyCharm
# @REMARKS : 字符串的一些常用处理

from __future__ import unicode_literals

# 正则表达式
import re

# emoji 表情处理
from emoji import emojize, demojize

# 中文分词
import jieba

# 数字精度
from decimal import Decimal

# 对象转换
import ast
import json

# 字符串格式校验
from ..check.check import CheckData

# 字符串公共功能
from ..xstring import BasicsFunction


# 字符串处理
class Dispose(object):
    """
    字符串的一些常用处理
    """

    def __init__(self, mark):
        self.__mark = mark

    # 获取身份证信息
    def get_identity_card(self, *args):
        """
        提供中国大陆身份证验证，暂时只支持效验18位身份证

        mold表示消息类型，为选填
            为空表示不输出错误或正确消息，只输出 True 或者 False，表示格式正确或者错误
            True 输出正确消息，包括出生年月，性别基础信息
            False 输出完整身份证信息，包括市县，出生年月日，性别等信息，但速度比较慢，因为是进行的网络查询
        """
        return BasicsFunction(self.__mark).identity_card(args[0])

    # 字符串分割
    def split(self, *args):
        """
        重写系统的split，使其可以进行多个分割符号分割字符串
        """
        # 分割标识列表
        sign = args[0]

        # 分隔符集合必须为列表，并且不能为空
        if not isinstance(sign, list):
            return {"code": "0001", "msg": "分割标识数据类型必须为列表", "data": {"data": None}}

        signs = ""
        for key in sign:
            signs += r"\{}".format(key)

        signs = r"[{}]".format(signs)

        return re.split(signs, self.__mark)

    # 字符串过滤
    def strip(self, *args, **kwargs):
        """
        重写系统的strip，使其可以进行多字符串过滤
        默认去掉全部空格，包括收尾和字符串中间的
        """
        # 过滤标识
        method = args[0] if args else [" "]

        returned = self.__mark
        for key in method:
            returned = returned.replace(key, "")

        return returned

    # 字符串转emoji表情
    def string_to_emoji(self, *args, **kwargs):
        """
        把字符串转换为emoji表情
        """
        # 效验数据
        if not self.__mark:
            raise ValueError("转换的字符串不能为空")

        return emojize(self.__mark)

    # emoji表情转字符串
    def emoji_to_string(self, *args, **kwargs):
        """
        emoji表情转字符串
        """
        # 效验数据
        if not self.__mark:
            raise ValueError("转换的字符串不能为空")

        return demojize(self.__mark)

    # 中文分词
    def part(self, *args, **kwargs):
        """
        分词对象 中国人民解放军海军工程大学

        全模式：把文本中所有可能的词语都扫描出来，有冗余 cut_all=True
            ['中国', '中国人民解放军', '中国人民解放军海军', '国人', '人民', '人民解放军', '解放', '解放军', '海军', '海军工程大学', '军工', '工程', '大学']


        精确模式：把文本精确的切分开，不存在冗余单词 cut_all=False
            ['中国人民解放军', '海军工程大学']

        默认为精确模式
        """
        cut_all = True if kwargs.get("cut_all", None) else False
        return jieba.lcut(self.__mark, cut_all=cut_all)

    # 金额人性化
    def humanized_amount(self, *args, **kwargs):
        """
        金额人性化,保留二位小数，再进行人性化显示
        """
        if not CheckData(self.__mark).is_int_or_float:
            return {"code": "0001", "msg": "必须传入数字", "data": None}
        else:
            figure = str(float(self.__mark))

        # 分解成整数部分和小数部分
        integer, decimals = figure.split(".")

        # 小数部分
        decimals = "0." + decimals
        decimals = Decimal(decimals).quantize(Decimal('0.00'))

        # 整数部分（人性化显示）
        integer = "{:,}".format(float(integer))

        # 合并整数和小时部分
        figure = integer.split(".")[0] + "." + str(decimals).split(".")[1]

        return figure

    # 对象转字符串
    def objects_to_string(self):
        """
        对象字符串转对象,比如把 dict的 {"name": "熊利宏", "age": 32} 的字典对象转换为 字符串的 "{"name": "熊利宏", "age": 32}"
        """
        return json.dumps(self.__mark)

    # 字符串转对象
    def string_to_objects(self):
        """
        对象字符串转对象,比如把 "{'name': '熊利宏', 'age': 32}" 的字符串转换为 dict {"name": "熊利宏", "age": 32}
        """
        return ast.literal_eval(self.__mark)

    # 字节串转字符串
    def bytes_to_string(self, *args, **kwargs):
        """
        字节串（bytes）转 字符串（string）
        """
        return bytes.decode(self.__mark, *args, **kwargs)

    # 字符串转字节串
    def string_to_bytes(self, *args, **kwargs):
        """
        字符串（string）转 字节串（bytes）
        """
        return str.encode(self.__mark, *args, **kwargs)

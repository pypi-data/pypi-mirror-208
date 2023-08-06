#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/16 20:52
# @Author  : 熊利宏
# @project : 字符串验证模块
# @Email   : xionglihong@163.com
# @File    : xstring.py
# @IDE     : PyCharm
# @REMARKS : 字符串验证功能
import ast
import json
import re

# 字符串公共功能
from xToolkit.xstring.xstring import BasicsFunction

# 基类格式判断
from xToolkit.xtoolkit.judgement import JudgeType


# 校验模块
class CheckData(object):

    def __init__(self, mark):
        self.__mark = mark

        # 基类格式判断
        self.judge = JudgeType

    # 正则表达式验证方法
    def __regular_expression(self, expression):
        """
        正则表达式验证方法
        """
        # 需要验证的字符串
        string = self.__mark

        if re.match(expression, str(string)):
            return True
        else:
            return False

    # 车牌号
    @property
    def is_car_number(self):
        """
        提供中国大陆车牌号验证

        表达式校验的规则：
            常规车牌号：省份+地区代码+五位数字/大写英文字母（序号位）如：粤B12345。 
                1. 序号位不存在字母I和O防止1、0混淆 
                2. 省份范围：京、津、沪、渝、冀、豫、云、辽、黑、湘、皖、鲁、新、苏、浙、赣、鄂、桂、甘、晋、蒙、陕、吉、闽、贵、粤、青、藏、川、宁、琼。 
                3. 地区代码O为省级公安厅专用车牌 
                4. 地区代码U为省级政府专用车牌 
                5. 地区代码中暂无I

            新能源车牌号：省份简称（1位汉字）+发牌机关代号（1位字母）+序号（6位） 
                1. 小型新能源汽车号牌（序号）的第一位必须使用字母D、F（D代表纯电动新能源汽车，F代表非纯电动新能源汽车），第二位可以使用字母或者数字，后四位必须使用数字。 
                2. 大型新能源汽车号牌（序号）的第六位必须使用字母D、F（D代表纯电动新能源汽车，F代表非纯电动新能源汽车），前五位必须使用数字。 
                3. 序号中英文字母I和O不能使用。 
                4. 省份范围同常规车牌号 
                5. 发牌机关代码暂无I

            警车车牌：车牌最后汉字为警字 
                1. 省份+地区代码+4位数字+警（川A0001警） 
                2. 省份+地区代码+字母+3位数字（川AA001警）字母可选项包括（A、B、C、D） 
                3. 省份范围同常规车牌号 
                4. 地区代码没有I 
                5. 地区代码为O时代表为省级公安厅专用车牌

            领事馆车牌：车牌中包括“使”或“领”字 
                1. 大使馆：三位国家代码（数字）+三位 车辆编号（数字）+使 
                2. 领事馆：省份简称+地区代码+四位 车辆编号（数字）+领（省份与地区代码可选范围包括：沪A、粤A、川A、云A、桂A、鄂A、闽D、鲁B、陕A、蒙A、蒙E、蒙H、藏A、黑A、辽A、渝A）

            武警车牌：车牌开头包括WJ 
                1. 武警总部车牌：WJ+•（中间点）+四个数字+数字或字母 
                2. 武警地方车牌：WJ+省份简称+四位数字+数字或字母 
                3. 省份范围同常规车牌号 
                4. 其中字母包括（T D S H B X J）

            军用车牌：字头+字头号 +序号组成。 
                1. 字头：大写字母汉语拼音字母，字母包括（VKHBSLJNGCE） 
                2. 字头号：大写英文字母，字母包括（A-D,J-P,R-T,V,Y） 
                3. 序号：5位数字
        """
        expression = "^(([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z](([0-9]{5}[DF])|([DF]([A-HJ-NP-Z0-9])[0-9]{4})))" \
                     "|([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{4}[A-HJ-NP-Z0-9挂学警港澳使领]))$"

        return self.__regular_expression(expression)

    # 身份证
    @property
    def is_identity_card(self):
        """
        提供中国大陆身份证验证，暂时只支持效验18位身份证
        """
        return BasicsFunction(self.__mark).identity_card()

    # 整形或浮点型
    @property
    def is_int_or_float(self):
        return self.judge.is_timestamp(self.__mark)

    # 整形
    @property
    def is_int(self):
        return self.judge.is_int(self.__mark)

    # 时间字符串
    @property
    def is_datetime_string(self):
        return self.judge.is_datetime_string(self.__mark)

    # URL地址
    @property
    def is_url(self):
        expression = "(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
        return self.__regular_expression(expression)

    # 手机号
    @property
    def is_phone(self):
        """
        第一位为1，一共11位数字几个
        """
        expression = "^1\\d{10}$"
        return self.__regular_expression(expression)

    # 银行卡
    @property
    def is_bank_number(self):
        """
        第一位不能为0,并且13到19位数字
        """
        expression = "^[1-9]\\d{12,18}$"
        return self.__regular_expression(expression)

    # 用户姓名
    @property
    def is_user_name(self):
        """
        姓名要求为2-4个中文
        """
        expression = "^[\u4e00-\u9fa5]{2,4}$"
        return self.__regular_expression(expression)

    # 密码
    @property
    def is_user_password(self):
        """
        包含6-18位字符，必须包含字母与数字，可以包含特殊字符
        """
        expression = "^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z\\W]{6,18}$"
        return self.__regular_expression(expression)

    # 邮箱
    @property
    def is_mailbox(self):
        """
        第一种：只允许英文字母、数字、下划线、英文句号、以及中划线组成
        第二种：名称允许汉字、字母、数字，域名只允许英文域名
        二种中任何一种即可
        """
        expression = "{}|{}".format(
            "^([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)+)",
            "([A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)+)$"
        )

        return self.__regular_expression(expression)

    # 工号
    @property
    def is_job(self):
        """
        工号格式为 4个大写字母+8位数字
        """
        expression = "^[A-Z]{4}\d{8}"
        return self.__regular_expression(expression)

    # ip地址
    @property
    def ip_address(self):
        """
        ip地址,ip4
        """
        expression = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return self.__regular_expression(expression)


# 高级校验模块
class FormativeCheck(CheckData):
    """
    高级校验模块

    接收用户的参数并进行校验

    parameter 为需要校验的参数名称
    is_blank 是否可以为空，如果可以为空，不进行规则校验，直接返回空字符串，如果用户传了，就进行规则校验
    rule 为正则表达式代号
    """

    def __init__(self, parameter):
        super().__init__(parameter)
        self.parameter = parameter
        self.rule_usual_list = [
            "is_car_number", "is_identity_card", "is_int_or_float", "is_int",  # 车牌号,身份证,整形或浮点型,整形
            "is_datetime_string", "is_url", "is_phone", "is_bank_number",  # 时间字符串,url地址,手机号,银行卡
            "is_user_name", "is_user_password", "is_mailbox", "ip_address",  # 用户姓名,密码,邮箱,ip地址
        ]
        self.rule_list_list = ["{}_list".format(key) for key in self.rule_usual_list]

    # 正则校验
    def regular(self, rule, **kwargs):
        """
        正则校验
        """
        if rule in self.rule_usual_list:
            return eval("self.{}".format(rule))
        # JSON
        elif rule == "is_json":
            # noinspection PyBroadException
            try:
                # 不能用ast，因为ast的处理能力太强，各种格式都不报错，无法触发tey
                resource = json.loads(self.parameter)
                return True if isinstance(resource, dict) else False
            except Exception:
                return False
        # 枚举
        elif rule == "is_choices":
            is_true = False

            if self.parameter in kwargs.get("choices"):
                is_true = True

            return is_true
        # 整形(浮点)列表，整形列表，URL列表,任意
        elif rule in (self.rule_list_list + ["is_json_list", "is_casual_list"]):
            # noinspection PyBroadException
            try:
                resource = json.loads(self.parameter)

                if isinstance(resource, list):
                    is_true = True

                    for key in resource:
                        super().__init__(key)

                        if rule in self.rule_list_list and not eval("self.{}".format(rule.replace("_list", ""))):
                            is_true = False
                        if rule == "is_json_list" and not isinstance(key, dict):
                            is_true = False
                        if rule == "is_casual_list":
                            is_true = True

                    return is_true
                else:
                    return False
            except Exception:
                return False

        # 任意
        elif rule == "casual":
            return True
        else:
            return False

    # 校验逻辑
    def regular_logic(self, rule, **kwargs):
        """
        校验逻辑
        """
        choices, regular = kwargs["choices"], kwargs["regular"]

        tem_list = ["is_json", "is_json_list", "is_casual_list"]
        tem_list += self.rule_list_list

        # 如果用户自定义正则表达式，就用用户自定义的正则表达式
        if regular:
            if re.match(regular, str(self.parameter)):
                return self.parameter
            else:
                return False
        else:
            if self.regular(rule, choices=choices) is not False:
                if rule in tem_list:
                    return json.loads(self.parameter)
                elif rule == "is_int":
                    return int(self.parameter)
                else:
                    return self.parameter
            else:
                return False

    def introduction(self, **kwargs):
        """
        is_blank 如果为True代表如果用户传值，就进行校验，如果传空，值就为空
        """
        rule = kwargs["rule"] if kwargs.get("rule") else None
        is_blank = kwargs["is_blank"] if kwargs.get("is_blank") else False
        choices = kwargs["choices"] if kwargs.get("choices") else None
        max_length = kwargs["max_length"] if kwargs.get("max_length") else None  # 最大字符串长度
        regular = kwargs["regular"] if kwargs.get("regular") else None  # 自定义正则表达式

        result = False
        # 如果长度超出最大长度
        if max_length:
            if len(self.parameter) > max_length:
                return result

        if is_blank is True:
            if self.parameter:
                result = self.regular_logic(rule, choices=choices, regular=regular)
            else:
                result = self.parameter
        else:
            result = self.regular_logic(rule, choices=choices, regular=regular)

        return result

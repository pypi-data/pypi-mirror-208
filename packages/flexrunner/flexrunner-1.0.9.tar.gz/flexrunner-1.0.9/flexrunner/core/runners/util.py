#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:util
@time:2023/02/25
@email:tao.xu2008@outlook.com
@description:
"""
import os
import re
import ast
from loguru import logger

import allure


def get_testcase_id_by_func_name(func_name):
    """
    从测试用例方法名中获取用例ID，只取一个ID值
    :param func_name:
    :return:
    """
    cid = re.findall(r"-?[0-9]\d*", func_name)
    return str(int(cid[0]) if cid else 0)


if __name__ == '__main__':
    pass

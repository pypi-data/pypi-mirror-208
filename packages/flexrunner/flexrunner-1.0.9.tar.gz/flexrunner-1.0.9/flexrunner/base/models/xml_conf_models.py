#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:xml_conf_model
@time:2023/02/25
@email:tao.xu2008@outlook.com
@description: 测试配置文件 xml解析数据模型
"""
from typing import Dict, List, Text, Union, Any

from pydantic import BaseModel, HttpUrl

Url = Union[HttpUrl, Text]


# 输入参数 - 环境 （cf_xml.py解析）
class TestEnv(BaseModel):
    """测试环境配置 - 数据模型"""
    description: Text = ''
    node_list: List[Dict[Text, Text]] = []
    endpoint: Text = ""
    endpoint_user: Text = ""
    endpoint_pass: Text = ""
    params: Dict[Text, Any] = {}
    web_url: Url
    web_user: Text = ""
    web_pass: Text = ""


# 输入参数 - 测试床 （cf_xml.py解析）
class Testbed(BaseModel):
    """测试床配置 - 数据模型"""
    xml_path: Text  # xml配置文件路径
    name: Text = ''
    description: Text = ''
    env_list: List[TestEnv]


# 输入参数 - 测试集 （cf_xml.py解析）
class TestSet(BaseModel):
    """测试集配置 - 数据模型"""
    xml_path: Text  # xml配置文件路径
    description: Text = ''
    case_list: List[Dict]


# 输入参数 - 配置 （cf_xml.py解析）
class TestConf(BaseModel):
    """测试执行配置 - 数据模型"""
    project: Text
    base_path: Text
    full_path: Text
    description: Text = ''
    testbed: Testbed
    test_set_list: List[TestSet]


if __name__ == '__main__':
    pass

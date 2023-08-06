#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:platform_models
@time:2023/02/25
@email:tao.xu2008@outlook.com
@description:
"""
from enum import Enum
from typing import Text
from pydantic import BaseModel


# 测试平台信息
class PlatformInfo(BaseModel):
    runner_name: Text
    runner_version: Text
    python_version: Text
    platform: Text


# 数据库连接信息
class DBInfo(BaseModel):
    """数据库连接信息"""
    ENGINE: Text = "django.db.backends.sqlite3",  # django.db.backends.mysql
    NAME: Text = "",  # sqlite3: sqlite3.db path, mysql:database_name
    USER: Text = "",
    PASSWORD: Text = "",
    HOST: Text = "",
    PORT: int = 0,


# 浏览器类型 - 枚举
class WebDriverTypeEnum(Text, Enum):
    """Web测试浏览器类型枚举"""
    CHROME = 'chrome'
    FIREFOX = 'firefox'
    IE = 'ie'
    EDGE = 'edge'


# 测试步骤类型 - 枚举
class StepTypeEnum(Text, Enum):
    """测试步骤类型枚举"""
    UNKNOWN = ''  # 未知、未定义
    WEB = 'WEB'  # Web UI 测试
    API = 'API'  # rest_api 测试
    SDK = 'SDK'  # SDK 调用
    CMD = 'CMD'  # 系统命令执行
    CASE_REF = 'CASE_REF'  # 步骤为测试用例引用

    # 为项目特别定义类型
    MC = 'MC'  # demo项目MinIO客户端 MC命令执行


if __name__ == '__main__':
    pass

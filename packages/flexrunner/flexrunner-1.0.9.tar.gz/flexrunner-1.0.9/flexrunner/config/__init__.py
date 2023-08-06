#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 全局配置，及配置文件读写方法。
"""
from flexrunner.config.globals import *
from flexrunner.config.cf_xml import ConfigXml
from flexrunner.config.cf_yaml import read_yaml
from flexrunner.config.cf_ini import ConfigIni, read_ini

__all__ = [
    "VERSION", "AUTHOR",
    # 基本方法
    "read_yaml", "ConfigIni", "ConfigXml",
    # 全局内存变量-读写
    "set_global_value", "get_global_value", "get_global_dict",
    # 环境变量-读写
    "set_os_environ", "unset_os_environ", "get_os_environment",
    # 全局常量
    "CWD", "BASE_DIR", "LOG_DIR", "REPORT_DIR",  # 全局路径 dir
    "TIME_STR",  # 时间戳
]


if __name__ == '__main__':
    pass

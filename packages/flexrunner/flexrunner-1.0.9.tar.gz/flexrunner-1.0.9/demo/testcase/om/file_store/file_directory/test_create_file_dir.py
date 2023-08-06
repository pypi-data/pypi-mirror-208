#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_create_file_dir
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from flexrunner import CaseMetaClass


@allure.suite("创建文件目录")
class TestCaseCreateFileDir(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_create_file_dir_006(self):
        """文件存储-正常创建文件目录成功"""


if __name__ == '__main__':
    pass

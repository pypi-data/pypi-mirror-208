#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_create_file_share
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from flexrunner import CaseMetaClass


@allure.suite("创建文件共享")
class TestCaseCreateFileShare(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_create_file_share_007(self):
        """文件存储-正常创建文件共享成功"""


if __name__ == '__main__':
    pass

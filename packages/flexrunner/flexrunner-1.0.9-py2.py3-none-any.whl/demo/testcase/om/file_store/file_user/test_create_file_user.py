#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_create_file_user
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 文件用户 - 创建
"""
import pytest
import allure
from flexrunner import CaseMetaClass
from demo.features.om.login_page import LoginPage


@allure.suite("创建本地用户")
class TestCaseCreateLocalUser(metaclass=CaseMetaClass):
    login_page = LoginPage()

    @pytest.mark.CI
    def test_create_loacl_user_008(self):
        """文件存储-正常创建本地用户成功"""
        self.login_page.login_success()


if __name__ == '__main__':
    pass

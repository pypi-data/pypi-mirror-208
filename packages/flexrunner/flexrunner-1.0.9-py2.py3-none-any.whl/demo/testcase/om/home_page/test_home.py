#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_home
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 首页显示验证
"""
import pytest
import allure
from flexrunner import CaseMetaClass
from demo.features.om.login_page import LoginPage


@allure.suite("首页")
class TestCaseHome(metaclass=CaseMetaClass):
    login_page = LoginPage()

    @pytest.mark.CI
    def test_home_005(self):
        """正常登录成功"""
        self.login_page.login_success()


if __name__ == '__main__':
    pass

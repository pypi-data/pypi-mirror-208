#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:login_page
@time:2022/12/23
@email:tao.xu2008@outlook.com
@description: 登录页面 操作步骤
"""
import pytest

from flexrunner import WebRunner
from flexrunner.global_context import GlobalContext
from flexrunner import StepMetaClass


class LoginPage(WebRunner, metaclass=StepMetaClass):
    """登录页面"""
    env = GlobalContext.env

    def login_input(self, user=None, password=None):
        """登录页面输入"""
        self.open(self.env.web_url + '/login')
        self.type(id_="accessKey", text=user or self.env.web_user, enter=False)
        self.type(id_="secretKey", text=password or self.env.web_pass, enter=False)
        self.click(id_="do-login")

    def assert_login_success(self):
        """验证登录成功"""
        self.assertInUrl("browser")
        self.assertInTitle("MinIO Console")

    def assert_login_failed(self):
        """验证登录失败"""
        self.assertInElement(xpath='/html/body/div[2]/div[1]', text="Invalid Login.")
        # self.assertInElement(xpath='/html/body/div[2]/div[1]', text="ErrorResponse")

    def assert_logout_success(self):
        """验证退出登录成功"""
        self.assertInUrl("/login")

    def login_success(self):
        """正常登录 -> 成功"""
        self.login_input()
        self.assert_login_success()

    def login_with_err_user(self):
        """使用错误用户名登录 -> 失败"""
        self.login_input(user='err_user')
        self.assert_login_failed()

    def login_with_err_pass(self):
        """使用错误用户名密码登录 -> 失败"""
        self.login_input(password='err_password')
        self.assert_login_failed()

    def login_with_err_user_pass(self):
        """使用错误用户名+密码登录 -> 失败"""
        self.login_input(user='err_user', password='err_password')
        self.assert_login_failed()

    def logout(self):
        """退出登录"""
        self.click(xpath='//*[@id="app-menu"]/div/div[2]/ul[2]/a')
        self.assert_logout_success()


@pytest.fixture()
def teardown_logout():
    yield
    # 在执行测试方法之后要执行的代码, 退出登录
    LoginPage().logout()


if __name__ == '__main__':
    pass

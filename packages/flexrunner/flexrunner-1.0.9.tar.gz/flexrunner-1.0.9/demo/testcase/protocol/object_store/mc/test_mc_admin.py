#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_mc_admin
@time:2023/03/06
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from loguru import logger
from flexrunner import CaseMetaClass
from demo.features.protocol.object_store.mc.mc_admin import MCAdmin


@allure.suite("MCAdmin")
class TestCaseMCAdmin(metaclass=CaseMetaClass):
    """mc admin 命令测试"""

    def setup(self):
        """pytest setup"""
        self.mc_admin = MCAdmin()

    @pytest.mark.CI
    def test_info_018(self):
        """mc admin info"""
        rc, _ = self.mc_admin.info()
        assert rc == 0

    @pytest.mark.CI
    def test_info_019(self):
        """mc admin user list"""
        rc, _ = self.mc_admin.user_list()
        assert rc == 0


if __name__ == '__main__':
    pass

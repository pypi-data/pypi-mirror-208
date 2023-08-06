#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_upgrade
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description: 在线升级
"""
import pytest
import allure
from flexrunner import CaseMetaClass


class TestCaseUpgrade(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_upgrade_017(self):
        """正常在线升级成功"""
        pass


if __name__ == '__main__':
    pass

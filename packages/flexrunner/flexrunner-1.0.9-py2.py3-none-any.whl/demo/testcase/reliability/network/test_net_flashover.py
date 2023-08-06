#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_ha_network
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description: 网络闪断 - 前端网络
"""
import pytest
import allure
from flexrunner import CaseMetaClass


@allure.suite("网络闪断")
class TestCaseNetFlashover(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_front_014(self):
        """前端网络闪断"""
        pass


if __name__ == '__main__':
    pass

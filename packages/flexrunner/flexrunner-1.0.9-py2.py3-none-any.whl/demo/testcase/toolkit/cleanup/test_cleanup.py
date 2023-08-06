#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_cleanup
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description: 清除部署
"""
import pytest
import allure
from flexrunner import CaseMetaClass
from demo.features.toolkit.cli import ToolKitCLI


class TestCaseCleanup(metaclass=CaseMetaClass):

    def setup(self):
        """pytest setup"""
        self.toolkit_cli = ToolKitCLI()

    @pytest.mark.CI
    @pytest.mark.run(order=-1)
    def test_cleanup_015(self):
        """正常清除部署成功"""
        self.toolkit_cli.cleanup()


if __name__ == '__main__':
    pass

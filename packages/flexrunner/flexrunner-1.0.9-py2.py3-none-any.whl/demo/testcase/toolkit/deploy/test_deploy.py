#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_deploy
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description: 部署
"""
import pytest
import allure
from flexrunner import CaseMetaClass
from demo.features.toolkit.cli import ToolKitCLI


class TestCaseDeploy(metaclass=CaseMetaClass):

    def setup(self):
        """pytest setup"""
        self.toolkit_cli = ToolKitCLI()

    @pytest.mark.CI
    @pytest.mark.run(order=1)
    def test_deploy_016(self):
        """正常部署成功"""
        assert self.toolkit_cli.deploy()


if __name__ == '__main__':
    pass

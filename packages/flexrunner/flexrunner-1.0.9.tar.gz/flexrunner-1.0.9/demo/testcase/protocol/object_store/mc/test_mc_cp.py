#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:cp
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description: mc cp
"""
import pytest
import allure
from flexrunner import CaseMetaClass


@allure.suite("cp")
class TestCaseMCCP(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_cp_012(self):
        """mc cp上传对象"""
        pass


if __name__ == '__main__':
    pass

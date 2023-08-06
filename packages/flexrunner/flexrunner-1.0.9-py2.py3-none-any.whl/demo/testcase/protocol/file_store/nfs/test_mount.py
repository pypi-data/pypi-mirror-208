#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_mount
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from flexrunner import CaseMetaClass


@allure.suite("mount")
class TestCaseNFSMount(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_mount_011(self):
        """NFS mount成功"""
        pass


if __name__ == '__main__':
    pass

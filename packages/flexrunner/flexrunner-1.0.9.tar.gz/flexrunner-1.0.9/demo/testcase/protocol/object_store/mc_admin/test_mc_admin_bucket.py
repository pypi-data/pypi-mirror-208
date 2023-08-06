#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_mc_admin_bucket
@time:2023/02/22
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from flexrunner import CaseMetaClass


@allure.suite("bucket")
class TestCaseMCAdminBucket(metaclass=CaseMetaClass):

    @pytest.mark.CI
    def test_bucket_info_013(self):
        """mc admin bucket info"""
        pass


if __name__ == '__main__':
    pass

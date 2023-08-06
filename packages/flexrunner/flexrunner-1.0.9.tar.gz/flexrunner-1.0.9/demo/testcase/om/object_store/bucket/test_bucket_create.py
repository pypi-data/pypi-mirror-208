#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_bucket_create
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from flexrunner import CaseMetaClass
from flexrunner.global_context import GlobalContext
from demo.features.om.login_page import LoginPage
from demo.features.om.object_store.bucket_mgr.bucket_list_page import BucketListPage


@allure.suite("创建桶")
class TestCaseCreateBucket(metaclass=CaseMetaClass):
    time_str = GlobalContext.get_time_str()
    login_page = LoginPage()
    bucket_list_page = BucketListPage()

    @classmethod
    def setup_class(cls):
        cls.login_page.login_success()

    @classmethod
    def teardown_class(cls):
        cls.login_page.logout()

    @pytest.mark.P0
    def test_create_bucket_009(self):
        """创建桶成功"""
        bucket_name = f'auto-{self.time_str}'
        self.bucket_list_page.create_bucket(bucket_name)


if __name__ == '__main__':
    pass

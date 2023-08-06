#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:object
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 对象上传
"""
import pytest
import allure
from flexrunner import CaseMetaClass
from flexrunner.global_context import GlobalContext
from demo.features.om.login_page import LoginPage
from demo.features.om.object_store.bucket_mgr.bucket_list_page import BucketListPage


@allure.suite("上传对象")
class TestCaseUploadObject(metaclass=CaseMetaClass):
    time_str = GlobalContext.get_time_str()
    bucket_name = f'auto-{time_str}'
    login_page = LoginPage()
    bucket_list_page = BucketListPage()

    @classmethod
    def setup_class(cls):
        cls.login_page.login_success()
        cls.bucket_list_page.create_bucket(cls.bucket_name)

    @classmethod
    def teardown_class(cls):
        cls.login_page.logout()

    @pytest.mark.P0
    def test_upload_object_010(self):
        """上传对象成功 TODO"""
        pass


if __name__ == '__main__':
    pass

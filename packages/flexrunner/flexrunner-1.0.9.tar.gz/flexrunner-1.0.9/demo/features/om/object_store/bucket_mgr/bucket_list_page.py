#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:buckets_page
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 桶列表页面 操作步骤
"""
from flexrunner import WebRunner
from flexrunner.global_context import GlobalContext
from flexrunner import StepMetaClass


class BucketListPage(WebRunner, metaclass=StepMetaClass):
    """桶页面"""
    env = GlobalContext.env
    buckets_url = env.web_url + "/buckets"

    def refresh_bucket_list(self):
        """刷新桶列表"""
        self.open(self.buckets_url)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div[1]/div[2]/span[4]')

    def search_bucket_list(self, bucket_name):
        """搜索桶列表"""
        self.open(self.buckets_url)
        self.type_enter(bucket_name, clear=True, xpath='//*[@id="search-resource"]')

    def assert_bucket_exist(self, bucket_name):
        self.search_bucket_list(bucket_name)
        self.assertElement(xpath=f'//*[@id="manageBucket-{bucket_name}"]')

    def _enter_create_bucket_page(self):
        """进入”创建桶“页面"""
        self.open(self.buckets_url)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div[1]/div[2]/span[5]')
        self.assertInUrl("add-bucket")

    def _create_bucket_input(self, bucket_name):
        """创建桶输入信息"""
        self.type(xpath='//*[@id="bucket-name"]',
                  text=bucket_name, enter=False)
        self.click(xpath='//*[@id="create-bucket"]')

    def create_bucket(self, bucket_name):
        """创建一个桶"""
        self._enter_create_bucket_page()
        self._create_bucket_input(bucket_name)
        self.assert_bucket_exist(bucket_name)


if __name__ == '__main__':
    pass

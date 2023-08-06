#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:models
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: 基础数据模型
"""
from enum import Enum
from typing import List, Text

from pydantic import BaseModel
from flexrunner.base.models.result_models import TestStatusEnum, TestTime


# 测试用例状态
class TestCaseStatusEnum(Text, Enum):
    """测试用例状态枚举"""
    TODO = '未开始'
    CREATION = '写作中'
    DEBUGGING = '调试中'
    WAIT = '待评审'
    NORMAL = '正常'
    OBSOLETED = '废弃'


# 测试用例
class TestCaseInfo(BaseModel):
    """测试用例信息"""
    # 用例详情
    id: int = 0  # 用例ID，对应禅道ID
    name: Text = ""  # 测试用例名称、标题
    description: Text = ""  # 测试用例描述
    product_id: int = 0  # 所属产品 ID
    product_name: Text = ""  # 所属产品名称
    story: Text = ""  # 相关研发需求
    priority: Text = ""  # 优先级
    type: Text = "功能测试"  # 用例类型：(feature 功能测试 | performance 性能测试 | config 配置相关 | install 安装部署 |
    # security 安全相关 | interface 接口测试 | unit 单元测试 | other 其他)
    mark_list: List[Text] = []  # 测试用例标记
    keyword_list: List[Text] = []  # 测试用例关键词
    module_list: List[Text] = []  # 测试用例所属模块
    bug_list: List[Text] = []  # 测试用例已知bug

    # 编写、维护
    owner: Text = ""  # 用例责任人
    maintainer: Text = ""  # 用例维护人
    status: Text = TestCaseStatusEnum.WAIT.value
    code_path: Text = ""  # 测试用例脚本路径
    is_delete: bool = False  # 软删除

    # 执行状态
    last_report_id: int = 0  # 最近一次执行测试用例的报告ID
    last_test_status: Text = TestStatusEnum.UNKNOWN.value  # 最近一次测试用例执行状态
    last_test_time: TestTime = TestTime()  # 最近一次测试用例执行时间
    last_test_detail: Text = "{}"  # 最近一次测试详情


if __name__ == '__main__':
    pass

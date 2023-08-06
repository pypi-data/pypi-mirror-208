#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:result_models
@time:2023/02/25
@email:tao.xu2008@outlook.com
@description:
"""
from enum import Enum
from typing import Dict, List, Text

from pydantic import BaseModel


# 测试结果状态 - 枚举
class TestStatusEnum(Text, Enum):
    """测试结果状态枚举"""
    UNKNOWN = ''
    PASSED = 'passed'
    FAILED = 'failed'
    ERROR = 'error'
    SKIPPED = 'skipped'
    BROKEN = 'broken'


# 测试结果统计
class TestStat(BaseModel):
    """测试结果统计"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    error: int = 0
    skipped: int = 0
    # 记录失败、故障、跳过的用例/步骤详情
    failed_list: List[Dict] = []  # [{},{}]
    error_list: List[Dict] = []  # [{},{}]
    skipped_list: List[Dict] = []  # [{},{}]


# 测试执行时间
class TestTime(BaseModel):
    """测试用例执行时间"""
    start_at: float = 0
    end_at: float = 0
    duration: float = 0
    start_at_format: Text = ""
    end_at_format: Text = ""
    duration_format: Text = ""


# 测试报告 - 结果概览
class ReportSummary(BaseModel):
    """测试报告概要收集"""
    id: int = 0
    name: Text = "xxx测试报告"
    description: Text = "xxx测试报告"
    status: Text = TestStatusEnum.UNKNOWN.value
    time: TestTime = TestTime()
    testcases_stat: TestStat = TestStat()
    teststeps_stat: TestStat = TestStat()
    log_path: Text = ''
    report_allure_path: Text = ''
    report_html_path: Text = ''
    jenkins_job_name: Text = ''
    jenkins_build_number: int = 0
    allure_url: Text = ''
    build_type: Text = 0
    build_status: Text = 'build-status-static'
    env_id: int = 0


if __name__ == '__main__':
    pass

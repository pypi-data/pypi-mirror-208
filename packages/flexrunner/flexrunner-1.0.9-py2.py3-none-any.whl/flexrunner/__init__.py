#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/08/24
@email:tao.xu2008@outlook.com
@description:
"""
# from flexrunner.global_context import GlobalContext
from flexrunner.core.runners.util import get_testcase_id_by_func_name
from flexrunner.core.runners.meta_class import StepMetaClass, CaseMetaClass, step_decorator, case_decorator
from flexrunner.core.runners.api.step import ApiStep, RunRequest
from flexrunner.core.runners.web import WebRunner, WebDriver, WebElement
from flexrunner.core.runners.command import CmdRunner

__all__ = [
    # "GlobalContext",
    "get_testcase_id_by_func_name",
    "StepMetaClass", "CaseMetaClass", "step_decorator", "case_decorator",  # 元编程，实现批量装饰
    "ApiStep", "RunRequest",
    "WebRunner", "WebDriver", "WebElement",  # WEB UI 测试
    "CmdRunner"  # CMD命令执行测试
]


if __name__ == '__main__':
    pass

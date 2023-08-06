#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:global_context.py
@time:2022/12/26
@email:tao.xu2008@outlook.com
@description: 
"""
import os
import json
from datetime import datetime
from typing import Dict, Text
from loguru import logger
from threading import local

from flexrunner.base.db import TestDB
from flexrunner.base.models import TestConf, TestEnv, TestStatusEnum, ReportSummary, TestCaseInfo
from flexrunner.config.cf_xml import ConfigXml
from flexrunner.config.globals import BASE_DIR, CWD, REPORT_DIR, ConfigIni
from flexrunner.utils.util import zfill


class GlobalContext:
    """全局上下文配置参数"""

    driver = None  # 浏览器 driver
    timeout = 10

    # 测试配置文件/输入参数 解析
    test_conf_path = ""
    test_conf: TestConf = None

    # jenkins
    jenkins_workspace = ""

    # 全局常量配置：global_conf.ini
    global_cf = None
    debug = False
    log_level = 'DEBUG'
    console_log_level = 'INFO'
    max_rotation = '100 MB'
    max_retention = '30 days'
    db_info = {"ENGINE": 'django.db.backends.sqlite3', "NAME": 'db.sqlite3'}
    # 常量
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")  # 时间字符串

    # 输出报告信息记录
    report_summary: ReportSummary = ReportSummary()

    # 测试用例执行列表
    test_case_dict: Dict[Text, TestCaseInfo] = {}

    # 测试环境配置
    env: TestEnv = None

    # 全局动态缓存
    current_local = local()  # local cache

    def __init__(self):
        pass

    # 测试环境配置
    @classmethod
    def set_env(cls, env):
        cls.env = env

    @classmethod
    def get_env(cls):
        return cls.env

    @classmethod
    def del_env(cls):
        del cls.env

    # 全局动态缓存
    @classmethod
    def set_global_cache(cls, key, value):
        if not hasattr(cls.current_local, "glb_cache") or cls.current_local.glb_cache is None:
            cls.current_local.glb_cache = {}
        cls.current_local.glb_cache[key] = value

    @classmethod
    def get_global_cache(cls, key):
        if not hasattr(cls.current_local, "glb_cache") or cls.current_local.glb_cache is None:
            return None
        return cls.current_local.glb_cache.get(key)

    @classmethod
    def del_global_cache(cls):
        if not hasattr(cls.current_local, "glb_cache") or cls.current_local.glb_cache is None:
            return None
        rc_l = cls.current_local
        del rc_l.glb_cache

    @classmethod
    def get_global_step_id(cls, start=1):
        if not hasattr(cls.current_local, "step_id") or cls.current_local.step_id is None:
            cls.current_local.step_id = start
        return cls.current_local.step_id

    @classmethod
    def reset_step_id(cls, start=1):
        cls.current_local.step_id = start

    @classmethod
    def count_global_step_id(cls, start=1, step=1):
        if not hasattr(cls.current_local, "step_id") or cls.current_local.step_id is None:
            cls.current_local.step_id = start
        cls.current_local.step_id += step

    # 常量
    @classmethod
    def get_time_str(cls):
        return datetime.now().strftime("%Y%m%d%H%M%S")  # 时间字符串

    # 测试配置文件解析，并生成全局常量
    @classmethod
    def get_test_conf(cls) -> TestConf:
        """
        xml测试配置文件-解析
        :return:
        """
        if not hasattr(cls.current_local, "test_conf") or cls.current_local.test_conf is None:
            if cls.test_conf_path:
                logger.info("XML配置文件参数解析...")
                cx = ConfigXml(cls.test_conf_path)
                cls.test_conf = cx.parse_test_conf()
                logger.info(json.dumps(cls.test_conf.dict(), indent=2))
            else:
                logger.info("测试输入参数解析... TODO")  # TODO
                raise Exception("输入参数解析暂不支持，请输入XML配置文件路径！")
        return cls.test_conf

    # 全局常量配置文件解析：global_conf.ini
    @classmethod
    def get_global_cf(cls):
        project_cf_path = os.path.join(CWD, cls.test_conf.project, "conf", "global_conf.ini")
        if os.path.exists(project_cf_path):
            global_cf_path = project_cf_path
        else:
            # 项目未单独配置 global_conf.ini，则使用默认配置
            global_cf_path = os.path.join(BASE_DIR, "flexrunner", "config", "global_conf.ini")
        cls.global_cf = ConfigIni(global_cf_path)
        try:
            cls.log_level = cls.global_cf.get_str("LOGGER", "file_level")
            cls.console_log_level = cls.global_cf.get_str("LOGGER", "console_level")
            cls.max_rotation = cls.global_cf.get_str("LOGGER", "max_rotation")
            cls.max_retention = cls.global_cf.get_str("LOGGER", "max_retention")
            cls.db_info = {
                "ENGINE": cls.global_cf.get_str("DATABASES", "ENGINE"),
                "NAME": cls.global_cf.get_str("DATABASES", "NAME"),
            }
        except Exception as e:
            logger.debug(e)

        return cls.global_cf

    @property
    def zfill_report_id(self):
        return zfill(self.report_summary.id)

    @property
    def webdriver_path(self):
        return os.path.join(CWD, self.test_conf.project, 'bin', 'webdrivers')

    @property
    def testcase_path(self):
        return os.path.join(CWD, self.test_conf.project, 'testcase')

    @property
    def testdata_path(self):
        return os.path.join(CWD, self.test_conf.project, 'testdata')

    @property
    def log_name(self):
        return '{}_{}_{}.log'.format(self.test_conf.project, self.report_summary.id, self.time_str)

    @property
    def project_reports_path(self):
        return os.path.join(REPORT_DIR, self.test_conf.project)

    @property
    def output_path(self):
        return os.path.join(REPORT_DIR, self.test_conf.project, self.zfill_report_id)

    @property
    def log_path(self):
        return os.path.join(self.output_path, "log")

    @property
    def case_log_path(self):
        return os.path.join(self.output_path, "log", "testcase")

    @property
    def log_full_path(self):
        return os.path.join(self.log_path, self.log_name)

    @property
    def html_name(self):
        return '{}_{}_{}.html'.format(self.test_conf.project, self.report_summary.id, self.time_str)

    @property
    def html_report_path(self):
        return os.path.join(self.output_path, "html")

    @property
    def html_report_full_path(self):
        return os.path.join(self.html_report_path, self.html_name)

    @property
    def json_name(self):
        return '{}_{}_{}.json'.format(self.test_conf.project, self.report_summary.id, self.time_str)

    @property
    def json_report_path(self):
        return os.path.join(self.output_path, "json")

    @property
    def json_report_full_path(self):
        return os.path.join(self.json_report_path, self.json_name)

    @property
    def allure_results_path(self):
        return os.path.join(self.jenkins_workspace or self.output_path, "allure-results")

    # 初始化数据库
    def _init_db(self):
        """数据库初始化、插入测试session数据到test report表"""
        db = TestDB(db_info=self.db_info)
        db.create_report_table_if_not_exist()
        db.create_testcase_table_if_not_exist()
        self.report_summary.id = db.get_report_last_id() + 1
        db.insert_init_testreport(self.report_summary.id)

    # 初始化
    def init_data(self):
        """解析配置文件并初始化全局变量"""
        self.get_test_conf()  # 解析测试配置文件
        self.get_global_cf()  # 解析项目全局配置文件
        self.set_env(self.test_conf.testbed.env_list[0])  # 环境信息设置为env
        self._init_db()

        self.report_summary.log_path = self.log_path
        self.report_summary.report_html_path = self.html_report_path
        self.report_summary.report_allure_path = self.allure_results_path

    # 结果收集统计
    @classmethod
    def add_case_passed(cls, case=''):
        cls.report_summary.testcases_stat.total += 1
        cls.report_summary.testcases_stat.passed += 1

    @classmethod
    def add_case_failed(cls, case):
        cls.report_summary.testcases_stat.total += 1
        cls.report_summary.testcases_stat.failed += 1
        cls.report_summary.testcases_stat.failed_list.append(case)

    @classmethod
    def add_case_error(cls, case):
        cls.report_summary.testcases_stat.total += 1
        cls.report_summary.testcases_stat.error += 1
        cls.report_summary.testcases_stat.error_list.append(case)

    @classmethod
    def add_case_skipped(cls, case):
        cls.report_summary.testcases_stat.total += 1
        cls.report_summary.testcases_stat.skipped += 1
        cls.report_summary.testcases_stat.skipped_list.append(case)

    @classmethod
    def testcases_stat_count(cls, test_status, case=''):
        """
        测试用例结果统计
        :param test_status:
        :param case:
        :return:
        """
        if test_status == TestStatusEnum.PASSED.value:
            cls.add_case_passed()
        elif test_status == TestStatusEnum.FAILED.value:
            cls.add_case_failed(case)
        elif test_status == TestStatusEnum.ERROR.value:
            cls.add_case_error(case)
        elif test_status == TestStatusEnum.SKIPPED.value:
            cls.add_case_skipped(case)
        else:
            pass


if __name__ == '__main__':
    pass

#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:conftest
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
"""
import os
import time
import datetime
import pytest
from filelock import FileLock
from py._xmlgen import html
from loguru import logger
import allure

from demo import PRODUCT_ID, PRODUCT_NAME
from flexrunner import get_testcase_id_by_func_name
from flexrunner.base.db import TestDB
from flexrunner.global_context import GlobalContext
from flexrunner.base.models import TestStatusEnum
from flexrunner.core.runners.icon_msg import IconMsg


# 自定义参数
def pytest_addoption(parser):
    parser.addoption("--case_log_path", action="store", default="", help="自定义参数，用例执行日志路径")
    parser.addoption("--case_log_level", action="store", default="DEBUG", help="自定义参数，用例执行日志level")
    parser.addoption("--report_id", action="store", default=None, help="自定义参数，测试报告ID")


@pytest.fixture
def time_str(request):
    return request.config.getoption("--time_str")


@pytest.fixture
def case_log_path(request):
    return request.config.getoption("--case_log_path")


@pytest.fixture
def case_log_level(request):
    return request.config.getoption("--case_log_level")


@pytest.fixture
def report_id(request):
    return request.config.getoption("--report_id")


@pytest.mark.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))


@pytest.mark.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report, cells):
    try:
        cells.insert(1, html.td(report.description))
    except Exception as e:
        cells.insert(1, html.td(str(e)))
        logger.error(e)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    标记测试结果到 BaseAPI().step_table
    :param item:
    :param call:
    :return:
    """
    out = yield
    report = out.get_result()
    # report.description = ''
    # logger.trace('⋙ 测试报告：%s' % report)
    # logger.trace('⋙ 步骤：%s' % report.when)
    # logger.trace('⋙ nodeid：%s' % report.nodeid)
    # logger.trace('⋙ description:%s' % str(item.function.__doc__))
    # logger.trace(('⋙ 运行结果: %s' % report.outcome))

    case_id = get_testcase_id_by_func_name(item.name)
    if report.when == "setup" and report.outcome == "failed":
        test_status = TestStatusEnum.SKIPPED.value
        # GlobalContext.test_case_dict[case_id].last_test_status = test_status
        GlobalContext.add_case_skipped(item.name)
    elif report.when == "call":
        test_status = report.outcome
        GlobalContext.testcases_stat_count(test_status, item.name)
        GlobalContext.test_case_dict[case_id].last_test_status = test_status
    else:
        pass


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    """setup and teardown each task"""
    with FileLock("session.lock"):
        logger.debug(IconMsg.setup(f"Start session ..."))
        # 开始时间
        start_at = time.time()
        GlobalContext.report_summary.time.start_at = start_at
        GlobalContext.report_summary.time.start_at_format = datetime.datetime.utcfromtimestamp(start_at).isoformat(timespec="seconds")
        logger.debug(IconMsg.setup("Start testcase ..."))

    yield
    logger.debug(IconMsg.teardown("Teardown session ..."))

    logger.debug(IconMsg.teardown(f"Task finished, update test report summary..."))
    # 连接数据库，写入测试结果
    try:
        db = TestDB(db_info=GlobalContext.db_info)
    except Exception as e:
        logger.error(IconMsg.teardown(e))
        db = None

    # 结束时间
    end_at = time.time()
    GlobalContext.report_summary.time.duration = end_at - start_at

    # 总体结果
    testcases_stat = GlobalContext.report_summary.testcases_stat
    if testcases_stat.total == (testcases_stat.passed + testcases_stat.skipped):
        GlobalContext.report_summary.status = TestStatusEnum.PASSED.value
    else:
        GlobalContext.report_summary.status = TestStatusEnum.FAILED.value

    # 遍历测试用例
    for item in request.node.items:
        case_id = get_testcase_id_by_func_name(item.name)
        GlobalContext.test_case_dict[case_id].product_id = PRODUCT_ID
        GlobalContext.test_case_dict[case_id].product_name = PRODUCT_NAME
        GlobalContext.test_case_dict[case_id].code_path = item.nodeid
        GlobalContext.test_case_dict[case_id].last_report_id = GlobalContext.report_summary.id
        GlobalContext.test_case_dict[case_id].last_test_time = GlobalContext.report_summary.time

        GlobalContext.test_case_dict[case_id].mark_list = [m.name for m in item.own_markers]
    # print(GlobalContext.test_case_dict)
    # 插入测试结果到TestReport表
    if db:
        logger.info(IconMsg.teardown("更新测试结果到TestReport表..."))
        update_report_keys = [
            "status", "time", "testcases_stat", "teststeps_stat",
            "log_path", "report_allure_path", "report_html_path",
            "jenkins_job_name", "jenkins_build_number", "allure_url", "build_type", "build_status",
            "env_id"
        ]
        db.update_testreport(GlobalContext.report_summary, filter_keys=update_report_keys)
        logger.info(IconMsg.teardown("更新测试用例到TestCase表..."))
        update_testcase_keys = [
            "name", "description", "product_id", "story", "priority", "type",
            "mark_list", "keyword_list", "module_list",
            "code_path",
            "last_report_id", "last_test_status", "last_test_time", "last_test_detail"
        ]
        exclude_keys = ["product_name"]
        db.insert_update_testcase(dict(GlobalContext.test_case_dict), update_testcase_keys, exclude_keys)

    # 发送测试报告到邮件 TODO
    logger.debug(IconMsg.teardown("发送测试报告到邮件...（TODO）"))


@pytest.fixture(scope="function", autouse=True)
def testcase_fixture(request):
    case_log_path = request.config.getoption("--case_log_path")
    case_log_level = request.config.getoption("--case_log_level")
    log_name = f"{request.node.name}.log"
    case_log_path_name = os.path.join(case_log_path, log_name)
    # 添加测试用例执行logger
    handler_id = logger.add(
        case_log_path_name,
        rotation='10 MB',
        retention='1 days',
        enqueue=True,
        encoding="utf-8",
        level=case_log_level
    )
    yield
    # 重置步骤ID
    GlobalContext.reset_step_id()
    # 删除测试用例logger
    logger.remove(handler_id)
    # 附件测试用例日志
    # allure.attach.file(case_log_path_name, log_name)  # 取消，已在meta_case中通过装饰器处理，使日志附加到body区域


if __name__ == '__main__':
    pass

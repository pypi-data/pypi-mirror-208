#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:main
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import os
import json
import shutil

import pytest
import typer
import subprocess
import urllib3
from loguru import logger

from flexrunner.base.db import TestDB
from flexrunner.base.log import LogLevelEnum, init_logger
from flexrunner.global_context import GlobalContext
from flexrunner.utils.util import seconds_to_hms, json_dumps


urllib3.disable_warnings()
urllib3.add_stderr_logger(LogLevelEnum.INFO.value)


def run_pytest(context, collect_only=False):
    """
    执行pytest
    :param collect_only:
    :param context:
    :return:
    """
    # 解析pytest 文件
    test_conf = context.test_conf
    pytest_files_set = []
    for ts in test_conf.test_set_list:
        for case in ts.case_list:
            pytest_files_set.append(os.path.join(test_conf.base_path, case['location']))
    logger.info("\n{}".format(json.dumps(pytest_files_set, indent=2)))

    db_info = GlobalContext.db_info
    if db_info.get('ENGINE') == 'django.db.backends.sqlite3':
        db_info["DB_PATH"] = str(db_info.get('NAME'))
    elif db_info.get('ENGINE') == 'django.db.backends.mysql':
        db_info["USER"] = db_info.get('USER')
        db_info["PASSWORD"] = db_info.get('PASSWORD')
        db_info["HOST"] = db_info.get('HOST')
        db_info["PORT"] = db_info.get('PORT')
        db_info["NAME"] = db_info.get('NAME')
    # - 构建pytest 参数
    logger.info("构建pytest 参数...")
    argv = pytest_files_set + [
        '--case_log_path={}'.format(context().case_log_path),
        '--case_log_level={}'.format(context.log_level),
        '-v', '-s',
        # '--show-capture=no',  # 不显示捕获日志
        '--ignore-unknown-dependency',
        '-W', 'ignore:Module already imported:pytest.PytestWarning',

        # '--capture=sys',
        '--allure-no-capture',  # 取消添加程序中捕获到控制台或者终端的log日志或者print输出到allure测试报告的Test Body中
        '--alluredir={}'.format(context().allure_results_path), '--clean-alluredir',  # 生成allure xml结果

        # pytest-html
        # '--html={}'.format(context().html_report_full_path),
        # '--self-contained-html',

        # pytest-flexreport
        '--template=3',
        '--report={}'.format(context().html_report_full_path),
        '--history_dir={}'.format(context().project_reports_path),
        '--title=测试报告：{}（ID={}）'.format(test_conf.project, context.report_summary.id),
        '--log_path={}'.format(context().log_full_path),
        '--report_path={}'.format(context.jenkins_workspace or "http://127.0.0.1:65329/index.html"),
        '--testcase_basename=testcase',

        # pytest-json-report
        '--json-report',
        '--json-report-file={}'.format(context().json_report_full_path),
    ]
    if collect_only:
        argv.append('--collect-only')  # 只收集用例不执行，可用于统计用例数

    # -q test_01.py
    logger.info("pytest 命令：{}\n".format(json.dumps(argv, indent=2)))

    # - 执行pytest

    # 执行方式一
    # import pytest
    pytest.main(argv)
    # err_msg = ''
    # exit_code = 0

    # 执行方式二
    # p = subprocess.Popen(['pytest'] + argv)
    # p.wait()

    # - 获取结果并返回
    db = TestDB()
    filter_keys = ["status", "time", "testcases_stat", "teststeps_stat"]
    report_id = context.report_summary.id
    reports = db.get_report(report_id, filter_keys)
    if len(reports) == 0:
        raise Exception("未找到测试报告：{}".format(report_id))

    report_dict = {}
    for report in reports:
        for idx, k in enumerate(filter_keys):
            report_dict[k] = report[idx]
        break
    testcases_stat = json.loads(report_dict["testcases_stat"])
    total = testcases_stat["total"]
    passed = testcases_stat["passed"]
    failed = testcases_stat["failed"]
    error = testcases_stat["error"]
    skipped = testcases_stat["skipped"]
    pass_rate = round((passed+skipped)/total if total > 0 else 0, 3)

    time_dict = json.loads(report_dict["time"])
    duration = time_dict["duration"]

    summary = {
        "status": report_dict["status"],
        "total": total,
        "passed": passed,
        "failed": failed,
        "error": error,
        "skipped": skipped,
        "pass_rate": "{}%".format(pass_rate * 100),
        "duration": seconds_to_hms(duration,)
    }
    logger.info("测试结果：\n{}".format(json_dumps(summary)))
    return report_id, summary


def generate_allure_report(context):
    """
    从测试报告中读取测试结果数据，生成allure报告。
    服务器运行：通过Jenkins生成allure报告
    本地运行：allure serve命令立即生成allure报告
    :param context:
    :return:
    """
    try:
        logger.info("generate allure report...")
        # 本地调试
        allure_serve_cmd = 'D:\\allure\\bin\\allure serve {}'.format(context.report_summary.report_allure_path)
        logger.info(allure_serve_cmd)
        subprocess.Popen(allure_serve_cmd, shell=True, close_fds=True)
        # p.wait()
    except Exception as e:
        logger.error(e)


def main(
    test_conf_path: str = typer.Option(
            "./demo/conf/demo.xml",
            "--test_conf_path",
            "-f",
            help="配置文件路径，对应目录：./{$project}/conf/{$test_conf}",
        ),
    report_allure: bool = typer.Option(False, help="本地生成allure报告"),
    jenkins_workspace: str = typer.Option("", help="jenkins workspace路径"),
    collect_only: bool = typer.Option(False, help="只收集用例不执行，用于统计用例数"),
    loglevel: LogLevelEnum = typer.Option(LogLevelEnum.INFO, help="日志等级"),
    desc: str = typer.Option('', help="测试描述"),
):
    """FlexRunner 命令行 CLI"""
    # 参数解析
    test_conf_path = os.path.abspath(os.path.join(os.getcwd(), test_conf_path))
    logger.info("执行 {}".format(test_conf_path))
    GlobalContext.test_conf_path = test_conf_path
    GlobalContext.jenkins_workspace = jenkins_workspace
    GlobalContext().init_data()

    # 初始化日志
    init_logger(log_path=GlobalContext().log_full_path, suffix=desc.strip(), loglevel=loglevel)

    # - 执行 pytest
    try:
        return run_pytest(GlobalContext, collect_only)
    except Exception as e:
        raise e
    finally:
        logger.info("test log: {}".format(GlobalContext.report_summary.log_path))
        logger.info("result data: {}".format(GlobalContext.report_summary.report_allure_path))
        if report_allure and not collect_only:
            generate_allure_report(GlobalContext)


if __name__ == '__main__':
    typer.run(main)

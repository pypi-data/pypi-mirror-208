#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:log_init
@time:2022/09/06
@email:tao.xu2008@outlook.com
@description:
# 日志级别
Level	    value	Logger method
TRACE	    5	    logger.trace
DEBUG	    10	    logger.debug
INFO	    20	    logger.info
SUCCESS	    25	    logger.success
WARNING	    30	    logger.warning
ERROR	    40	    logger.error
CRITICAL	50	    logger.critical

info_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>"
"""
import os
import sys
import atexit
from enum import Enum
from typing import Text
import logging

import allure
from loguru import logger

from flexrunner.config import LOG_DIR  # FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, MAX_ROTATION, MAX_RETENTION
from flexrunner.global_context import GlobalContext
from flexrunner.base.models.log_icon_models import LogIconEnum
from flexrunner.base.models.platform_models import StepTypeEnum


FILE_LOG_LEVEL = GlobalContext.log_level
CONSOLE_LOG_LEVEL = GlobalContext.console_log_level
MAX_ROTATION = GlobalContext.max_rotation
MAX_RETENTION = GlobalContext.max_retention


class LogLevelEnum(Text, Enum):
    """logger级别枚举"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"


class LogFormatEnum(Text, Enum):
    """logger format枚举"""
    TINY = "{message}"
    MINI = "{time:YYYY-MM-DD HH:mm:ss} | {message}"
    SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | <level>{message}</level>"
    DEFAULT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | " \
              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
              "- <level>{message}</level>"
    DETAIL = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | " \
             "<cyan>P{process}</cyan>:<cyan>T{thread}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
             "- <level>{message}</level>"


class AllureLogger(logging.Handler):
    case_icon = LogIconEnum.CASE.value
    step_icon = LogIconEnum.STEP.value
    opt_fail_icon = LogIconEnum.OPT_FAIL.value

    def emit(self, record):
        if logging.DEBUG < record.levelno:  # print to allure only "info" messages
            msg = record.getMessage()
            if msg and self.case_icon not in msg and self.step_icon not in msg:  # meta_class -> step 已实现步骤描述，用例描述只打印日志
                try:
                    with allure.step(msg):  # f'LOG ({record.levelname}): {record.getMessage()}'
                        pass  # No need for content, since the step context is doing the work.
                        if self.opt_fail_icon in msg:
                            assert False
                except Exception as e:
                    pass


def __add_log_level():
    """
    新增级别
    :return:
    """
    logger.level('DESC', no=51)  # CRITICAL < DESC，打印描述信息到所有日志文件

    no_start = 52
    for step_type in StepTypeEnum:
        logger.level(step_type, no=no_start, color='<blue><bold>')  # CRITICAL < STEP
        no_start += 1


def init_logger(log_path='', suffix='', loglevel=None):
    """
    初始化logger日志配置
    :param log_path: 日志目录
    :param suffix: 日志名称后缀
    :param loglevel: 日志等级
    :return:
    """
    # 获取日志配置：级别、格式
    console_loglevel = CONSOLE_LOG_LEVEL
    console_format = LogFormatEnum.SIMPLE
    file_loglevel = FILE_LOG_LEVEL
    file_format = LogFormatEnum.SIMPLE
    if loglevel:
        if loglevel == LogLevelEnum.TRACE:
            console_loglevel = loglevel.value
            console_format = LogFormatEnum.DETAIL
            file_loglevel = loglevel.value
            file_format = LogFormatEnum.DETAIL
        elif loglevel == LogLevelEnum.DEBUG:
            console_loglevel = loglevel.value
            console_format = LogFormatEnum.DEFAULT
            file_loglevel = loglevel.value
            file_format = LogFormatEnum.DEFAULT

    # 获取日志保存路径
    log_path = log_path or LOG_DIR

    # 删除默认logger
    logger.remove()

    # 新增级别
    # logger.level('STEP', no=21, color='<blue><bold>')  # INFO < STEP < ERROR
    # logger.level('DESC', no=52)  # CRITICAL < DESC，打印描述信息到所有日志文件
    __add_log_level()

    # 初始化控制台配置 - CONSOLE_LOG_LEVEL
    logger.add(sys.stderr, level=console_loglevel, format=console_format)

    logger.info(log_path)
    suffix_log = '_{suffix}.log'.format(suffix=suffix) if suffix else '.log'
    # 初始化日志配置 -- all日志文件
    logger.add(
        log_path if log_path.endswith('.log') else os.path.join(log_path, '{time}' + suffix_log),
        rotation=MAX_ROTATION,  # '100 MB',
        retention=MAX_RETENTION,  # '30 days',
        enqueue=True,
        encoding="utf-8",
        level=file_loglevel,
        format=file_format,
        backtrace=True,
        diagnose=True
    )

    # allure 日志
    logger.add(
        AllureLogger(),
        level=console_loglevel, format=LogFormatEnum.MINI
    )

    atexit.register(logger.remove)


if __name__ == '__main__':
    pass

#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:icon_msg.py
@time:2023/03/12
@email:tao.xu2008@outlook.com
@description:
"""
from flexrunner.base.models.log_icon_models import LogIconEnum


class IconMsg(object):

    @staticmethod
    def setup(msg):
        return f"{LogIconEnum.SETUP.value} {msg}"

    @staticmethod
    def teardown(msg):
        return f"{LogIconEnum.TEARDOWN.value} {msg}"

    @staticmethod
    def case(msg):
        return f"{LogIconEnum.CASE.value} {msg}"

    @staticmethod
    def step(msg):
        return f"{LogIconEnum.STEP.value} {msg}"

    @staticmethod
    def opt(msg):
        return f"{LogIconEnum.OPT_SUCCESS.value} {msg}"

    @staticmethod
    def opt_visit_url(msg):
        return f"{LogIconEnum.OPT_VISIT_URL.value} {msg}"

    @staticmethod
    def opt_switch(msg):
        return f"{LogIconEnum.OPT_VISIT_URL.value} {msg}"

    @staticmethod
    def opt_refresh(msg):
        return f"{LogIconEnum.OPT_REFRESH.value} {msg}"

    @staticmethod
    def opt_wait(msg):
        return f"{LogIconEnum.OPT_WAIT.value} {msg}"

    @staticmethod
    def opt_sleep(msg):
        return f"{LogIconEnum.OPT_SLEEP.value} {msg}"

    @staticmethod
    def opt_success(msg):
        return f"{LogIconEnum.OPT_SUCCESS.value} {msg}"

    @staticmethod
    def opt_fail(msg):
        return f"{LogIconEnum.OPT_FAIL.value} {msg}"

    @staticmethod
    def opt_warning(msg):
        return f"{LogIconEnum.OPT_WARNING.value} {msg}"

    @staticmethod
    def check(msg):
        return f"{LogIconEnum.OPT_ASSERT.value} {msg}"

    @staticmethod
    def screenshot(msg):
        return f"{LogIconEnum.OPT_SCREENSHOT.value} {msg}"


if __name__ == '__main__':
    pass

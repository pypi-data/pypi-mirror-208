#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:custom_testcase
@time:2023/03/12
@email:tao.xu2008@outlook.com
@description:
"""
from loguru import logger
from unittest import TestCase
from flexrunner.core.runners.icon_msg import IconMsg


class CustomTestCase(TestCase):

    def fail(self, msg=None):
        """Fail immediately, with the given message."""
        if "次检查" in msg:
            logger.debug(IconMsg.opt_warning(msg))
        else:
            logger.error(IconMsg.opt_fail(msg))
        raise self.failureException(msg)


if __name__ == '__main__':
    pass

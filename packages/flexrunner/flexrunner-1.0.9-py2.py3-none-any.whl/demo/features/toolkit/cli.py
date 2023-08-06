#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:deploy
@time:2023/04/05
@email:tao.xu2008@outlook.com
@description:
"""
import os
import re
import json
import datetime
from loguru import logger
from flexrunner.base.models import StepTypeEnum
from flexrunner import CmdRunner

DEFAULT_MINIO_PATH = "D:\\minio"


class ToolKitCLI(CmdRunner):
    """ToolKit 命令行"""
    step_type = StepTypeEnum.MC.value  # 约定：指定测试类型，meta_class.py step需要使用

    def __init__(self, minio_path=DEFAULT_MINIO_PATH):
        super(ToolKitCLI, self).__init__()
        self.minio_path = minio_path

    def deploy(self):
        self.local_run_poll(
            f"{self.minio_path}\\minio.exe server {self.minio_path}\\data\\ --console-address 127.0.0.1:9001"
        )
        return True

    def cleanup(self):
        self.local_run("taskkill /F /IM minio.exe")


if __name__ == '__main__':
    pass

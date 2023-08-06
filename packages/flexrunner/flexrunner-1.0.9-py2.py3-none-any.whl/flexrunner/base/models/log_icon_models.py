#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:log_icon_models
@time:2023/4/7
@email:tao.xu2008@outlook.com
@description: 
"""
from enum import Enum
from typing import Text


# 测试日志图标 - 枚举
class LogIconEnum(Text, Enum):
    """测试日志图标 枚举"""
    SETUP = '🔛'  # 前置操作 标识 🅰️ 🥇  🔛  ▶
    TEARDOWN = '🔚'  # 后置操作 清除标识 🔚 ⏹
    CLEANUP = '🗑️'  # 后置操作 清除标识 ♻️
    CASE = '🌈'  # '📌' 🏷️  #️⃣ 🌈 🍉测试用例标识
    STEP = '🆔'  # 🚩 🔢 测试步骤标识
    # 操作
    OPT = '🕹️'  # 操作  ⚒️🛠️
    OPT_VISIT_URL = '📖'  # 操作: 打开网页 URL
    OPT_SWITCH = '🔀'  # 操作: 切换
    OPT_REFRESH = '🔄️'  # 操作: 刷新
    OPT_WAIT = '⌛'  # 操作: 等待
    OPT_SLEEP = '💤️'  # 操作: 睡眠
    OPT_SUCCESS = '✅'  # 操作: 成功
    OPT_FAIL = '❌'  # 操作: 失败
    OPT_WARNING = '⚡'  # 操作: 警告 💡 ⚡
    OPT_ASSERT = '👀'  # 操作: 校验检查
    OPT_SCREENSHOT = '📷️'  # 操作: 截屏


if __name__ == '__main__':
    pass

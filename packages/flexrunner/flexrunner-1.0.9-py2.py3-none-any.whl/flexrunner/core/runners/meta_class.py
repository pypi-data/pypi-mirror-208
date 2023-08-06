#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:meta_class
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 利用元类批量给所有继承类增加装饰器
"""
import os
import re
import ast
import allure
import types
import inspect
import unittest
from functools import wraps
from collections import OrderedDict
from loguru import logger
from flexrunner.base.models import TestCaseInfo
from flexrunner.global_context import GlobalContext
from flexrunner.core.runners.icon_msg import IconMsg
from flexrunner.core.runners.util import get_testcase_id_by_func_name


class PytestSetAllureLabelDynamic(object):
    """ pytest 动态设置Allure 标签"""
    def __init__(self):
        pass

    @staticmethod
    def get_testcase_path_parts(tc_py):
        """
        获取测试用例的路径 切片
        :param tc_py: 测试用例test_*.py文件路径
        :return:
        """
        path_parts = []
        while True:
            dirname, basename = os.path.split(tc_py)
            path_parts.insert(0, basename)
            if basename == "testcase":
                path_parts.insert(0, dirname)
                break
            if dirname == "":
                raise Exception("未找到*/testcase目录！")
            tc_py = dirname
        return 1, path_parts

    @staticmethod
    def get_init_module_zh(init_py):
        """
        获取包 __init__.py中：__module_zh__ = "模块中文描述"
        :param init_py: __init__.py文件路径
        :return:
        """
        module_zh_re = re.compile(r'__module_zh__\s+=\s+(.*)')
        with open(init_py, 'rb') as f:
            ret = module_zh_re.search(f.read().decode('utf-8'))

        if ret:
            str_zh = ret.group(1)
            module_zh = str(ast.literal_eval(str_zh)).strip()
            return module_zh
        logger.warning(f"{init_py} 未定义：__module_zh__")
        return ret

    @staticmethod
    def allure_dynamic_label(level, label):
        """
        动态设置allure标签
        :param level:
        :param label:
        :return:
        """
        if level > 3:
            return
        levels_define = ["epic", "feature", "story", "suite"]
        # logger.trace(f"allure.dynamic.label({levels_define[level]}, {label})")
        allure.dynamic.label(levels_define[level], label)

    def apply(self, case_id, tc_py_path):
        testcase_idx, path_parts = self.get_testcase_path_parts(tc_py_path)
        testcase_path = os.path.join(*path_parts[:testcase_idx + 1])
        part_path = testcase_path
        module_zh_levle = 0
        for idx, part in enumerate(path_parts[testcase_idx + 1:]):
            part_path = os.path.join(part_path, part)
            init_py_path = os.path.join(part_path, '__init__.py')
            if not os.path.exists(init_py_path):
                continue
            module_zh = self.get_init_module_zh(init_py_path)
            if module_zh:
                GlobalContext.test_case_dict[case_id].module_list.append(module_zh)
                self.allure_dynamic_label(module_zh_levle, module_zh)
                module_zh_levle += 1


def step_decorator(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if func.__name__ in ('setup', 'teardown', 'setup_class', 'teardown_class'):
            return func(*args, **kwargs)
        step_type = args[0].step_type
        # 如果用例没有描述/名称，则以方法名称代替
        step_desc = func.__doc__.lstrip("\n").lstrip().split("\n")[0] if func.__doc__ else func.__name__
        step_id = GlobalContext.get_global_step_id()
        title = f'Step{step_id}:【{step_type}】{step_desc}'
        logger.info(IconMsg.step(title))
        with allure.step(title=title):
            GlobalContext.count_global_step_id()
            return func(*args, **kwargs)
    return wrap


def case_decorator(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if func.__name__ in ('setup', 'teardown', 'setup_class', 'teardown_class'):
            return func(*args, **kwargs)
        case_desc = func.__doc__.strip("\n").strip()
        case_id = get_testcase_id_by_func_name(func.__name__)
        logger.info("")  # 每个case日志前空行
        logger.info(IconMsg.case(f'Case-{case_id}：{case_desc}'))
        allure.dynamic.title(f'(ID={case_id}){case_desc}')
        allure.dynamic.description(case_desc)
        allure.dynamic.testcase(f"https://chandao.cn/zendao/testcase-view-{case_id}.html", f"🆔:testcase-view-{case_id}")
        # 设置用例基本信息
        GlobalContext.test_case_dict[case_id] = TestCaseInfo(
            id=case_id,
            name=case_desc,
            description=case_desc,
            product=GlobalContext.test_conf.project,
        )
        # 动态设置模块树
        PytestSetAllureLabelDynamic().apply(case_id, os.path.abspath(func.__module__.replace('.', '/')))
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            case_log = f'{func.__name__}.log'
            allure.attach.file(os.path.join(GlobalContext().case_log_path, case_log), case_log)
        return res
    return wrap


class StepMetaClass(type):
    """
    使用方法:
        class TestClass(metaclass=MetaClass):
            meta_decoator = step
    """
    func = None

    def __new__(cls, name, bases, attrs):
        """
        name:类名,
        bases:类所继承的父类
        attrs:类所有的属性
        """
        cls.func = attrs.get('meta_decoator') or step_decorator
        assert inspect.isfunction(cls.func), '传入的meta装饰器不正确'
        # 在类生成的时候做一些处理
        new_attrs = cls.options(bases, attrs)
        return super().__new__(cls, name, bases, new_attrs)

    @classmethod
    def options(cls, bases, attrs):
        new_attrs = OrderedDict()
        # 循环自己的所有属性
        for key, value in attrs.items():
            # 对各种类型的方法进行分别处理
            if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
                    new_attrs[key] = value
                    continue
                if isinstance(value, staticmethod):
                    new_attrs[key] = staticmethod(cls.func(value.__func__))
                elif isinstance(value, classmethod):
                    new_attrs[key] = classmethod(cls.func(value.__func__))
                elif isinstance(value, property):
                    new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                              fdel=cls.func(value.fdel), doc=value.__doc__)
                elif not key.startswith('_'):
                    new_attrs[key] = cls.func(value)
                else:
                    new_attrs[key] = value
                continue
            new_attrs[key] = value
        # 循环所有继承类
        for base in bases:
            if isinstance(base, unittest.TestCase):
                continue
            for key, value in base.__dict__.items():
                if key not in new_attrs:
                    if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                        if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
                            new_attrs[key] = value
                            continue
                        if isinstance(value, staticmethod):
                            new_attrs[key] = staticmethod(cls.func(value.__func__))
                        elif isinstance(value, classmethod):
                            new_attrs[key] = classmethod(cls.func(value.__func__))
                        elif isinstance(value, property):
                            new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                                      fdel=cls.func(value.fdel), doc=value.__doc__)
                        elif not key.startswith('_'):
                            new_attrs[key] = cls.func(value)
                        else:
                            new_attrs[key] = value
                        continue
                    new_attrs[key] = value

        return new_attrs


class CaseMetaClassOld(type):
    func = None

    def __new__(cls, name, bases, attrs):
        """
        name:类名,
        bases:类所继承的父类
        attrs:类所有的属性
        """
        cls.func = attrs.get('meta_decoator') or case_decorator
        assert inspect.isfunction(cls.func), '传入的meta装饰器不正确'
        # 在类生成的时候做一些处理
        new_attrs = cls.options(bases, attrs)
        return super().__new__(cls, name, bases, new_attrs)

    @classmethod
    def options(cls, bases, attrs):
        new_attrs = OrderedDict()
        # 循环自己的所有属性
        for key, value in attrs.items():
            # 对各种类型的方法进行分别处理
            if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
                    continue
                elif isinstance(value, staticmethod):
                    new_attrs[key] = staticmethod(cls.func(value.__func__))
                elif isinstance(value, classmethod):
                    new_attrs[key] = classmethod(cls.func(value.__func__))
                elif isinstance(value, property):
                    new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                              fdel=cls.func(value.fdel), doc=value.__doc__)
                elif not key.startswith('_'):
                    new_attrs[key] = cls.func(value)
                else:
                    new_attrs[key] = value
                continue
            new_attrs[key] = value
        # 循环所有继承类
        for base in bases:
            if isinstance(base, unittest.TestCase):
                continue
            for key, value in base.__dict__.items():
                if key not in new_attrs:
                    if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                        if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
                            new_attrs[key] = value
                            continue
                        if isinstance(value, staticmethod):
                            new_attrs[key] = staticmethod(cls.func(value.__func__))
                        elif isinstance(value, classmethod):
                            new_attrs[key] = classmethod(cls.func(value.__func__))
                        elif isinstance(value, property):
                            new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                                      fdel=cls.func(value.fdel), doc=value.__doc__)
                        elif not key.startswith('_'):
                            new_attrs[key] = cls.func(value)
                        else:
                            new_attrs[key] = value
                        continue
                    new_attrs[key] = value

        return new_attrs


class CaseMetaClass(type):
    func = None

    def __new__(cls, name, bases, attrs):
        """
        name:类名,
        bases:类所继承的父类
        attrs:类所有的属性
        """
        cls.func = attrs.get('meta_decoator') or case_decorator
        assert inspect.isfunction(cls.func), '传入的meta装饰器不正确'
        # 在类生成的时候做一些处理
        new_attrs = cls.options(attrs)
        return super().__new__(cls, name, bases, new_attrs)

    @classmethod
    def options(cls, attrs):
        new_attrs = OrderedDict()
        # 循环自己的所有属性
        for key, value in attrs.items():
            # 对各种类型的方法进行分别处理
            if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
                    new_attrs[key] = value
                    continue
                elif isinstance(value, staticmethod):
                    new_attrs[key] = staticmethod(cls.func(value.__func__))
                elif isinstance(value, classmethod):
                    new_attrs[key] = classmethod(cls.func(value.__func__))
                elif isinstance(value, property):
                    new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                              fdel=cls.func(value.fdel), doc=value.__doc__)
                elif not key.startswith('_'):
                    new_attrs[key] = cls.func(value)
                else:
                    new_attrs[key] = value
                continue
            new_attrs[key] = value

        return new_attrs


if __name__ == '__main__':
    pass

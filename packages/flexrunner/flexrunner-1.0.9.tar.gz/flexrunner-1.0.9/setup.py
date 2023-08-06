#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'VERSION\s+=\s+(.*)')

with open('flexrunner/config/globals.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


# 读取文件内容
def read_file(filename, encoding='utf-8'):
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(cur_dir, filename), mode="r", encoding=encoding) as f:
        long_desc = f.read()
    return long_desc


# 获取依赖
def read_requirements(filename, encoding='utf-8'):
    return [line.strip() for line in read_file(filename, encoding).splitlines()
            if not line.startswith('#')]


def _find_packages():
    """find pckages"""
    packages = []
    path = '.'
    for root, _, files in os.walk(path):
        if '__init__.py' in files:
            if sys.platform.startswith('linux'):
                item = re.sub('^[^A-z0-9_]', '', root.replace('/', '.'))
            elif sys.platform.startswith('win'):
                item = re.sub('^[^A-z0-9_]', '', root.replace('\\', '.'))
            else:
                item = re.sub('^[^A-z0-9_]', '', root.replace('/', '.'))
            if item is not None:
                packages.append(item.lstrip('.'))
    return packages


setup(
    name='flexrunner',
    version=version,
    author='TXU',
    author_email='tao.xu2008@outlook.com',
    maintainer='TXU',
    maintainer_email='tao.xu2008@outlook.com',
    license='MIT',
    url='https://github.com/txu2k8/test-runner-flex',
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    descriptionr="一个针python写作的测试执行引擎/框架，以MinIO为demo，实现UI、API、MC命令行、可靠性等自动化测试",
    # py_modules=['flexrunner'],
    python_requires='>=3.5',
    install_requires=read_requirements('requirements.txt', encoding='utf-16'),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    package_data={
        "": ["*.html", '*.css', '*.js', '*.md', '*.ini', '*.xml'],
    },
    entry_points='''
        [console_scripts]
        flexrunner=flexrunner.cli.manage:main
        '''
)

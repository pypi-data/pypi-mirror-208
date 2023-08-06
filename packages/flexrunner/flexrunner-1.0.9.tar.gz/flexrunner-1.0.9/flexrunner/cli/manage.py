#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:manage
@time:2023/2/21
@email:tao.xu2008@outlook.com
@description: 项目管理相关命令
"""
import os
import shutil
import typer
from typing import Optional
from loguru import logger

from flexrunner.config import VERSION, AUTHOR
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from flexrunner import config
from flexrunner.base.models import WebDriverTypeEnum
from flexrunner.core.runners.web.webdriver_manager_extend import ChromeDriverManager


def version_callback(value: bool):
    if value:
        print(f"Version: {VERSION}")
        print(f"Written by: {VERSION}")
        raise typer.Exit()


def public(
        version: Optional[bool] = typer.Option(
            None, "--version", callback=version_callback, help='Show the tool version'
        ),
):
    """公共参数"""
    pass


app = typer.Typer(name="FlexRunner", callback=public, add_completion=False, help="FlexRunner 命令行 CLI.")


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"created folder: {folder_path}")


def create_file(path, file_content=""):
    with open(path, 'w', encoding="utf-8") as py_file:
        py_file.write(file_content)
    msg = f"created file: {path}"
    logger.info(msg)


def create_scaffold(project_name: str) -> None:
    """
    create scaffold with specified project name.
    :param project_name:
    :return:
    """
    if os.path.isdir(project_name):
        logger.info(f"Folder {project_name} already exists, please specify a new project name.")
        return

    logger.info(f"Start to create new test project: {project_name}")
    current_work_dir = os.getcwd()
    project_path = os.path.join(current_work_dir, project_name)
    logger.info(f"Project Path: {project_path}")
    # main.py
    shutil.copy(os.path.join(config.BASE_DIR, "flexrunner", "cli", "main.py"), current_work_dir)

    # reports
    create_folder(os.path.join(current_work_dir, "reports"))
    # demo
    if project_name == "demo":
        shutil.copytree(os.path.join(config.BASE_DIR, "demo"), project_path)
        return

    # project
    create_folder(project_path)
    shutil.copy(os.path.join(config.BASE_DIR, "demo", "__init__.py"), project_path)
    shutil.copy(os.path.join(config.BASE_DIR, "demo", "conftest.py"), project_path)
    shutil.copy(os.path.join(config.BASE_DIR, "demo", "pytest.ini"), project_path)

    # project/conf
    create_folder(os.path.join(project_path, "conf"))

    # project/conf
    create_folder(os.path.join(project_path, "conf"))
    create_file(os.path.join(project_path, "conf", "debug.xml"))
    create_file(os.path.join(project_path, "conf", "global_conf.ini"))
    create_folder(os.path.join(project_path, "conf", "testbed"))
    create_file(os.path.join(project_path, "conf",  "testbed", "testbed_debug.xml"))
    create_folder(os.path.join(project_path, "conf", "testset"))
    create_file(os.path.join(project_path, "conf", "testset", "testset_debug.xml"))

    # project/testdata
    data_sample = '''{
     "example":  [
        ["case1", "dddd"],
        ["case2", "eeee"],
        ["case3", "ffff"]
     ]
    }
    '''
    data_path = os.path.join(project_path, "data")
    create_folder(data_path)
    create_file(os.path.join(data_path, "data_sample.json"), data_sample)

    # project/testcase
    testcase_path = os.path.join(project_path, "testcase")
    create_folder(testcase_path)
    shutil.copy(os.path.join(config.BASE_DIR, "demo", "testcase", "__init__.py"), testcase_path)


def install_driver(browser: str) -> None:
    """
    Download and install the browser driver

    :param browser: The Driver to download. Pass as `chrome/firefox/ie/edge`. Default Chrome.
    :return:
    """

    if browser == "chrome":
        driver_path = ChromeDriverManager().install()
        logger.info(f"Chrome Driver[==>] {driver_path}")
    elif browser == "firefox":
        driver_path = GeckoDriverManager().install()
        logger.info(f"Firefox Driver[==>] {driver_path}")
    elif browser == "ie":
        driver_path = IEDriverManager().install()
        logger.info(f"IE Driver[==>] {driver_path}")
    elif browser == "edge":
        driver_path = EdgeChromiumDriverManager().install()
        logger.info(f"Edge Driver[==>] {driver_path}")
    else:
        raise NameError(f"Not found '{browser}' browser driver.")


@app.command(help='CLI初始化测试项目')
def startapp(
    project: str = typer.Option("demo", "--project", "-p", help="Create a new automation test project"),
    install: WebDriverTypeEnum = typer.Option(..., "--install", "-i", help="install with Web driver type?"),
):
    """FlexRunner startapp 命令行 CLI"""
    if install:
        install_driver(install.value)
        return
    create_scaffold(project)


def main():
    typer.run(startapp)


if __name__ == '__main__':
    main()

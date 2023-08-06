#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:utils
@time:2023/4/7
@email:tao.xu2008@outlook.com
@description: 
"""
import os
import re
import sys
import six
import json
import subprocess
import threading
from io import open
from six import PY3, raise_from, reraise


EXT = ".air"  # script dir extension
DEFAULT_LOG_DIR = "log"  # <script_dir>/log


if PY3:
    def decode_path(path):
        return path
else:
    def decode_path(path):
        return path.decode(sys.getfilesystemencoding()) if path else path


if sys.platform.startswith("win"):
    # Don't display the Windows GPF dialog if the invoked program dies.
    try:
        SUBPROCESS_FLAG = subprocess.CREATE_NO_WINDOW  # in Python 3.7+
    except AttributeError:
        import ctypes
        SEM_NOGPFAULTERRORBOX = 0x0002  # From MSDN
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)  # win32con.CREATE_NO_WINDOW?
        SUBPROCESS_FLAG = 0x8000000
else:
    SUBPROCESS_FLAG = 0


def script_dir_name(script_path):
    """get script dir for old & new cli api compatibility"""
    script_path = os.path.normpath(decode_path(script_path))
    if script_path.endswith(EXT):
        path = script_path
        name = os.path.basename(script_path).replace(EXT, ".py")
    else:
        path = os.path.dirname(script_path) or "."
        name = os.path.basename(script_path)
    return path, name


def script_log_dir(script_path, logdir):
    if logdir is True:
        logdir = os.path.join(script_path, DEFAULT_LOG_DIR)
    elif logdir:
        logdir = decode_path(logdir)
    return logdir


def raisefrom(exc_type, message, exc):
    if sys.version_info[:2] >= (3, 2):
        raise_from(exc_type(message), exc)
    else:
        reraise(exc_type, '%s - %s' % (message, exc), sys.exc_info()[2])


def proc_communicate_timeout(proc, timeout):
    """
    Enable subprocess.Popen to accept timeout parameters, compatible with py2 and py3

    :param proc: subprocess.Popen()
    :param timeout: timeout in seconds
    :return: result of proc.communicate()
    :raises: RuntimeError when timeout
    """
    if sys.version_info[:2] >= (3, 3):
        # in Python 3.3+
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            proc.kill()
            stdout, stderr = proc.communicate()
            exp = RuntimeError("Command {cmd} timed out after {timeout} seconds: stdout['{stdout}'], "
                                    "stderr['{stderr}']".format(cmd=proc.args, timeout=e.timeout,
                                                                stdout=stdout, stderr=stderr))
            raise_from(exp, None)
    else:
        timer = threading.Timer(timeout, proc.kill)
        try:
            timer.start()
            stdout, stderr = proc.communicate()
        finally:
            timer.cancel()
            if proc.returncode > 0:
                raise RuntimeError("Command timed out after {timeout} seconds: stdout['{stdout}'], "
                                   "stderr['{stderr}']".format(timeout=timeout, stdout=stdout, stderr=stderr))
    return stdout, stderr


def get_script_info(script_path):
    """extract info from script, like basename, __author__, __title__ and __desc__."""
    script_path = os.path.normpath(script_path)
    script_name = os.path.basename(script_path)
    if script_path.endswith(".py"):
        pyfilepath = script_path
        parent_name = os.path.basename(os.path.dirname(script_path))
        if parent_name.endswith(EXT):
            script_name = parent_name
    else:
        pyfilename = script_name.replace(EXT, ".py")
        pyfilepath = os.path.join(script_path, pyfilename)

    if not os.path.exists(pyfilepath) and six.PY2:
        pyfilepath = pyfilepath.encode(sys.getfilesystemencoding())
    with open(pyfilepath, encoding="utf-8") as pyfile:
        pyfilecontent = pyfile.read()

    author, title, desc = get_author_title_desc(pyfilecontent)

    result_json = {"name": script_name, "path": script_path, "author": author, "title": title, "desc": desc}
    return json.dumps(result_json)


def get_author_title_desc(text):
    """Get author title desc."""
    regex1 = r'__(?P<attr>\w+)__\s*=\s*(?P<val>"[^"]+"|"""[^"]+""")'
    regex2 = r"__(?P<attr>\w+)__\s*=\s*(?P<val>'[^']+'|'''[^']+''')"
    data1 = re.findall(regex1, text)
    data2 = re.findall(regex2, text)
    data1.extend(data2)
    file_info = dict(data1)
    author = strip_str(file_info.get("author", ""))
    title = strip_str(file_info.get("title", ""))
    desc = strip_str(file_info.get("desc", ""))
    desc = process_desc(desc)
    return author, title, desc


def process_desc(desc):
    lines = desc.split('\n')
    lines = [line.strip() for line in lines]
    return '\n'.join(lines)


def strip_str(string):
    """Strip string."""
    return string.strip('"').strip("'").strip()





if __name__ == '__main__':
    pass

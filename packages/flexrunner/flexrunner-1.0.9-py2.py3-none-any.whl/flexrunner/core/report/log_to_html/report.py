#!/usr/bin/env python
# -*- coding:utf8 -*-
import json
import os
import io
import re
import six
import sys
# from PIL import Image
import shutil
import jinja2
import traceback
from copy import deepcopy
from datetime import datetime
from markupsafe import Markup, escape
try:
    from jinja2 import evalcontextfilter as pass_eval_context  # jinja2<3.1
except:
    from jinja2 import pass_eval_context  # jinja2>=3.1
from loguru import logger
from flexrunner.base.models.log_icon_models import LogIconEnum
from flexrunner.core.report.log_to_html.utils import decode_path, script_dir_name
from six import PY3

DEFAULT_LOG_DIR = "log"
DEFAULT_LOG_FILE = "log.txt"
HTML_TPL = "log_template.html"
HTML_FILE = "log.html"
STATIC_DIR = os.path.dirname(__file__)


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@pass_eval_context
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def time_fmt(timestamp):
    """
    Formatting of timestamp in Jinja2 templates
    :param timestamp: timestamp of steps
    :return: "%Y-%m-%d %H:%M:%S"
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


class LogToHtml(object):
    """Convert log to html display """
    scale = 0.5

    def __init__(self, script_root, log_root="", static_root="", export_dir=None, script_name="", logfile=None, lang="en", plugins=None):
        self.log = []
        self.script_root = script_root
        self.script_name = script_name
        if not self.script_name or os.path.isfile(self.script_root):
            self.script_root, self.script_name = script_dir_name(self.script_root)
        self.log_root = log_root or ST.LOG_DIR or os.path.join(".", DEFAULT_LOG_DIR)
        self.static_root = static_root or STATIC_DIR
        self.test_result = True
        self.run_start = None
        self.run_end = None
        self.export_dir = export_dir
        self.logfile = logfile  #  or getattr(ST, "LOG_FILE", DEFAULT_LOG_FILE)
        self.lang = lang
        self.init_plugin_modules(plugins)

    @staticmethod
    def init_plugin_modules(plugins):
        if not plugins:
            return
        for plugin_name in plugins:
            logger.debug("try loading plugin: %s" % plugin_name)
            try:
                __import__(plugin_name)
            except:
                logger.error(traceback.format_exc())

    @staticmethod
    def _parse_log_line(line):
        """
        解析一行日志内容，返回字典
        :param line:
        :return:
        """
        t, level, msg = line.split("|")
        log = {
            "data": line,
            "time": t.strip(""),
            "level": level.strip(),
            "msg": msg,
            "__children__": []
        }
        return log

    def _load(self):
        """
        读取加载 logfile，按行保存在self.log中
        :return:
        """
        logfile = os.path.join(self.log_root, self.logfile)
        if not PY3:
            logfile = logfile.encode(sys.getfilesystemencoding())
        with io.open(logfile, encoding="utf-8") as f:
            for line in f.readlines():
                # self.log.append(json.loads(line))  # json格式日志
                self.log.append(self._parse_log_line(line))  # 非json格式日志

    def _analyse(self):
        """ 解析log成可渲染的dict """
        case_info = {"name": "", "path": "", "author": "", "title": "", "desc": ""}
        steps = []
        children_steps = []

        for log in self.log:
            if not self.run_start:
                self.run_start = log["time"]
            self.run_end = log["time"]

            msg = log['msg']
            if LogIconEnum.CASE.value in msg:
                # 测试用例
                name, title = re.findall(r"(Case-\d+)：(.*)", msg)[0]
                case_info["name"] = name
                case_info["title"] = title
                case_info["desc"] = title
            elif LogIconEnum.STEP.value in msg:
                # 测试步骤
                step = deepcopy(log)
                if steps:
                    steps[-1]["__children__"] = children_steps
                steps.append(step)
                children_steps = []
            else:
                # 步骤日志
                children_steps.append(log)

        # return case_info, steps
        translated_steps = [self._translate_step(s) for s in steps]
        if len(translated_steps) > 0 and translated_steps[-1].get("traceback"):
            # Final Error
            self.test_result = False
        return case_info, translated_steps

    def _translate_step(self, step):
        """translate single step"""
        name, title = re.findall(r"(Step\d+):(.*)", step["msg"])[0]
        code = self._translate_code(step)
        screen = {}  # self._translate_screen(step, code)
        info = self._translate_info(step)
        assertion = self._translate_assertion(step)

        translated = {
            "title": title,
            "time": step["time"],
            "code": code,
            "screen": screen,
            "desc": "",
            "traceback": info[0],
            "log": info[1],
            "assert": assertion,
        }
        return translated

    def _translate_assertion(self, step):
        if "assert_" in step["msg"]:
            return step["data"]

    def _translate_screen(self, step, code):
        if step['tag'] not in ["function", "info"] or not step.get("__children__"):
            return None
        screen = {
            "src": None,
            "rect": [],
            "pos": [],
            "vector": [],
            "confidence": None,
        }

        for item in step["__children__"]:
            if item["data"]["name"] == "try_log_screen":
                snapshot = item["data"].get("ret", None)
                if isinstance(snapshot, six.text_type):
                    src = snapshot
                elif isinstance(snapshot, dict):
                    src = snapshot['screen']
                    screen['resolution'] = snapshot['resolution']
                else:
                    continue
                if self.export_dir:  # all relative path
                    screen['_filepath'] = os.path.join(DEFAULT_LOG_DIR, src)
                else:
                    screen['_filepath'] = os.path.abspath(os.path.join(self.log_root, src))
                screen['src'] = screen['_filepath']
                self.get_thumbnail(os.path.join(self.log_root, src))
                screen['thumbnail'] = self.get_small_name(screen['src'])
                break

        display_pos = None

        for item in step["__children__"]:
            if item["data"]["name"] == "_cv_match" and isinstance(item["data"].get("ret"), dict):
                cv_result = item["data"]["ret"]
                pos = cv_result['result']
                if self.is_pos(pos):
                    display_pos = [round(pos[0]), round(pos[1])]
                rect = self.div_rect(cv_result['rectangle'])
                screen['rect'].append(rect)
                screen['confidence'] = cv_result['confidence']
                break

        if step["data"]["name"] in ["touch", "assert_exists", "wait", "exists"]:
            # 将图像匹配得到的pos修正为最终pos
            if self.is_pos(step["data"].get("ret")):
                display_pos = step["data"]["ret"]
            elif self.is_pos(step["data"]["call_args"].get("v")):
                display_pos = step["data"]["call_args"]["v"]

        elif step["data"]["name"] == "swipe":
            if "ret" in step["data"]:
                screen["pos"].append(step["data"]["ret"][0])
                target_pos = step["data"]["ret"][1]
                origin_pos = step["data"]["ret"][0]
                screen["vector"].append([target_pos[0] - origin_pos[0], target_pos[1] - origin_pos[1]])

        if display_pos:
            screen["pos"].append(display_pos)
        return screen

    @classmethod
    def get_thumbnail(cls, path):
        """compress screenshot"""
        new_path = cls.get_small_name(path)
        if not os.path.isfile(new_path):
            try:
                img = Image.open(path)
                compress_image(img, new_path, ST.SNAPSHOT_QUALITY, max_size=300)
            except Exception:
                logger.error(traceback.format_exc())
            return new_path
        else:
            return None

    @classmethod
    def get_small_name(cls, filename):
        name, ext = os.path.splitext(filename)
        return "%s_small%s" % (name, ext)

    def _translate_info(self, step):
        trace_msg, log_msg = "", ""
        if "traceback" in step["msg"]:
            # 若包含有traceback内容，将会认定步骤失败
            trace_msg = step["data"]
        else:
            # 普通文本log内容，仅显示
            log_msg = "".join([s['msg'] for s in step["__children__"]])
        return trace_msg, log_msg

    def _translate_code(self, step):
        code = {
            "name": "",
            "args": [],
        }
        return code

    @staticmethod
    def div_rect(r):
        """count rect for js use"""
        xs = [p[0] for p in r]
        ys = [p[1] for p in r]
        left = min(xs)
        top = min(ys)
        w = max(xs) - left
        h = max(ys) - top
        return {'left': left, 'top': top, 'width': w, 'height': h}

    @staticmethod
    def _render(template_name, output_file=None, **template_vars):
        """ 用jinja2渲染html"""
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(STATIC_DIR),
            extensions=(),
            autoescape=True
        )
        env.filters['nl2br'] = nl2br
        env.filters['datetime'] = time_fmt
        template = env.get_template(template_name)
        html = template.render(**template_vars)

        if output_file:
            with io.open(output_file, 'w', encoding="utf-8") as f:
                f.write(html)
            logger.info(output_file)

        return html

    def is_pos(self, v):
        return isinstance(v, (list, tuple))

    def copy_tree(self, src, dst, ignore=None):
        try:
            shutil.copytree(src, dst, ignore=ignore)
        except:
            logger.error(traceback.format_exc())

    def _make_export_dir(self):
        """mkdir & copy /staticfiles/screenshots"""
        # let dirname = <script name>.log
        dirname = self.script_name.replace(os.path.splitext(self.script_name)[1], ".log")
        # mkdir
        dirpath = os.path.join(self.export_dir, dirname)
        if os.path.isdir(dirpath):
            shutil.rmtree(dirpath, ignore_errors=True)

        # copy script
        def ignore_export_dir(dirname, filenames):
            # 忽略当前导出的目录，防止递归导出
            if os.path.commonprefix([dirpath, dirname]) == dirpath:
                return filenames
            return []
        self.copy_tree(self.script_root, dirpath, ignore=ignore_export_dir)
        # copy log
        logpath = os.path.join(dirpath, DEFAULT_LOG_DIR)
        if os.path.normpath(logpath) != os.path.normpath(self.log_root):
            if os.path.isdir(logpath):
                shutil.rmtree(logpath, ignore_errors=True)
            self.copy_tree(self.log_root, logpath, ignore=shutil.ignore_patterns(dirname))
        # if self.static_root is not a http server address, copy static files from local directory
        if not self.static_root.startswith("http"):
            for subdir in ["css", "fonts", "image", "js"]:
                self.copy_tree(os.path.join(self.static_root, subdir), os.path.join(dirpath, "static", subdir))

        return dirpath, logpath

    def get_relative_log(self, output_file):
        """
        Try to get the relative path of log.txt
        :param output_file: output file: log.html
        :return: ./log.txt or ""
        """
        try:
            html_dir = os.path.dirname(output_file)
            if self.export_dir:
                # When exporting reports, the log directory will be named log/ (DEFAULT_LOG_DIR),
                # so the relative path of log.txt is log/log.txt
                return os.path.join(DEFAULT_LOG_DIR, os.path.basename(self.logfile))
            return os.path.relpath(os.path.join(self.log_root, self.logfile), html_dir)
        except:
            logger.error(traceback.format_exc())
            return ""

    def get_console(self, output_file):
        html_dir = os.path.dirname(output_file)
        file = os.path.join(html_dir, 'console.txt')
        content = ""
        if os.path.isfile(file):
            try:
                content = self.readFile(file)
            except Exception:
                try:
                    content = self.readFile(file, "gbk")
                except Exception:
                    content = traceback.format_exc() + content
                    content = content + "Can not read console.txt. Please check file in:\n" + file
        return content

    def readFile(self, filename, code='utf-8'):
        content = ""
        with io.open(filename, encoding=code) as f:
            for line in f.readlines():
                content = content + line
        return content

    def report_data(self, output_file=None, record_list=None):
        """
        Generate data for the report page

        :param output_file: The file name or full path of the output file, default HTML_FILE
        :param record_list: List of screen recording files
        :return:
        """
        self._load()
        case_info, steps = self._analyse()

        if record_list:
            records = [os.path.join(DEFAULT_LOG_DIR, f) if self.export_dir
                       else os.path.abspath(os.path.join(self.log_root, f)) for f in record_list]
        else:
            records = []

        if not self.static_root.endswith(os.path.sep):
            self.static_root = self.static_root.replace("\\", "/")
            self.static_root += "/"

        if not output_file:
            output_file = HTML_FILE

        data = {}
        data['steps'] = steps
        data['name'] = self.script_root
        data['scale'] = self.scale
        data['test_result'] = self.test_result
        data['run_end'] = self.run_end
        data['run_start'] = self.run_start
        data['static_root'] = self.static_root
        data['lang'] = self.lang
        data['records'] = records
        data['info'] = case_info
        data['log'] = self.get_relative_log(output_file)
        data['logfile'] = os.path.basename(self.logfile)
        data['console'] = self.get_console(output_file)
        # 如果带有<>符号，容易被highlight.js认为是特殊语法，有可能导致页面显示异常，尝试替换成不常用的{}
        info = json.dumps(data).replace("<", "{").replace(">", "}")
        data['data'] = info
        return data

    def report(self, template_name=HTML_TPL, output_file=HTML_FILE, record_list=None):
        """
        Generate the report page, you can add custom data and overload it if needed

        :param template_name: default is HTML_TPL
        :param output_file: The file name or full path of the output file, default HTML_FILE
        :param record_list: List of screen recording files
        :return:
        """
        if not self.script_name:
            path, self.script_name = script_dir_name(self.script_root)

        if self.export_dir:
            self.script_root, self.log_root = self._make_export_dir()
            # output_file可传入文件名，或绝对路径
            output_file = output_file if output_file and os.path.isabs(output_file) \
                else os.path.join(self.script_root, output_file or HTML_FILE)
            if not self.static_root.startswith("http"):
                self.static_root = "static/"

        if not record_list:
            record_list = []  # [f for f in os.listdir(self.log_root) if f.endswith(".mp4")]
        data = self.report_data(output_file=output_file, record_list=record_list)
        return self._render(template_name, output_file, **data)


def simple_report(filepath, logpath=True, logfile=None, output=HTML_FILE):
    path, name = script_dir_name(filepath)
    if logpath is True:
        logpath = os.path.join(path, getattr(ST, "LOG_DIR", DEFAULT_LOG_DIR))
    rpt = LogToHtml(path, logpath, logfile=logfile or getattr(ST, "LOG_FILE", DEFAULT_LOG_FILE), script_name=name)
    rpt.report(HTML_TPL, output_file=output)


def get_parger(ap):
    ap.add_argument("script", help="script filepath")
    ap.add_argument("--outfile", help="output html filepath, default to be log.html", default=HTML_FILE)
    ap.add_argument("--static_root", help="static files root dir")
    ap.add_argument("--log_root", help="log & screen data root dir, logfile should be log_root/log.txt")
    ap.add_argument("--record", help="custom screen record file path", nargs="+")
    ap.add_argument("--export", help="export a portable report dir containing all resources")
    ap.add_argument("--lang", help="report language", default="en")
    ap.add_argument("--plugins", help="load reporter plugins", nargs="+")
    ap.add_argument("--report", help="placeholder for report cmd", default=True, nargs="?")
    return ap


def main(args):
    # script filepath
    path, name = script_dir_name(args.script)
    record_list = args.record or []
    log_root = decode_path(args.log_root) or decode_path(os.path.join(path, DEFAULT_LOG_DIR))
    static_root = args.static_root or STATIC_DIR
    static_root = decode_path(static_root)
    export = decode_path(args.export) if args.export else None
    lang = args.lang if args.lang in ['zh', 'en'] else 'en'
    plugins = args.plugins

    # gen html report
    rpt = LogToHtml(path, log_root, static_root, export_dir=export, script_name=name, lang=lang, plugins=plugins)
    rpt.report(HTML_TPL, output_file=args.outfile, record_list=record_list)


if __name__ == "__main__":
    # import argparse
    # ap = argparse.ArgumentParser()
    # args = get_parger(ap).parse_args()
    # main(args)

    path, name = './', 'report.py'
    log_root = "D:\\workspace\\test-runner-flex\\reports\\demo\\000098\\log\\testcase"
    log_file = "test_create_loacl_user_008.log"
    static_root = decode_path(STATIC_DIR)

    rpt = LogToHtml(path, log_root, static_root='./', export_dir=None, script_name=name, logfile=log_file, lang="en", plugins=[])
    rpt.report(HTML_TPL)

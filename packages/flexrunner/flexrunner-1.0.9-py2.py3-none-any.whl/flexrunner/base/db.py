#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:db.py
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import os
import json
from typing import Dict, Text
from loguru import logger

from flexrunner.config import REPORT_DIR
from flexrunner.base.models import ReportSummary, TestCaseInfo
from flexrunner.pkgs.sqlite_opt import Sqlite3Operation
from flexrunner.pkgs.mysql_opt import MysqlOperation


DEFAULT_DB_INFO = {"ENGINE": 'django.db.backends.sqlite3', "NAME": 'db.sqlite3'}


class TestDB(object):
    """数据库初始化"""
    def __init__(self, db_info=None):
        if db_info is None:
            db_info = DEFAULT_DB_INFO
        self.db_info = db_info
        self.db = None
        self.connect()
        self.report_table_name = "base_app_testreport"
        self.testcase_table_name = "base_app_testcase"

    def _report_parse_for_sql(self, report: ReportSummary, filter_keys=None):
        """
        ReportSummary 解析适配插入、更新 SQL：
        UPDATE student SET (id,name) = (?,?) WHERE ID = ?
        """
        if filter_keys is None:
            filter_keys = []
        keys = []
        values = []
        report_dict = report.dict()
        for k, v in report_dict.items():
            if filter_keys and k not in filter_keys:
                continue
            keys.append(k)
            if k in ['time', 'testcases_stat', 'teststeps_stat']:
                values.append(json.dumps(v, indent=0).replace("\n", ""))
            else:
                values.append(v)

        str_keys = ','.join(keys)
        replace_str = '%s' if self.db.__class__.__name__ == 'MysqlOperation' else '?'
        str_values = ', '.join([replace_str for _ in values])
        data = [values]

        return str_keys, str_values, data

    def _testcase_parse_for_sql(self, tc: TestCaseInfo, filter_keys=None, exclude_keys=None):
        """
        TestCaseInfo 解析适配插入、更新 SQL：
        UPDATE student SET (id,name) = (?,?) WHERE ID = ?
        """
        if filter_keys is None:
            filter_keys = []
        if exclude_keys is None:
            exclude_keys = []
        keys = []
        values = []
        tc_dict = tc.dict()
        for k, v in tc_dict.items():
            if filter_keys and k not in filter_keys:
                continue
            if exclude_keys and k in exclude_keys:
                continue
            keys.append(k)
            if k in ['mark_list', 'keyword_list', 'module_list', 'bug_list', 'last_test_time']:
                values.append(json.dumps(v, indent=0, ensure_ascii=False).replace("\n", ""))
            else:
                values.append(v)

        str_keys = ','.join(keys)
        replace_str = '%s' if self.db.__class__.__name__ == 'MysqlOperation' else '?'
        str_values = ', '.join([replace_str for _ in values])
        data = [values]

        return str_keys, str_values, data

    def connect(self):
        """连接数据库"""
        if self.db_info.get('ENGINE') == 'django.db.backends.sqlite3':
            db_path = os.path.join(REPORT_DIR, self.db_info.get('NAME'))
            self.db = Sqlite3Operation(db_path, logger=logger, show=False)
        elif self.db_info.get('ENGINE') == 'django.db.backends.mysql':
            user = self.db_info.get('USER')
            password = self.db_info.get('PASSWORD')
            host = self.db_info.get('HOST')
            port = self.db_info.get('PORT')
            name = self.db_info.get('NAME')
            self.db = MysqlOperation(host, port, user, password, name, logger=logger, show=True)
        else:
            logger.critical("错误的数据库类型，将跳过结果写入！")

    def create_report_table_if_not_exist(self):
        """
        CREATE TABLE IF NOT EXISTS "xxxxx"
        :return:
        """
        sql = '''
        CREATE TABLE IF NOT EXISTS "{}" (
          "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
          "name" varchar(500),
          "description" varchar(4096),
          "status" varchar(50),
          "time" TEXT,
          "testcases_stat" TEXT,
          "teststeps_stat" TEXT,
          "log_path" varchar(2048),
          "report_allure_path" varchar(2048),
          "report_html_path" varchar(2048),
          "jenkins_job_name" varchar(100),
          "jenkins_build_number" integer,
          "allure_url" varchar(500),
          "build_type" varchar(20),
          "build_status" varchar(50),
          "env_id" integer default(0),
          "create_time" datetime,
          "update_time" datetime,
          "delete_time" datetime,
          "is_delete" bool default(0)
          )
        '''.format(self.report_table_name)

        logger.info("CREATE TABLE IF NOT EXISTS \"{}\" ...".format(self.report_table_name))
        self.db.create_table(sql)
        return True

    def create_testcase_table_if_not_exist(self):
        """
        CREATE TABLE IF NOT EXISTS "xxxxx"
        :return:
        """
        sql = '''
        CREATE TABLE IF NOT EXISTS "{}" (
          "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
          "name" varchar(4096),
          "description" varchar(4096),
          "product" varchar(512),
          "story" varchar(512),
          "priority" varchar(100),
          "type" varchar(100),
          "mark_list" TEXT,
          "keyword_list" TEXT,
          "module_list" TEXT,
          "bug_list" TEXT,
        
          "owner" varchar(100),
          "maintainer" varchar(100),
          "status" varchar(100),
          "code_path" varchar(4096),
          "is_delete" integer default(0),
          
          "last_report_id" integer default(0),
          "last_test_status" varchar(100),
          "last_test_time" TEXT,
          "last_test_detail" TEXT
          )
        '''.format(self.testcase_table_name)

        logger.info("CREATE TABLE IF NOT EXISTS \"{}\" ...".format(self.testcase_table_name))
        self.db.create_table(sql)
        return True

    def get_report_last_id(self):
        sql = '''SELECT id FROM {} ORDER BY id DESC LIMIT 1'''.format(self.report_table_name)
        cursor = self.db.execute(sql)
        for row in cursor.fetchall():
            return row[0]
        return 1

    def insert_init_testreport(self, report_id):
        report = ReportSummary()
        report.id = report_id
        str_keys, str_values, data = self._report_parse_for_sql(report)
        sql = '''INSERT INTO {}({})  values ({})'''.format(self.report_table_name, str_keys, str_values)
        self.db.insert_update_delete(sql, data)

    def update_testreport(self, report: ReportSummary, filter_keys=None):
        str_keys, str_values, data = self._report_parse_for_sql(report, filter_keys)
        sql = '''UPDATE {} SET ({}) = ({}) WHERE id = {}'''.format(self.report_table_name, str_keys, str_values, report.id)
        self.db.insert_update_delete(sql, data)

    def insert_update_testcase(self, tc_dict: Dict[Text, TestCaseInfo], filter_keys=None, exclude_keys=None):
        """
        插入/更新测试用例
        :param tc_dict:
        :param filter_keys:
        :param exclude_keys:
        :return:
        """
        for tc_id, tc in tc_dict.items():
            if self.get_testcase(tc.id, ["id"], fetchone=True):
                str_keys, str_values, data = self._testcase_parse_for_sql(tc, filter_keys, exclude_keys)
                sql = '''UPDATE {} SET ({}) = ({}) WHERE id = {}'''.format(self.testcase_table_name, str_keys, str_values, tc.id)
            else:
                str_keys, str_values, data = self._testcase_parse_for_sql(tc, None, exclude_keys)
                sql = '''INSERT INTO {}({})  values ({})'''.format(self.testcase_table_name, str_keys, str_values)
            self.db.insert_update_delete(sql, data)

    def get_report(self, report_id, filter_keys=None):
        if filter_keys is None:
            filter_keys = []
        spec_keys = ",".join(filter_keys) if filter_keys else "*"
        sql = '''SELECT {} FROM {} WHERE id = {}'''.format(spec_keys, self.report_table_name, report_id)
        cursor = self.db.execute(sql)
        rows = cursor.fetchall()
        return rows

    def get_testcase(self, case_id, filter_keys=None, fetchone=False):
        if filter_keys is None:
            filter_keys = []
        spec_keys = ",".join(filter_keys) if filter_keys else "*"
        sql = '''SELECT {} FROM {} WHERE id = {}'''.format(spec_keys, self.testcase_table_name, case_id)
        cursor = self.db.execute(sql)
        if fetchone:
            rows = cursor.fetchone()
        else:
            rows = cursor.fetchall()
        return rows


if __name__ == '__main__':
    pass

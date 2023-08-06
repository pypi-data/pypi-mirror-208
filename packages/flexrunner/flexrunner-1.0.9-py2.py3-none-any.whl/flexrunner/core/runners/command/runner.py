#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner
@time:2022/12/20
@email:tao.xu2008@outlook.com
@description: 命令行测试执行器
"""
import subprocess
import socket
from loguru import logger

from flexrunner.base.models import StepTypeEnum
from flexrunner.pkgs.ssh_mgr import SSHManager


class CmdRunner(SSHManager):
    """命令行测试执行器"""
    step_type = StepTypeEnum.CMD.value  # 约定：指定测试类型，meta_class.py step需要使用
    local_host_ip = socket.gethostbyname(socket.gethostname())

    def __init__(self, ip='', username='root', password=None, key_file=None, port=22, conn_timeout=None):
        super(CmdRunner, self).__init__(ip, username, password, key_file, port, conn_timeout)
        pass

    def local_run(self, cmd, timeout=7200):
        """
        本地执行命令
        :param cmd:
        :param timeout: 等待最大时间
        :return:
        """
        logger.log(self.step_type, f"[{self.local_host_ip}] {cmd}")
        # rc, output = subprocess.getstatusoutput(cmd)

        output = ''
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            for line_o in iter(p.stdout.readline, b''):
                line_o_s = line_o.decode("utf-8", 'ignore')
                output += line_o_s
            for line_e in iter(p.stderr.readline, b''):
                line_e_s = line_e.decode("utf-8", 'ignore')
                output += line_e_s
            p.stdout.close()
            p.stderr.close()
            rc = p.wait(timeout)
        except Exception as e:
            raise Exception('Failed to execute: {0}\n{1}'.format(cmd, e))

        logger.debug(output.strip('\n'))
        return rc, output

    def local_run_poll(self, cmd):
        """
        不等待命令执行完成
        :param cmd:
        :return:
        """
        logger.log(self.step_type, f"[{self.local_host_ip}] {cmd}")
        # rc, output = subprocess.getstatusoutput(cmd)
        try:
            p = subprocess.Popen(cmd, shell=True)
            p.poll()
        except Exception as e:
            raise Exception('Failed to execute: {0}\n{1}'.format(cmd, e))
        return True

    def ssh_run(self, cmd):
        """
        ssh 到远程并执行命令
        :param cmd:
        :return:
        """
        logger.log(self.step_type, f"[{self.ip}] {cmd}")
        return self.ssh_cmd(cmd)

    def run(self, cmd):
        """CMDRunner执行命令"""
        if self.ip:
            return self.ssh_run(cmd)
        else:
            return self.local_run(cmd)


if __name__ == '__main__':
    pass

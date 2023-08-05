#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2017-05-10 20:11:31
modify by: 2017-6-30 15:56:58

功能：实现rsync命令的二次封装，注意：这里封装的是系统命令rsync；
     更加优雅的做法可以尝试Python的fabric模块，该模块提供了rsync的封装rsync_project()。

     注意的是：fabric的rsync_project() 只是一个简单的 rsync 封装，
     关于 rsync 是如何工作的，请阅读它自身的使用手册。
     不管怎么做，为了保证工作正常，你需要保证本地和远程系统中都已安装 rsync。

参考文档：
    https://help.ubuntu.com/community/rsync
    http://fabric-chs.readthedocs.io/zh_CN/chs/tutorial.html
    http://fabric-chs.readthedocs.io/zh_CN/chs/api/contrib/project.html
"""

import subprocess


class RsyncUtil:
    """Rsync, 工具类

    封装系统命令rsync, 调用的是shell命令。
    你需要保证本地和远程系统中都已安装rsync。
    """

    @staticmethod
    def rsync_use_ssh(workspace, source_dir, rsync_user,
                      rsync_ip, target, rsync_port="22"):
        """rsync + ssh

        参数:

            source_dir：Rsync源路径，这里为svn code本地路径; string。
            workspace：Rsync工作路径, 路径任意; string。
            rsync_user: Rsync用户名; string。
            target: Rsync远端路径; string。
            rsync_ip: Rsync IP; string。
            rsync_port: ssh端口，默认为22; int。

        返回:
            status_code, 0 为正常，其他任何数值皆为异常。

        返回类型:
            int
        """
        cmd = ("rsync -e ssh -auvzHP --port=%s %s %s@%s:%s"
               % (rsync_port, source_dir, rsync_user, rsync_ip, target))

        status_code = subprocess.call(cmd, cwd=workspace,
                                      stdout=subprocess.DEVNULL, shell=True)
        return status_code

    @staticmethod
    def rsync_daemon(workspace, source_dir, rsync_user, rsync_ip,
                     rsync_remote_module, rsync_passwd_file, rsync_port="873"):
        """rsync daemon

        参数:

            source_dir：Rsync源路径，这里为svn code本地路径; string。
            workspace：Rsync工作路径, 路径任意;string。
            rsync_user: Rsync用户名; string。
            rsync_passwd_file: 存储rsync密码的文本，PS: 文件权限要为600; string。
            rsync_remote_module： Rsync module; string。
            rsync_ip: Rsync IP; string。
            rsync_port: Rsync端口，默认为873；int。

        返回:
            status_code, 0 为正常，其他任何数值皆为异常。

        返回类型:
            int
        """
        cmd = ("rsync -auvzHP --port=%s %s %s@%s::%s --password-file=%s"
               % (rsync_port, source_dir, rsync_user, rsync_ip,
                  rsync_remote_module, rsync_passwd_file))

        status_code = subprocess.call(cmd, cwd=workspace,
                                      stdout=subprocess.DEVNULL, shell=True)
        return status_code

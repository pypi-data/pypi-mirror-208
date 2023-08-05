#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2018-2-23 14:15:57
modify by: 2021-12-19 17:46:40

功能：各种常用的方法函数的封装。
"""
import os
from pathlib import Path
import shutil
# import gzip
# import tarfile
import stat
from ._strings import PublicUtils

class FileUtils:
    """FileUtils"""
    @staticmethod
    def open_lagre_file(filename:str):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                yield line

    @staticmethod
    def create_folder(str1:str) -> None:
        """创建目录
        
        等同于：

        if not os.path.exists(str1):
            os.makedirs(str1)
        """
        Path(str1).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def copy(src:str, dst:str, ignore=None, dirs_exist_ok=True) -> None:
        """Recursively copy a directory tree.
        The destination directory must not already exist.
        If exception(s) occur, an Error is raised with a list of reasons."""

        if ignore:
            "忽略文件"
            "ignore=shutil.ignore_patterns('*.pyc', 'tmp*')"
            ignore=shutil.ignore_patterns(ignore)

        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=dirs_exist_ok)
        else:
            raise OSError("The target path already exists! After a minute retry ~!")

    @staticmethod
    def get_listfile_01(path:str, natural=False) -> list:
        """递归遍历文件夹, 并返回所有文件list(不含有文件夹)"""
        file_path_list = []
        for root, _, files in os.walk(path):
            file_path_list.extend(os.path.join(root, f) for f in files)

        if natural:
            # # 通常所用的排序函数sort()，是按照string进行比较的
            # files.sort(key= lambda x:int(x[:-4]))
            file_path_list = PublicUtils.natural_sort(file_path_list)
        return file_path_list

    @staticmethod
    def get_listfile_02(path:str, file_type:str=True, dir_type:str=False) -> list:
        """遍历文件夹

        默认返回所有文件list(不含文件夹)；

        当file_type=True, dir_type=False； 则值返回文件列表；

        当file_type=Flase, dir_type=True 则值返文件夹列表；
        """
        if os.path.exists(path):
            file_path_list = []
            dir_path_list = []
            for root, dirs, files in os.walk(path):
                file_path_list.extend(os.path.join(root, f) for f in files)
                dir_path_list.extend(os.path.join(root, d) for d in dirs)
        else:
            raise OSError("The path %s does not exist!" % (path))

        if dir_type is False and file_type is True:
            return file_path_list
        elif dir_type is True and file_type is False:
            return dir_path_list
        elif dir_type is True and file_type is True:
            # return file_path_list + dir_path_list
            return [*file_path_list, *dir_path_list]
        else:
            raise ValueError("The dir_type/file_type is error!")

    @staticmethod
    def chown_user_perm(src:str, dst:str, loop=True) -> None:
        """文件/文件夹权限修改

            当loop等于True的时候,遍历文件夹。
        """
        if loop is True:
            all_list = FileUtils.get_listdir_loop_01(dst)
        else:
            all_list = FileUtils.get_listdir(dst)

        st = os.stat(src)
        if os.path.isdir(dst) and all_list is not None:
            for line in all_list:
                os.chown(line, st[stat.ST_UID], st[stat.ST_GID])
        else:
            raise OSError("The path %s is not exist!" % (dst))

    @staticmethod
    def rename_files(file_lists:list, file_prefix:any, file_suffix:int=None) -> None:
        """批量重命名文件
        
        file_prefix： 文件前缀，xxx-001.py; 默认不设置则保留原样
        file_suffix： 文件后缀，abc-00x.py, 默认不设置则保留原样

        file_lists = ["/root/1.py", "/root/a.py"]

        """
        if file_suffix is None or not str.isdigit(str(file_suffix)):
            uffix = 1
        else:
            uffix = file_suffix

        for f in file_lists:
            file_name, file_ext = os.path.splitext(f)
            if file_prefix is None:
                prefix = file_name
            else:
                prefix = file_prefix
            os.rename(f, prefix + str('{0:03}'.format(uffix)) + file_ext)
            uffix += 1

    @staticmethod
    def rename(old:str, new:str) -> None:
        """重命名"""
        if not Path.exists(new):
            Path.rename(old, new)

# class ZipToFiles:

#     def gzip_to_files(self):
#         with open('file.txt', 'rb') as f_in, gzip.open('file.txt.gz', 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)

#     def tar_to_files(self):
#         pass

#     def tar_zip_to_files(self):
#         pass

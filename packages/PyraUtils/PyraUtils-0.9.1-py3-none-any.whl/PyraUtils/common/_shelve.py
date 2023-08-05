#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path
import shelve

class ShelveUtils:
    """"Shelf" 是一种持久化的类似字典的对象。 """
    @staticmethod
    def set_shelve_value(file_path, key, value, flag='c', writeback=False):
        """写入shelve

        参数flag的取值范围：
        'w'：读写访问
        'c'：读写访问，如果不存在则创建,这个是默认
        'n'：读写访问，总是创建新的、空的数据库文件

        protocol：与pickle库一致
        writeback：为True时，当数据发生变化会回写，不过会导致内存开销比较大
        """

        if not path.isfile(file_path) and flag == "w":
            raise OSError("The file path %s is not exist!!!")

        with shelve.open(file_path, flag=flag, writeback=writeback) as shelf:
            shelf[key] = value


    @staticmethod
    def get_shelve_value(file_path, key, flag='r', writeback=False):
        """读取shelve
    
        参数flag的取值范围：
        'r'：只读打开
        'w'：读写访问
        'c'：读写访问，如果不存在则创建,这个是默认

        protocol：与pickle库一致
        writeback：为True时，当数据发生变化会回写，不过会导致内存开销比较大
        """
        with shelve.open(file_path, flag=flag, writeback=writeback) as shelf:
            try:
                value = shelf[key]
            except KeyError as err:
                raise KeyError('KeyError: {}'.format(err))
            else:
                return value

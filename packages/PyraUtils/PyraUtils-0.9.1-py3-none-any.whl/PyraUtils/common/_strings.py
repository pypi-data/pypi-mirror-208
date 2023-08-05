#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2017-05-10 20:11:31
modify by: 2021-11-25 20:07:46

功能：各种常用的字符串处理方法函数的封装。
"""

import re
import string
import unicodedata
from functools import reduce
from pypinyin import Style, pinyin
from collections import defaultdict


class StringsUtils:
    """PublicUtils, 工具类

    Attributes:

    """
    @staticmethod
    def delete_duplicate(list_dict:any) -> list:
        """python 字典列表/列表套字典 数据去重
        http://www.chenxm.cc/post/508.html?segmentfault
        
        """
        return [dict(t) for t in set([tuple(d.items()) for d in list_dict])]

    @staticmethod
    def multidict(key_values:any) -> list:
        """
        key_values = [('even',2),('odd',1),('even',8),('odd',3),('float',2.4),('odd',7)]

        defaultdict(<class 'list'>, {'float': [2.4], 'even': [2, 8], 'odd': [1, 3, 7]})

        https://ithelp.ithome.com.tw/articles/10193094
        """
        multi_dict = defaultdict(list) 
        for key, value in key_values:
            multi_dict[key].append(value)
        return multi_dict

    @staticmethod
    def str_to_pinyin(str1:str, style=Style.FIRST_LETTER, strict=False) -> str:
        """拼音缩写

        参数:

            str1: 字符串
            style: NORMAL,zhao,TONE,zh4ao,TONE2,zha4o,TONE3,zhao4,\
                   INITIALS,zh,FIRST_LETTER,z,FINALS,ao,FINALS_TONE,\
                   4ao,FINALS_TONE2,a4o,FINALS_TONE3,ao4,BOPOMOFO,\
                   BOPOMOFO_FIRST,CYRILLIC,CYRILLIC_FIRST}
        """
        character_list = pinyin(str1, style=style, strict=strict)      # [[c],[h]]
        return "".join(map(str, reduce(lambda x,y:x+y, character_list)))

    @staticmethod
    def is_empty(str1) -> bool:
        """判空"""
        if str1 is None or str1 == "":
            return True
        return False

    @staticmethod
    def valid_str_is_digit(P) -> bool:
        """
        限制输入数字

        以下為 tk.Tk().register() 的參數說明，
        %d：Type of action (1 for insert, 0 for delete, -1 for focus, forced or textvariable validation)
        %i：index of char string to be inserted/deleted, or -1
        %P：value of the entry if the edit is allowed
        %s：value of entry prior to editing
        %S：the text string being inserted or deleted, if any
        %v：the type of validation that is currently set
        %V：the type of validation that triggered the callback (key, focusin, focusout, forced)
        %W：the tk name of the widget
        
        https://shengyu7697.github.io/python-tkinter-entry-number-only/
        """
        if str.isdigit(P) or P == '':
            return True
        else:
            return False

    @staticmethod
    def valid_str_01(name:str) -> str:
        """
        Return the given string converted to a string that can be used for a clean
        filename. Remove leading and trailing spaces; convert other spaces to
        underscores; and remove anything that is not an alphanumeric, dash,
        underscore, or dot.
        >>> get_valid_filename("john's portrait in 2004.jpg")
        'johns_portrait_in_2004.jpg'

        https://github.com/django/django/blob/main/django/utils/text.py

        """
        s = str(name).strip().replace(' ', '_')
        s1 = re.sub(r'(?u)[^-\w.]', '', s)
        if s1 in {'', '.', '..'}:
            raise ValueError("Could not derive file name from '%s'" % name)
        return s1

    @staticmethod
    def valid_str_02(name:str) -> str:
        """
        In [45]: valid_filename_02("陈aaa ll%.jpg") -> Out[45]: 'aaall.jpg'
        In [44]: valid_filename_02("aaa ll%.jpg")   -> Out[44]: 'aaall.jpg'
        """
        try:
            # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.
            # safechars = string.ascii_letters + string.digits + " -_."

            # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.
            safechars = string.ascii_letters + string.digits + "-_."
            return "".join(filter(lambda c: c in safechars, name))
        except:
            raise ValueError("Could not derive file name from '%s'" % name) 

    @staticmethod
    def slugify(value:str, allow_unicode=False) -> str:
        """
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.

        https://github.com/django/django/blob/main/django/utils/text.py

        In [20]: slugify("陈 ll%.jpg")  --> In [20]: slugify("陈 ll%.jpg")
        In [22]: slugify("aaa ll%.jpg", allow_unicode=True)  --> Out[23]: '陈aaa-lljpg'
        """
        if allow_unicode:
            value_1 = unicodedata.normalize('NFKC', str(value))
        else:
            value_1 = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value_2 = re.sub(r'[^\w\s-]', '', value_1.lower())
        return re.sub(r'[-\s]+', '-', value_2).strip('-_')

    @staticmethod
    def natural_sort(value:list) -> list: 
        """自然排序
        
        https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
        """
        convert = lambda x: int(x) if x.isdigit() else x.lower() 
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(value, key=alphanum_key)


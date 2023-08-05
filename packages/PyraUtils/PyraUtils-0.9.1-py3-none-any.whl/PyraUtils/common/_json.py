#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2021-12-02 18:02:15
modify by: 2021-12-02 18:02:18

功能：json函数的封装。
"""

import json
from json import JSONDecodeError

class JsonUtils:
    """JsonUtils, 工具类

    Attributes:

        dumps是将dict转化成str格式，loads是将str转化成dict格式。

        dump和load也是类似的功能，只是与文件操作结合起来了。
    """
    @staticmethod
    def load_json_file(json_path:str) -> json:
        """加载json文件"""
        with open(json_path, "r", encoding="utf8")  as frs:
            res = json.load(frs)
        return res

    @staticmethod
    def set_json_file(value:str, json_path:str, ensure_ascii=False) -> None:
        """json数据写入文件"""
        if not JsonUtils.is_json(value):
            raise ValueError("The format is not json.")

        res = json.dumps(value, ensure_ascii=ensure_ascii)
        with open(json_path, "w", encoding="utf8")  as fws:
            fws.write(res)

    @staticmethod
    def get_json_file_value(json_path:str, key:str) -> json:
        """根据key获取json文件中的value"""
        with open(json_path, "r", encoding="utf8")  as frs:
            res = json.load(frs)

        try:
            return res[key]
        except KeyError as err:
            raise KeyError("The key is not error %s." % (err))

    @staticmethod
    def set_json_file_value(json_path:str, key:str, value:str) -> None:
        """根据key修改json文件中的value"""
        with open(json_path, "r", encoding="utf8")  as frs:
            res = json.load(frs)
        res[key] = value
        result = json.dumps(res, indent=4, sort_keys=True, ensure_ascii=False).replace("'", "\"")
        with open(json_path, "r", encoding="utf8")  as fws:
            fws.write(result)

    @staticmethod
    def loads_json_value(value:str) -> str:
        """字符串转json"""
        try:
            json_data = json.loads(value)  
        except (ValueError, TypeError, JSONDecodeError) as err:
            json_data = json.loads(json.dumps(value))
        finally:
            return json_data

    @staticmethod
    def is_json(value:str) -> bool:
        """判断数据是否是json"""
        try:
            json.loads(value)  
        except (ValueError, TypeError, JSONDecodeError) as err:
            # raise ("The format is not json. msg: %s" % (err))
            return False
        else:
            return True
        

if __name__ == "__main__":
    pass

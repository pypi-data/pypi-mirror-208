#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2018-4-16 20:59:0
modify by: 2021-12-03 15:24:33

功能：generate nonce or signature
"""
import uuid
import random
import hmac
import hashlib
import base64

class GenerateNonceUtil:
    """"generate Nonce"""
    def gen_nonce_use_random(self, length=8):
        """Generate pseudorandom number."""
        # https://stackoverflow.com/questions/31848293/python3-and-hmac-how-to-handle-string-not-being-binary?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        return int(''.join([str(random.randint(0, 9)) for i in range(length)]))
    
    def gen_nonce_use_uuid1(self):
        """uuid1 creates a unique key based on host and time"""
        return str(uuid.uuid1())

class GenerateEncryptionUtil:
    """"加密"""
    def gen_hmac_shax(self, secretKey, msg, digestmod="HmacSHA1"):
        """Python实现的PHP hash_hmac"""
        # PHP hash_hmac与python hmac sha1匹配
        # https://blog.csdn.net/ligongxiang123/article/details/76590196

        # 因为不同语言，对应加密的规则有些许不同。

        # 1.首先双方基本算法需要一致，这里都以sha1为基本规则
        # 2.python部分，如果是使用digest（）输出，php部分则一定要使用原始二进制数据输出。
        #     python: hmac.new('test', 'test', hashlib.sha1).digest()
        #     php: hash_hmac('sha1','test','test',true);

        # 3.python部分如果是使用hexdigest()输出，则php部分去掉最后一个raw数据参数即可匹配。
        #     python: hmac.new('test', 'test', hashlib.sha1).hexdigest()
        #     php: hash_hmac('sha1','test','test');

        if digestmod == "HmacSHA1" or digestmod == "HMAC-SHA1":
            data_bytes = hmac.new(secretKey.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha1).digest()
        elif digestmod == "HmacSHA256":
            data_bytes = hmac.new(secretKey.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256).digest()
        else:
            data_bytes =  hmac.new(secretKey.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha1).digest()
        signature = base64.b64encode(data_bytes)
        return signature

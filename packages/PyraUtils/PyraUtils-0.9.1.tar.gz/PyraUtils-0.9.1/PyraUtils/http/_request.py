# -*- coding: utf-8 -*-

"""
created by：2017-05-10 20:11:31
modify by: 2021-12-07 23:21:32

功能：requests二次封装，常用的get,post,head,delete方法封装。
     这个是第三方库，使用提前需要pip install requests

参考文档:
    http://docs.python-requests.org/zh_CN/latest/user/quickstart.html
    http://docs.python-requests.org/zh_CN/latest/user/advanced.html
    http://docs.python-requests.org/zh_CN/latest/api.html
    http://docs.python-requests.org/zh_CN/latest/_modules/requests/api.html
"""

import requests


class RequestsBasiceUtil:
    """requests二次封装，常用的get,post,head,delete方法封装，工具类。"""

    @staticmethod
    def req_method(method:str, url:str, **kwargs) -> requests.Response:
        """Sends request.

        参数:

            method: - ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
            url – 新建 Request 对象的URL
            params – (可选) Request 对象的查询字符中要发送的字典或字节内容
            data – (可选) Request 对象的 body 中要包括的字典、字节或类文件数据
            json – (可选) Request 对象的 body 中要包括的 Json 数据
            headers – (可选) Request 对象的字典格式的 HTTP 头
            cookies – (可选) Request 对象的字典或 CookieJar 对象
            files – (可选)字典，'name':file-like-objects(或{'name':('filename',fileobj)})用于上传含多个部分的（类）文件对象
            auth – (可选) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
            timeout (浮点或元组) – (可选) 等待服务器数据的超时限制，是一个浮点数，或是一个(connect timeout, read timeout)元组
            allow_redirects (bool) – (可选) Boolean. True 表示允许跟踪 POST/PUT/DELETE 方法的重定向
            proxies – (可选) 字典，用于将协议映射为代理的URL
            verify – (可选) 为 True 时将会验证 SSL 证书，也可以提供一个 CA_BUNDLE 路径
            stream – (可选) 如果为 False，将会立即下载响应内容
            cert – (可选) 为字符串时应是 SSL 客户端证书文件的路径(.pem格式)，如果是元组，就应该是一个(‘cert’, ‘key’) 二元值对

        返回:
            Response object

        返回类型:
            requests.Response
        """
        try:
            resp = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.HTTPError,
                requests.Timeout, requests.URLRequired) as err:
            raise RuntimeError(err)
        return resp


class RequestsSessionUtil:
    """Request ssession方法封装，额外提供 cookie 的存储，连接池和配置"""

    def __init__(self, max_retries:int=5, proxies:any={}):
        """
        max_retries: 最大重试次数
        proxies： 代理池
        """
        self.max_retries = max_retries
        self.proxies = proxies

    def session_method(self, method:str, url:str, **kwargs) -> requests.Response:
        """Sends request.

        参数:

            url – 新建 Request 对象的URL.
            method: - ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
            params – (可选) Request 对象的查询字符中要发送的字典或字节内容。
            data – (可选) Request 对象的 body 中要包括的字典、字节或类文件数据
            json – (可选) Request 对象的 body 中要包括的 Json 数据
            headers – (可选) Request 对象的字典格式的 HTTP 头
            cookies – (可选) Request 对象的字典或 CookieJar 对象
            files – (可选)字典，'name':file-like-objects(或{'name':('filename',fileobj)})用于上传含多个部分的（类）文件对象
            auth – (可选) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
            timeout (浮点或元组) – (可选) 等待服务器数据的超时限制，是一个浮点数，或是一个(connect timeout, read timeout)元组
            allow_redirects (bool) – (可选) Boolean. True 表示允许跟踪 POST/PUT/DELETE 方法的重定向
            proxies – (可选) 字典，用于将协议映射为代理的URL
            verify – (可选) 为 True 时将会验证 SSL 证书，也可以提供一个 CA_BUNDLE 路径
            stream – (可选) 如果为 False，将会立即下载响应内容
            cert – (可选) 为字符串时应是 SSL 客户端证书文件的路径(.pem格式)，如果是元组，就应该是一个(‘cert’, ‘key’) 二元值对
            proxies - { 'http': 'http://10.10.1.10:3128', 'https': 'http://10.10.1.10:1080',}

        返回:
            Response object

        返回类型:
            requests.Response
        """
        with requests.Session() as s:
            max_retries = requests.adapters.HTTPAdapter(max_retries=self.max_retries)
            s.mount('https://', max_retries)
            s.mount('http://', max_retries)
            resp = s.request(method, url, **kwargs)
        return resp


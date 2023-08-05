# -*- coding: utf-8 -*-

"""
created by：2021-11-25 14:21:41
modify by: 2021-12-02 19:53:33

功能：httpx二次封装，常用的get,post,head,delete方法封装。
     这个是第三方库，使用提前需要pip install httpx

参考文档:
    https://github.com/encode/httpx
    https://www.python-httpx.org/
"""

import httpx

class httpxBasiceUtil:
    """httpx二次封装，常用的get,post,head,delete方法封装，工具类。"""

    @staticmethod
    def httpx_method(method:str, url:str, **kwargs) -> httpx.Response:
        """Sends a request.

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
            httpx.Response
        """

        try:
            resp = httpx.Request(method, url, **kwargs)
        except (httpx.ConnectError, httpx.HTTPError, httpx.ProtocolError,
                httpx.InvalidURL, httpx.TimeoutException, httpx.NetworkError,
                httpx.ProxyError) as err:
            raise RuntimeError(err)
        return resp


class httpxClientUtil:
    """httpx连接池二次封装，异步支持;常用的get,post,head,delete方法封装，工具类。"""

    def __init__(self, http2:bool=False, proxies=None,  timeout=5.0,
                max_keepalive=20, max_connections=100, keepalive_expiry:float=5.0) -> None:
        """
        http2: 启用 HTTP/2 支持的客户端
        proxies： 代理地址
        max_keepalive，允许保持活动连接的数量，或None始终允许。（默认 20）
        max_connections、最大允许连接数或None无限制。（默认 100）
        keepalive_expiry: 浮点， 默认为5.0
        timeout: 超时时间，如果填‘None’，则默认禁止
        """
        self.http2 = http2
        self.proxies = proxies
        self.timeout = timeout
        self.limits = httpx.Limits(max_keepalive_connections=max_keepalive,
                                   max_connections=max_connections,
                                   keepalive_expiry=keepalive_expiry)

    def httpx_method(self, method, url, **kwargs) -> httpx.Response:
        with httpx.Client(http2=self.http2, proxies=self.proxies,
                          timeout=self.timeout, limits=self.limits) as client:
            resp = client.request(method, url, **kwargs)
        return resp


    async def async_method(self, method, url, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(http2=self.http2, proxies=self.proxies,
                                     timeout=self.timeout, limits=self.limits) as client:
            resp = await client.request(method, url, **kwargs)
        return resp


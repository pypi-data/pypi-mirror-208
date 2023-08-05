#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2018-2-23 14:15:57
modify by: 2021-12-03 15:05:05

功能：各种常用的方法函数的封装。
"""

import urllib3
from contextlib import closing
import requests
import httpx
import rich.progress
from tqdm import tqdm

from loguru import logger

class DownloadUtil:
    """DownloadUtil, 工具类

    Attributes:

    """

    @staticmethod
    def dl_01(url:str, dl_path:str, **kwargs) -> None:
        '''
        使用requests实现下载
        '''
        with open(dl_path, "wb") as f:
            try:
                resp = requests.get(url, kwargs)
                f.write(resp.content)
            except (requests.HTTPError, requests.Timeout,
                    requests.exceptions.URLRequired) as err:
                logger.error(err)

    @staticmethod
    def dl_02(url:str, dl_path:str, **kwargs) -> None:
        '''
        使用urllib3实现下载
        '''
        # 创建连接池管理器
        http = urllib3.PoolManager()
         # 发送请求并获取响应
        response = http.request('GET', url, kwargs)
        # 读取响应内容并保存到文件中
        with open(dl_path, 'wb') as f:
            f.write(response.data)


    @staticmethod
    def dl_03(url:str, dl_path:str, **kwargs) -> None:
        '''
        使用requests实现下载,同时增加对特定情况下的判断
        '''
        with closing(requests.get(url, kwargs)) as resp:
            # 判断下载链接是否异常
            resp_code = resp.status_code
            if 299 < resp_code or resp_code < 200:
                logger.warning('returnCode %s %s' % (resp_code, url))

            # 判断下载文件是否为0
            content_length = int(resp.headers.get('content-length', '0'))
            if content_length == 0:
                logger.warning('size0 %s' % url)

            try:
                with open(dl_path, 'wb') as f:
                    for data in resp.iter_content(1024):
                        f.write(data)
            except Exception as err:
                logger.error('Savefail %s, %s' % (url, err))

    @staticmethod
    def dl_04(url:str, dl_path:str, chunk_size=512 * 1024, **kwargs) -> None:
        '''
        使用requests实现下载,大文件专用
        '''
        with open(dl_path, "wb") as f:
            try:
                resp = requests.get(url, kwargs)
                for chunk in resp.iter_content(chunk_size=chunk_size): 
                    f.write(chunk)
            except (requests.HTTPError, requests.Timeout,
                    requests.exceptions.URLRequired) as err:
                logger.error(err)

class DownloadProgressUtil:
    """DownloadProgressUtil, 工具类

    Attributes:

    """
    @staticmethod
    def dl_01(url, dl_path, **kwargs):
        '''
        进度条
        '''
        with open(dl_path, 'wb', kwargs) as out_file:
            with httpx.stream("GET", url) as resp:
                total = int(resp.headers["Content-Length"])

                with tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B") as progress:
                    num_bytes_downloaded = resp.num_bytes_downloaded
                    for chunk in resp.iter_bytes():
                        out_file.write(chunk)
                        progress.update(resp.num_bytes_downloaded - num_bytes_downloaded)
                        num_bytes_downloaded = resp.num_bytes_downloaded


    @staticmethod
    def dl_02(url, dl_path, **kwargs):
        '''
        使用rich实现进度条
        '''
        with open(dl_path, 'wb') as out_file:
            with httpx.stream("GET", url, kwargs) as resp:
                total = int(resp.headers["Content-Length"])

                with rich.progress.Progress(
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    rich.progress.BarColumn(bar_width=None),
                    rich.progress.DownloadColumn(),
                    rich.progress.TransferSpeedColumn(),) as progress:
                    download_task = progress.add_task("Download", total=total)
                    for chunk in resp.iter_bytes():
                        out_file.write(chunk)
                        progress.update(download_task, completed=resp.num_bytes_downloaded)


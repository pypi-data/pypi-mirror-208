# -*- coding: utf-8 -*-

"""
created by：2017-01-10 20:11:31
modify by: 2021-12-06 22:11:17

功能：logging模块常用两种日志轮询方法的封装。
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class LoggingHandler(logging.Logger):
    """logging 日志轮询二次封装，工具类
    
    Doc: https://docs.python.org/3/howto/logging-cookbook.html
    """
    def __init__(self, stream=True, file=True, size_rollback=False,
                max_bytes=10*1024*1024, rotating_time="D",
                encoding="utf-8", level="NOTSET", backup_count=5):
        """
        stream:是否输出到控制台
        file:是否保存到文件
        size_rollback: 为False的时候，默认启用时间回滚；为True的时候，默认是文件大小存储
        max_bytes： 如果开启文件大小回滚时，则该值生效
        rotating_time：  如果开启按照时间回滚时，则该值生效。S - Seconds/M - Minutes/ H - Hours/ D - Days / W{0-6} - roll over on a certain day; 0 - Monday
        level：日志级别；CRITICAL/FATAL/CRITICAL/ERROR/WARN/WARNING/INFO/DEBUG/NOTSET
        """
        self.encoding = encoding
        self.stream = stream
        self.file = file
        self.max_bytes = max_bytes
        self.rotating_time = rotating_time
        self.backup_count = backup_count
        self.size_rollback = size_rollback
        self.name = None
        super().__init__(name=self.name, level=level)

    def set_name(self, filename='default.log', name='', log_format=None, log_datefmt=None):
        """
        filename：保存的文件名
        name:日志名字
        log_format: 日志格式
        log_datefmt： 时间格式
        """
        self.name = name
        # 设置输出格式，依次为，线程，时间，名字，信息。
        if log_format is None:
            self.fmt = '%(asctime)8s | %(levelname)8s | %(name)5s - %(threadName)8s:%(filename)5s:%(funcName)s:%(lineno)d - %(message)s'
        else:
            self.fmt = log_format

        # 设置时间格式
        if log_datefmt is None:
            self.datefmt = '%Y-%m-%d %H:%M:%S'
        else:
            self.datefmt = log_datefmt

        # 解决重复输出的问题
        if self.handlers:
            return
        else:
            if self.stream:
                self.__set_stream_handler__()

            if self.file:
                self.__set_file_handler__(filename)
            
    def __set_file_handler__(self, filename):
        """
        设置输出文件
        """
        if self.size_rollback:
            # 按照日志大小切割
            file_handler = RotatingFileHandler(filename=filename, maxBytes=self.max_bytes,
                                    backupCount=self.backup_count, encoding=self.encoding)
        else:
            # 按照时间切割
            file_handler = TimedRotatingFileHandler(filename=filename, when=self.rotating_time,
                                    backupCount=self.backup_count, encoding=self.encoding)
        file_handler.setLevel(self.level)
        formatter = logging.Formatter(fmt=self.fmt, datefmt=self.datefmt)
        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)

    def __set_stream_handler__(self):
        """
        设置控制台输出
        """
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(self.fmt)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(self.level)
        self.addHandler(stream_handler)

if __name__ == '__main__':
    pass

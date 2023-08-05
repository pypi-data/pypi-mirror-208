# -*- coding: utf-8 -*-

"""
created by：2017-01-10 20:11:31
modify by: 2018-1-16 14:49:22

功能：logging模块常用两种日志轮询方法的封装。
"""

import logging
from logging.config import fileConfig
from logging import StreamHandler
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class LoggingFileHandler:
    """logging 日志轮询二次封装，工具类 """
    @staticmethod
    def size_rotating_file_handler(logfile, username, log_format=None, log_encoding=None,
                                   log_datefmt=None, max_bytes=10*1024*1024,
                                   level=logging.INFO, backup_count=5):
        """根据文件大小切割日志"""

        # 设置日志格式
        if log_format is None:
            log_format = '%(asctime)-8s - %(name)5s: %(filename)5s  %(levelname)-8s %(message)s'

        # 设置时间格式
        if log_datefmt is None:
            log_datefmt = '%Y-%m-%d %H:%M:%S'

        # 生成一个日志对象
        logger = logging.getLogger(username)
        # 设置日志级别
        logger.setLevel(level)
        log_formatter = logging.Formatter(fmt=log_format, datefmt=log_datefmt)

        rthandler = RotatingFileHandler(logfile, maxBytes=max_bytes,
                                        backupCount=backup_count, encoding=log_encoding)
        rthandler.setFormatter(log_formatter)
        logger.addHandler(rthandler)

        console_handler = StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
        return logger

    @staticmethod
    def timed_rotating_file_handler(logfile, username, log_format=None, log_encoding=None,
                                    log_datefmt=None, rotating_time="midnight",
                                    level=logging.INFO, backup_count=5):
        """根据时间切割日志"""

        # 设置日志格式
        if log_format is None:
            log_format = '%(asctime)-8s - %(name)5s: %(filename)5s  %(levelname)-8s %(message)s'
        # 设置时间格式
        if log_datefmt is None:
            log_datefmt = '%Y-%m-%d %H:%M:%S'

        # 生成一个日志对象
        logger = logging.getLogger(username)
        # 设置日志级别
        logger.setLevel(level)
        log_formatter = logging.Formatter(fmt=log_format, datefmt=log_datefmt)

        trthandler = TimedRotatingFileHandler(logfile, when=rotating_time,
                                              backupCount=backup_count, encoding=log_encoding)
        trthandler.setFormatter(log_formatter)
        logger.addHandler(trthandler)

        console_handler = StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
        return logger

if __name__ == '__main__':
    # fileConfig('logging_config.ini')
    # logger = logging.getLogger()
    # logger.debug('often makes a very good meal of %s', 'visiting tourists')

    # #logger_main = logging.getLogger('main')
    # #logger_main.debug('often makes a very good meal of %s', 'visiting tourists')
    pass

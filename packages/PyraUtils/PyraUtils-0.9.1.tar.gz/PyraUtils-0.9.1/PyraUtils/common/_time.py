# -*- coding: utf-8 -*-
"""
created by：2022-07-29 16:17:18
modify by: 2022-08-01 18:51:42
功能：时间相关的函数封装
"""

import datetime
from calendar import timegm

class TimeUtils:

    @staticmethod
    def datetime_strftime_now(tz_info:str="Asia/Shanghai", strftime:str="%Y-%m-%d %H:%M:%S") -> str:
        """
        Returns an aware or naive datetime.datetime, depending on settings.tz_info.
        """
        try:
            import pytz
        except ImportError as e:
            raise ImportError('e')

        if tz_info:
            # timeit shows that datetime.now(tz=utc_info) is 24% slower
            utc_info = pytz.timezone('UTC')
            as_info = pytz.timezone(tz_info)
            return datetime.datetime.utcnow().replace(tzinfo=utc_info).astimezone(as_info).strftime(strftime)
        else:
            return datetime.datetime.now().strftime(strftime)

    @staticmethod
    def timegm_timestamp(value:datetime) -> int:
        '''uninx时间戳转换'''
        # return timegm(datetime.datetime.now(tz=datetime.timezone.utc).utctimetuple())
        return timegm(value.utctimetuple())

    @staticmethod
    def datetime_utc_now(date_type:str="seconds", tz="", timedelta:int="") -> datetime:
        """
        返回 UTC时间的偏移量 例如
            In [15]: datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=111)
            Out[15]: datetime.datetime(2022, 8, 1, 10, 48, 17, 464785, tzinfo=datetime.timezone.utc)

            In [16]: datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=0)
            Out[16]: datetime.datetime(2022, 8, 1, 10, 46, 28, 592419, tzinfo=datetime.timezone.utc)

        如果timedelta为空，则默认为当前的UTC时间
        """
        if timedelta and date_type.lower() == "milliseconds":
            datetime_timedelta = datetime.timedelta(milliseconds=timedelta)
        if timedelta and date_type.lower() == "microseconds":
            datetime_timedelta = datetime.timedelta(microseconds=timedelta)
        if timedelta and date_type.lower() == "seconds":
            datetime_timedelta = datetime.timedelta(seconds=timedelta)
        elif timedelta and date_type.lower() == "minutes":
            datetime_timedelta = datetime.timedelta(minutes=timedelta)
        elif timedelta and date_type.lower() == "hours":
            datetime_timedelta = datetime.timedelta(hours=timedelta)
        elif timedelta and date_type.lower() == "days":
            datetime_timedelta = datetime.timedelta(days=timedelta)
        else:
            datetime_timedelta = datetime.timedelta(seconds=0)
 
        return datetime.datetime.now(tz=datetime.timezone.utc) + datetime_timedelta

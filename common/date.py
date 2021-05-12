# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask_restful import fields
import time


class Date(object):
    @classmethod
    def today_date(cls):
        return datetime(year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day)

    @classmethod
    # 把datetime转成字符串
    def datetime_toString(cls, dt, with_time=True, date_separator=''):
        if with_time:
            return dt.strftime("%Y" + date_separator + "%m" + date_separator + "%d %H:%M:%S")
        else:
            return dt.strftime("%Y" + date_separator + "%m" + date_separator + "%d")

    @classmethod
    # 获取当前时间戳
    def current_timestamp(cls):
        return int(cls.datetime_toTimestamp(datetime.now()))

    @classmethod
    # 把字符串转成datetime
    def string_toDatetime(cls, string):
        return datetime.strptime(string, "%Y%m%d %H:%M:%S")

    @classmethod
    # 把字符串转成时间戳形式
    def string_toTimestamp(cls, strTime):
        return int(time.mktime(cls.string_toDatetime(strTime).timetuple()))

    @classmethod
    #把时间戳转成字符串形式
    def timestamp_toString(cls, stamp):
        return time.strftime("%Y%m%d %H:%M:%S", time.localtime(stamp))

    @classmethod
    # 把时间戳转成Datatime
    def timestamp_toDatetime(cls, stamp):
        return datetime.fromtimestamp(stamp)

    @classmethod
    # 把datetime类型转成时间戳形式
    def datetime_toTimestamp(cls, dateTim):
        return int(time.mktime(dateTim.timetuple()))

    @classmethod
    # dt类型运算
    def datetime_calculate(cls, dt, seconds=0):
        return dt + timedelta(seconds=seconds)


class FieldDatetimeToTimestamp(fields.Raw):
    # 把datetime类型转成时间戳形式
    def format(self, value):
        return time.mktime(value.timetuple())

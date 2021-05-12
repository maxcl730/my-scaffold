# -*- coding: utf-8 -*-
from flask_restful import fields
from common.date import Date

SEX = [
    (0, '未知'),
    (1, '男'),
    (2, '女'),
]

STATUS = [(100, '全部'),
          (1, '允许'),
          (2, '禁用')]


RUNNING_STATUS = [
    (100, '全部'),
    (0, '未开始'),
    (1, '申请中'),
    (2, '申请结束')
]

RUNNING_STATUS_WITH_APPLICATION = [
    (100, '全部'),
    (1, '申请中'),
    (2, '申请结束')
]

PUBLISH_STATUS = [
    (100, '全部'),
    (0, '未发布'),
    (1, '已发布'),
    (2, '发布申请名单'),
]


GOOD_STANDARD = [
    (0, '选择规格'),
    (1, '正装'),
    (2, '中样'),
    (3, '小样'),
    (4, '套装'),
]

APPLICATION_STATUS = [
    (100, '全部'),
    (0, '未审核'),
    (1, '审核通过'),
    (2, '已发货'),
    # (3, '已交报告'),
    (4, '审核未通过'),
    (99, '不展示'),
]

REPORT_STATUS = [
    (100, '全部'),
    (0, '未审核'),
    (1, '通过并发布'),
    (2, '不通过驳回')
]

# 邀请次数换算使用机会
INVITATION_TO_POINT = {
    1: 1,
    2: 2,
    3: 2,
    4: 0,
    5: 5,
}

# 省份列表
PROVINCE_LIST = [
    ('全部', '全部'),
    ('北京市', '北京市'),
    ('上海市', '上海市'),
    ('广东省', '广东省'),
    ('深圳市', '深圳市'),
]


def good_standard_desc(value=0):
    for n in GOOD_STANDARD:
        if n[0] == int(value):
            return n[1]
    return '未知'


def application_status_desc(status=0):
    for n in APPLICATION_STATUS:
        if n[0] == int(status):
            return n[1]
    return '未知'


def report_status_desc(status=0):
    for n in REPORT_STATUS:
        if n[0] == int(status):
            return n[1]
    return '未知'


class StandardValue(fields.Raw):
    def format(self, value):
        for n in GOOD_STANDARD:
            if n[0] == int(value):
                return n[1]
        return '未知'


class TimestampValue(fields.Raw):
    def format(self, value):
        return Date.datetime_toTimestamp(value)

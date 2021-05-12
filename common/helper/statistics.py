# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from trialcenter.models.member import Member, Application, Report, Trial
from extensions import cache
from common.date import Date
from common import Log


class Statistics(object):

    @classmethod
    @cache.memoize(timeout=300)
    def all_member_count(cls):
        # 新增会员数
        count = Member.objects().count()
        return count

    @classmethod
    @cache.memoize(timeout=300)
    def new_member_count(cls, date=Date.today_date()):
        # 新增会员数
        begin_date = date
        end_date = date + timedelta(days=1)
        count = Member.objects(created_time__gte=begin_date, created_time__lt=end_date).count()
        return count

    @classmethod
    @cache.memoize(timeout=300)
    def new_application_count(cls, date=Date.today_date()):
        # 新增申请数
        begin_date = date
        end_date = date + timedelta(days=1)
        count = Application.objects(created_time__gte=begin_date, created_time__lt=end_date).count()
        return count

    @classmethod
    @cache.memoize(timeout=300)
    def noaudit_report_count(cls):
        # 未审核报告数
        count = Report.objects(status=0).count()
        return count

    @classmethod
    @cache.memoize(timeout=300)
    def trial_visitors(cls, data_type='sum'):
        # 活动访问量 average-平均， sum-总和， max-最大
        count = 0
        if data_type == 'sum':
            count = Trial.objects.sum('visit_num_real')
        elif data_type == 'average':
            count = Trial.objects.average('visit_num_real')

        return count

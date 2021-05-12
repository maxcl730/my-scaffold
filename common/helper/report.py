# -*- coding: utf-8 -*-
from trialcenter.models.member import Report
from bson.objectid import ObjectId
from flask_restful import fields
from extensions import cache
from common.date import Date
from common import Log


@cache.memoize(timeout=120)
def get_report_member_data(trial_id='', number=5):
    if len(trial_id) == 24:
        all_reports = Report.objects(trial=ObjectId(trial_id), status=1).only('member', 'created_time').order_by('-created_time')
        count = len(all_reports)
        if count > 0:
            newest_report = all_reports[0]
        else:
            newest_report = None
        avatars = [report.member.avatar for report in all_reports[0:number]]
        return {'count': count, 'avatars': avatars, 'newest_report': newest_report}
    else:
        return None


class ReportAvatars(fields.Raw):
    def format(self, value):
        avatars = get_report_member_data(str(value))['avatars']
        return avatars


class ReportCount(fields.Raw):
    def format(self, value):
        return get_report_member_data(str(value))['count']


class NewestReportTime(fields.Raw):
    def format(self, value):
        newest_report_time = get_report_member_data(str(value))['newest_report'].created_time
        return Date.datetime_toTimestamp(newest_report_time)

# -*- coding: utf-8 -*-
from trialcenter.models.member import Application
from bson.objectid import ObjectId
from flask_restful import fields
from extensions import cache
from common import Log


@cache.memoize(timeout=60)
def get_applications_member_data(trial_id='', number=5):
    if len(trial_id) == 24:
        all_apps = Application.objects(trial=ObjectId(trial_id), status__ne=99).only('member').order_by('-created_time')
        count = len(all_apps)
        avatars = [app.member.avatar for app in all_apps[0:number]]
        return {'count': count, 'avatars': avatars}
    else:
        return None


class ApplicationAvatars(fields.Raw):
    def format(self, value):
        avatars = get_applications_member_data(str(value))['avatars']
        return avatars


class ApplicationCount(fields.Raw):
    def format(self, value):
        return get_applications_member_data(str(value))['count']


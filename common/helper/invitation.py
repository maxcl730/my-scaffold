# -*- coding: utf-8 -*-
from extensions import cache
from datetime import datetime
from trialcenter.models.member import Invitation


@cache.memoize(timeout=60)
def get_invitation_data():
    # 获取接受助力的总人数(count host_member)
    invitation_number = len(Invitation.unique_invitation_host_member(begin_date=datetime(year=2019, month=1, day=1)))

    # 最新一个获得助力的记录
    newest_invitations = Invitation.objects(origin_point__gt=0).order_by('-created_time')[:5]

    data = {'invitation_number': invitation_number,
            'newest_invitations': newest_invitations}
    return data

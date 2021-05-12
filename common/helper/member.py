# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import current_app
from trialcenter.models.member import Member, Application, Report, MemberFavorite
from common.date import Date
from common import Log


def ban_member(config):
    result = list()
    # 封禁逾期未提交报告的用户
    report_deadline_days = config['report_deadline_days'] if 'report_deadline_days' in config else 10
    members = Application.objects(updated_time__lt=Date.today_date() - timedelta(days=report_deadline_days),
                                  updated_time__gt=Date.today_date() - timedelta(days=report_deadline_days + 1),
                                  status__in=[1, 2],
                                  report=None).order_by('member').values_list('member')
    #members = Application.objects(updated_time__lt=Date.today_date() - timedelta(days=report_deadline_days),
    #                              status__in=[1, 2],
    #                              report=None).order_by('member').values_list('member')
    count = 0
    if members is None:
        return result
    temp_member = None
    for member in members:
        if temp_member == member or member.status == 2:
            continue
        temp_member = member
        member.status = 2
        member.updated_time = datetime.now()
        member.blocked_info = '提交报告逾期'
        member.save()
        count += 1
    result.append({'reason': '逾期{}天未提交报告'.format(report_deadline_days), 'count': count})
    return result


def gift_point_to_member():
    # 每日赠送会员一次试用机会，如果上次赠送机会未使用就不再赠送
    count = Member.objects(point=0, status=1).update(set__point=1)
    return count


def check_member_favorite_report(member, reports):
    # 检查会员是否收藏了报告
    favor_action = list()
    member_favorite = MemberFavorite.objects(member=member).first()
    if member_favorite is None:
        for report in reports:
            favor_action.append({'id': report.id.__str__(),
                                 'action': 'add'})
        return favor_action
    for report in reports:
        favor_action.append({'id': report.id.__str__(),
                             'action': 'delete' if report in member_favorite.reports else 'add'})
    return favor_action


def check_member_like_report(member, reports):
    # 检查会员是否喜欢了报告
    like_action = list()
    member_favorite = MemberFavorite.objects(member=member).first()
    if member_favorite is None:
        for report in reports:
            like_action.append({'id': report.id.__str__(),
                                'action': 'add'})
        return like_action
    for report in reports:
        like_action.append({'id': report.id.__str__(),
                            'action': 'delete' if report in member_favorite.likes else 'add'})
    return like_action


def check_member_application(member=None, trial=None):
    # 检查会员是否申请了试用
    if member and trial:
        application = Application.objects(member=member, trial=trial).first()
        if application is None:
            return False
        else:
            return True


def check_member_report(member=None, trial=None):
    # 检查会员是否提交了报告
    if member and trial:
        return Report.objects(member=member, trial=trial).first()
    else:
        return None


def check_token(uid='', token='', fake=False):
    # 验证token
    try:
        member = Member.objects(id=ObjectId(uid)).first()
        if fake:
            # 用作测试，不验证token，直接返回会员信息
            return member
    except InvalidId:
        raise Exception('Invalid Uid')

    if not member:
        raise Exception('Uid not exist.')
    if token != member.geneToken():
        raise Exception('Invalid Token')
    if member.status == 2:
        raise Exception('Member has been blocked.')
    return member


def sort_and_unique_list(l, reverse=False):
    origin_list = [x for x in l]
    new_list = sorted(set(origin_list), key=origin_list.index)
    new_list.sort(reverse=reverse)
    return new_list


def generate_invitation_code(uid):
    # 生成邀请码（uid与时间编码组合）
    now = datetime.now()
    timestamp = Date.datetime_toTimestamp(Date.today_date())
    # print(timestamp)
    code_table = sort_and_unique_list(uid, reverse=True)
    x = len(code_table)
    b = []
    while True:
        s = timestamp // x  # 商
        y = timestamp % x  # 余数
        b = b + [y]
        if s == 0:
            break
        timestamp = s
    b.reverse()
    return uid[:8] + '-' + uid[8:16] + '-' + uid[16:] + '-' + "".join(code_table[i] for i in b)


def get_uid_from_invitation_code(code):
    # 从邀请码中获取uid
    uid = code[0:27].replace('-', '')
    return uid


def check_invitation_code(code):
    # 检验邀请码是否有效
    uid = code[0:27].replace('-', '')
    invitation_code = code[27:]
    code_table = sort_and_unique_list(uid, reverse=True)
    x = len(code_table)
    mapping = {}
    count = 0
    for letter in [x for x in code_table]:
        mapping[letter] = count
        count += 1
    count = 0
    for i in str(invitation_code)[:len(invitation_code)-1]:
        count = count + mapping[i]
        count = count * x
    timestamp = count + mapping[str(invitation_code)[len(invitation_code)-1]]
    if Date.datetime_toTimestamp(datetime.now()) > timestamp + current_app.config['INVITATION_CODE_TTL']:
            return False
    else:
        return True

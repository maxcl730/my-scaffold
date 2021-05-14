# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import current_app
from main.models.member import Member
from common.date import Date
from common import Log


def ban_member(config):
    pass


def check_member_application(member=None, trial=None):
    # 检查会员是有申请
    pass


def check_token(uid='', token='', fake=False):
    # 验证token , uid为主键
    member = Member.query.get(uid)
    if fake:
        # 用作测试，不验证token，直接返回会员信息
        return member

    if not member:
        raise Exception('Uid not exist.')
    if token != member.gene_Token:
        raise Exception('Invalid Token')
    if member.status == 2:
        raise Exception('Member has been banned.')
    return member


def sort_and_unique_list(l, reverse=False):
    origin_list = [x for x in l]
    new_list = sorted(set(origin_list), key=origin_list.index)
    new_list.sort(reverse=reverse)
    return new_list

# -*- coding: utf-8 -*-
from flask import current_app
from flask_restful import Resource, fields
from bson.objectid import ObjectId
from trialcenter.models.member import Application
from trialcenter.models.trial import Trial
from .parser import trial_get_parser
from common.helper.mapping import TimestampValue
from common.http import Http
from common.date import Date


class MemberAvatar(fields.Raw):
    def format(self, value):
        return value.avatar


class MemberNickname(fields.Raw):
    def format(self, value):
        return value.nickname


class MemberCreatedTimeStamp(fields.Raw):
    def format(self, value):
        return Date.datetime_toTimestamp(value.created_time)


class ApplicationListApi(Resource):
    def get(self):
        """
        试用信息页面的申请列表
        获取试用活动申请列表，包括申请会员和申请宣言
        ---
        tags:
          - 页面接口
        parameters:
          - name: uid
            in: query
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            description: AccessToken
            schema:
              type: string
          - name: trial_id
            in: query
            required: true
            description: 试用id
            schema:
              type: string
          - name: page
            in: query
            required: false
            description: 当前页号, 默认为第一页
            schema:
              type: int
        responses:
          200:
            description:
              code=0为正常，返回首页内容；code不等于0请查看message中的错误信息；</br>
              数据项：</br>
              pages - 总页数</br>
              applications_number - 总申请数</br>
              applications:申请数组
              {id:申请id，nickname:用户昵称，avatar:用户头像，content:申请内容，created_time:申请时间}
            examples:
              json: {'code': 0, "message": "Success", 'data': { }}

        """
        # 试用申请页面
        data_format = {
            'pages': fields.Integer,
            'applications_number': fields.Integer,
            'applications': fields.List(fields.Nested({
                'id': fields.String,
                'nickname': MemberNickname(attribute='member'),
                'avatar': MemberAvatar(attribute='member'),
                'content': fields.String(),
                'created_time': TimestampValue(attribute='created_time'),
            })),
        }
        args = trial_get_parser.parse_args()
        """
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            # 匿名用户
            member = None
        """
        list_per_page = current_app.config['FRONTEND_LIST_PER_PAGE']
        page = args['page'] if args['page'] else 1

        trial_id = args['trial_id']
        if len(trial_id) != 24:
            return Http.gen_failure_response(message='Invalid trial_id!')
        trial = Trial.objects(id=ObjectId(trial_id)).first()
        if trial is None:
            return Http.gen_failure_response(message='Trial_id not found!')
        # 试用申请列表
        applications = Application.objects(trial=trial).filter(status__ne=99)
        applications_paginate = applications.paginate(page=page, per_page=list_per_page)
        data = {
            'pages': applications_paginate.pages,
            'applications_number': applications.count(),
            'applications': applications_paginate.items
        }
        return Http.gen_success_response(data=data, data_format=data_format)


class SuccessApplicationApi(Resource):
    def get(self):
        """
        试用的成功申请-幸运湖友
        获取成功申请列表，包括申请会员和申请宣言
        ---
        tags:
          - 页面接口
        parameters:
          - name: uid
            in: query
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            description: AccessToken
            schema:
              type: string
          - name: trial_id
            in: query
            required: true
            description: 试用id
            schema:
              type: string
          - name: page
            in: query
            required: false
            description: 当前页号, 默认为第一页
            schema:
              type: int
        responses:
          200:
            description:
              code=0为正常，返回首页内容；code不等于0请查看message中的错误信息；</br>
              数据项：</br>
              pages - 总页数</br>
              applications_number - 总申请数</br>
              success_applications_number - 已通过申请数</br>
              applications:申请数组
              {id:申请id，nickname:用户昵称，avatar:用户头像，content:申请内容，created_time:申请时间}
            examples:
              json: {'code': 0, "message": "Success", 'data': { }}

        """
        # 成功申请
        data_format = {
            'pages': fields.Integer,
            'success_applications_number': fields.Integer,
            'applications_number': fields.Integer,
            'members': fields.List(fields.Nested({
                'nickname': MemberNickname(attribute='member'),
                'avatar': MemberAvatar(attribute='member'),
                'created_time': MemberCreatedTimeStamp(attribute='member'),
            })),
            'applications': fields.List(fields.Nested({
                'id': fields.String,
                'nickname': MemberNickname(attribute='member'),
                'avatar': MemberAvatar(attribute='member'),
                'content': fields.String(),
                'created_time': TimestampValue(attribute='created_time'),
            })),
        }
        args = trial_get_parser.parse_args()
        """
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            # 匿名用户
            member = None
        """
        list_per_page = current_app.config['FRONTEND_LIST_PER_PAGE']
        page = args['page'] if args['page'] else 1

        trial_id = args['trial_id']
        if len(trial_id) != 24:
            return Http.gen_failure_response(message='Invalid trial_id!')
        trial = Trial.objects(id=ObjectId(trial_id)).first()
        if trial is None:
            return Http.gen_failure_response(message='Trial_id not found!')
        # 试用申请列表
        applications = Application.objects(trial=trial)
        success_applications = applications.filter(status__in=[1, 2])
        success_applications_paginate = success_applications.paginate(page=page, per_page=list_per_page)
        data = {
            'pages': success_applications_paginate.pages,
            'success_applications_number': success_applications.count(),
            'applications_number': applications.count(),
            'members': success_applications,
            'applications': success_applications_paginate.items
        }
        return Http.gen_success_response(data=data, data_format=data_format)

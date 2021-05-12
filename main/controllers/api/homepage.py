# -*- coding: utf-8 -*-
from flask import current_app
from flask_restful import Resource, fields
from datetime import datetime
from common.http import Http
from common.helper.mapping import StandardValue
from .parser import pagination_get_perser
from common.helper.application import ApplicationAvatars, ApplicationCount


@cache.cached(timeout=300, key_prefix='focus')
def get_focus():
    # 获取焦点图
    return Focus.objects()


@cache.cached(timeout=300, key_prefix='banner')
def get_banner():
    # 获取Banner
    return Banner.objects().first()


class HomepageApi(Resource):
    # @cache.cached(timeout=60, key_prefix=make_cache_key)
    def get(self):
        """
        首页
        获取首页焦点图、试用列表、banner等
        ---
        tags:
          - 页面接口
        parameters:
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
              pages - 总页数; </br>
              focus - 焦点图 {order:顺序，title:标题，image:图片url，type:类型[trial-试用/report-报告]，trial_id:试用id，active:当前试用是否可用 }</br>
              banner - banner图 {image:图片url，click：链接地址}</br>
              opened_trials - 当前开启的试用活动
              {id:试用id，title:标题，thumb_image:缩略图，standard:规格，price:价格，visitors:人气，applicants:申请数，avatars:头像}</br>
              closed_trials - 已经结束的试用活动
              {id:试用id，title:标题，thumb_image:缩略图，visitors:人气，reports:报告数，avatars:头像}</br>

            examples:
              json: {'code': 0, "message": "Success", 'data': { }}

        """
        data_format = {
            'pages': fields.Integer(default=1),
            'focus': fields.List(
                fields.Nested({
                    'order': fields.Integer,
                    'title': fields.String,
                    'image': fields.String,
                    'type': fields.String(attribute='source_type'),
                    'trial_id': fields.String,
                    'active': fields.Boolean,
                })),
            'banner': fields.Nested({
                'position': fields.Integer,
                'image': fields.String,
                'click': fields.String,
                }),
            'opened_trials': fields.List(fields.Nested({
                'id': fields.String,
                'title': fields.String,
                'thumb_image': fields.String,
                'standard': StandardValue(),
                'price': fields.String,
                'visitors': fields.Integer(default=0),
                'applicants': ApplicationCount(attribute='id', default=0),
                'avatars': ApplicationAvatars(attribute='id', default={}),
            })),
            'closed_trials': fields.List(fields.Nested({
                'id': fields.String,
                'title': fields.String,
                'thumb_image': fields.String,
                'visitors': fields.Integer(default=0),
                'reports': ReportCount(attribute='id', default=0),
                'avatars': ReportAvatars(attribute='id', default={}),
            }))
        }
        args = pagination_get_perser.parse_args()
        list_per_page = current_app.config['FRONTEND_LIST_PER_PAGE']
        page = args['page'] if args['page'] else 1
        if page == 1:
            # 获取进行中的试用
            opened_trials = Trial.objects(begin_time__lt=datetime.now(),
                                          end_time__gt=datetime.now(),
                                          publish_status__gt=0).order_by('-end_time')
            # 获取已结束试用
            closed_trials = Trial.objects(end_time__lt=datetime.now(),
                                          publish_status__gt=0).order_by('-end_time').paginate(page=page,
                                                                                               per_page=list_per_page)
            data = {
                'pages': closed_trials.pages,
                'focus': get_focus(),
                'banner': get_banner(),
                'opened_trials': opened_trials,
                'closed_trials': closed_trials.items,
            }
        else:
            data_format.pop('focus')
            data_format.pop('banner')
            data_format.pop('opened_trials')
            try:
                closed_trials = Trial.objects(end_time__lt=datetime.now(),
                                              publish_status__gt=0).order_by('-end_time').paginate(page=page,
                                                                                                   per_page=list_per_page)
            except :
                return Http.gen_failure_response(message='Page not found!')
            data = {
                'pages': closed_trials.pages,
                'closed_trials': closed_trials.items,
            }
            return Http.gen_success_response(data=data, data_format=data_format)

        return Http.gen_success_response(data=data, data_format=data_format)

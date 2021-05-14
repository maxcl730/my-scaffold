# -*- coding: utf-8 -*-
from datetime import datetime
from flask import request, current_app
from flask_restful import Resource, fields, marshal_with, marshal, abort
from .parser import member_login_parser, uid_token_parser, member_register_parser, member_info_post_parser
from common.http import Http
from common.helper.member import check_member_application, check_token
from database import db
from main.models.member import Member
from common import Log
from pprint import pprint


class MemberAvatar(fields.Raw):
    def format(self, value):
        return value.avatar


class MemberNickname(fields.Raw):
    def format(self, value):
        return value.nickname


class MemberLoginApi(Resource):
    def post(self):
        """
        会员登录
        调用接口需要提供 National_id/Password, 返回Token和uid。
        ---
        tags:
          - 会员接口
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required:
                - national_id
                - password
              properties:
                national_id:
                  type: string
                  description: National_id.
                  example: "19230192"
                password:
                  type: string
                  description: 用户密码.
                  example: "helloworld"
        responses:
          200:
            description: 返回Token和Uid
            examples:
              json: {'token': 'eyJhbGciOiJIUzI1NiIsImlhdCI6MTU0NzcyMjY0MCwiZXhwIjoxNTQ3NzIyOTQwfQ.eyJpZCI6IjVjMzgzNTNkNmZlYmJiMDcyNTE0OGE1OCJ9._BjoZS8TMAifNik21hO6xpSVyHXEzRDmMrmWiRVgx0s', 'uid':123}

        """

        data_format = {
            'uid': fields.String,
            'token': fields.String,
        }
        # 用户验证（返回uid、signature)
        args = member_login_parser.parse_args()
        member = Member.query.filter_by(national_id=args['national_id']).first()
        if member:
            member.salt = member.gene_Salt
            db.session.add(member)
            db.session.commit()
            uid = str(member.id)
            token = member.gene_Token
            return Http.gen_success_response(data={'uid': str(uid), 'token': token}, data_format=data_format)
        else:
            return Http.gen_failure_response(code=-1, message='Member does not exist.')

        #if member.status == 2:
            # 会员已被禁用
        #    return Http.gen_failure_response(message="Member has been blocked.")


class MemberAuthApi(Resource):
    def get(self):
        """
        会员验证
        使用uid和token验证当前用户是否有效
        ---
        tags:
          - 会员接口
        parameters:
          - name: uid
            in: query
            required: true
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            required: true
            description: AccessToken
            schema:
              type: string
        responses:
          200:
            description: code=0为正常，返回uid(用户id)和AccessToken，每次用户访问登录接口Token会更新；code不等于0请查看message中的错误信息。
            examples:
              json: {'code': 0, "message": "Success", 'data': {'uid':'5c3a15126febbb06f576384b', 'token':'feee62378cc104e14e628e0048325103'}}
        """
        data_format = {
            'uid': fields.String,
            'token': fields.String,
        }
        # 用户验证（返回uid、signature)
        args = uid_token_parser.parse_args()
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        # 调用此接口后会更新Token
        member.salt = member.gene_Salt
        db.session.add(member)
        db.session.commit()
        uid = str(member.id)
        token = member.gene_Token
        return Http.gen_success_response(data={'uid': str(uid), 'token': token}, data_format=data_format)


class MemberRegisterApi(Resource):
    def post(self):
        """
        会员信息注册
        会员信息注册，National_ID/Mobile/Password
        ---
        tags:
          - 会员接口
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required:
                - national_id
                - mobile
                - password
              properties:
                national_id:
                  type: string
                  description: National_id.
                  example: "19230192"
                mobile:
                  type: string
                  description: 电话.
                  example: "111000222333"
                password:
                  type: string
                  description: 用户密码.
                  example: "hello_world"
                language:
                  type: string
                  description: 用户语言
                  example: "en_US"
                birthday:
                  type: string
                  description: 用户出生日期
                  example: "dd/mm/yyyy"
        responses:
          200:
            description: code=0为正常，返回uid(用户id)和AccessToken，每次用户访问登录接口Token会更新；code不等于0请查看message中的错误信息。
            examples:
              json: {'code': 0, "message": "Success", 'data': {'uid':'5c3a15126febbb06f576384b', 'token':'feee62378cc104e14e628e0048325103'}}
        """
        data_format = {
            'uid': fields.String,
            'token': fields.String,
        }
        args = member_register_parser.parse_args()
        #try:
        member = Member.query.filter_by(national_id=args['national_id']).first()
        if member:
            member.mobile = args['mobile']
            member.password = args['password']
            member.language = args.get('language', '')
            member.birthday = args.get('birthday', '')
            member.nickname = args.get('nickname', '')
            member.sex = args.get('sex', '')
            db.session.add(member)
        else:
            new_member = Member(
                national_id=args['national_id'],
                mobile=args['mobile'],
                password=args['password'],
                birthday=args.get('birthday', ''),
                language=args.get('language', 'en_US'),
                nickname=args.get('nickname', ''),
                sex=args.get('sex', 0)
            )
            db.session.add(new_member)
        member = Member.query.filter_by(national_id=args['national_id']).first()
        member.salt = member.gene_Salt
        pprint(member.salt)
        uid = str(member.id)
        db.session.add(member)
        db.session.commit()
        token = member.gene_Token
        return Http.gen_success_response(data={'uid': str(uid), 'token': token}, data_format=data_format)
        #except Exception as e:
        #    db.session.rollback()
        #    return Http.gen_failure_response(message=e.__str__())


class MemberInfoApi(Resource):
    def get(self):
        """
        获取会员信息
        获取昵称、头像、性别、状态、数等个人信息
        ---
        tags:
          - 会员接口
        parameters:
          - name: uid
            in: query
            required: true
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            required: true
            description: AccessToken
            schema:
              type: string
        responses:
          200:
            description:
              code=0为正常，返回用户信息；code不等于0请查看message中的错误信息；
              nickname:用户昵称；
              sex： 0 未知，1 男，2 女；
              status： 1 正常 ，2 禁用；
              point： 剩余试用次数。
            examples:
              json: {'code': 0, "message": "Success", 'data': {'nickname':'logan', 'national_id':'1304124123', 'sex':1, 'status':1, 'mobile':'11222333444', 'language':'en_US'}}

        """
        data_format = {
            'nickName': fields.String,
            'national_id': fields.String,
            'mobile': fields.String,
            'sex': fields.Integer,
            'language': fields.String,
            'birthday': fields.String,
            'status': fields.Integer,
        }
        args = uid_token_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        # Log.info("{}, {}".format(effective_invitation.sum('current_point'), effective_helper.sum('helper_point')))

        return Http.gen_success_response(data={'nickName': member.nickname,
                                               'national_id': member.national_id,
                                               'sex': member.sex,
                                               'language': member.language,
                                               'birthday': member.birthday,
                                               'status': member.status,
                                               },
                                         data_format=data_format)

    def post(self):
        """
        更新会员信息， 注册新会员信息
        更新会员密码、手机号、nickname、性别、语言等
        ---
        tags:
          - 会员接口
        parameters:
          - name: uid
            in: query
            required: true
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            required: true
            description: AccessToken
            schema:
              type: string
          - name: body
            in: body
            required: true
            schema:
              properties:
                nickname:
                  type: string
                  description: 昵称.
                  example: "iloveu"
                password:
                  type: string
                  description: password.
                  example: "3uihfaefeDAFAa34fAFA"
                mobile:
                  type: string
                  description: 手机号
                  example: "91030219421"
                sex:
                  type: int
                  description: 性别
                  example: "1-男；2-女；0-未知"
                language:
                  type: string
                  description: 语言
                  example: "zh_CN, en_US"
        responses:
          200:
            description: code=0为正常，返回成功；code不等于0请查看message中的错误信息；
            examples:
              json: {'code': 0, 'message':'SUCCESS', 'data':{}}

        """
        # 提交更新会员信息
        args = member_info_post_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'])
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        member.sex = args.get('sex', member.sex)
        member.nickName = args.get('nickName', member.nickname)
        member.mobile = args.get('mobile', member.mobile)
        member.language = args.get('language', member.language)
        member.birthday = args.get('birthday', member.birthday)
        member.nickname = args.get('nickname', member.birthday)

        return Http.gen_success_response()


class MemberApplyApi(Resource):
    def get(self):
        """
        验证会员申请请求，返回是否允许申请
        验证会员申请请求，如果会员可以申请此试用返回成功，如果已经申请或没有试用机会则返回错误
        ---
        tags:
          - 会员接口
        parameters:
          - name: uid
            in: query
            required: true
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            required: true
            description: AccessToken
            schema:
              type: string
          - name: trial_id
            in: query
            required: true
            description: 试用id
            schema:
              type: string
        responses:
          200:
            description:
              code=0为用户申请通过，可以进入提交申请宣言页面；code不等于0请查看message中的错误信息；</br>
            examples:
              json: {'code': 0, "message": "Success", 'data': { }}

        """
        # 用户申请试用，如果已经申请则返回失败
        args = application_get_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        # 验证试用ID
        trial_id = args['trial_id']
        if trial_id is None or len(trial_id) != 24:
            return Http.gen_failure_response(message='Invalid trial_id.')

        trial = Trial.objects(id=ObjectId(trial_id), publish_status__gt=0).first()
        if trial is None:
            return Http.gen_failure_response(message='Trial not found.')

        if check_member_application(member, trial):
            return Http.gen_failure_response(message='您已经申请过该试用活动.')

        effective_invitation = Invitation.effective_invitation(host_member=member,
                                                               ttl_days=current_app.config['EFFECTIVE_INVITATION_TTL'])
        effective_helper = Invitation.effective_helper(guest_member=member,
                                                       ttl_days=current_app.config['EFFECTIVE_INVITATION_TTL'])
        current_point = effective_invitation.sum('current_point') + effective_helper.sum('helper_point')

        if current_point + member.point < 1:
            return Http.gen_failure_response(message='试用机会已耗尽.')

        return Http.gen_success_response()

    def post(self):
        """
        会员提交申请试用的宣言和地址
        当前用户申请试用，如果已经当前已经申请过此试用则返回错误状态
        ---
        tags:
          - 会员接口
        parameters:
          - name: uid
            in: query
            required: true
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            required: true
            description: AccessToken
            schema:
              type: string
          - name: trial_id
            in: query
            required: true
            description: 试用id
            schema:
              type: string
          - name: body
            in: body
            required: true
            schema:
              required: false
                - postal_code
                - national_code
                - county_name
                - form_id
              required:
                - content
                - username
                - province_name
                - city_name
                - detail_info
                - tel_number
              properties:
                content:
                  type: string
                  description: 申请宣言
                  example: "我很喜欢，我想要，给我吧！"
                username:
                  type: string
                  description: 收件人姓名，必须传入
                  example: "沙隆巴斯"
                province_name:
                  type: string
                  description: 省份，必须传入
                  example: "西藏"
                city_name:
                  type: string
                  description: 城市，必须传入
                  example: "拉萨"
                detail_info:
                  type: string
                  description: 详细地址，必须传入
                  example: "布达拉宫1号楼4门103"
                tel_number:
                  type: string
                  description: 电话号码，必须传入
                  example: "13911122233"
                postal_code:
                  type: string
                  description: 邮编，可选
                  example: "100001"
                county_name:
                  type: string
                  description: 国家，可选(默认为"中国")
                  example: "中国"
                national_code:
                  type: string
                  description: 国家代码，可选(默认为"086")
                  example: "086"
                form_id:
                  type: string
                  description: 小程序消息的form_id
        responses:
          200:
            description:
              code=0为用户申请提交完成；code不等于0请查看message中的错误信息；</br>
              application_id - 申请ID</br>
            examples:
              json: {'code': 0, "message": "Success", 'data': { }}

        """
        data_format = {
            'application_id': fields.String,
        }
        # 会员提交报告填写申请宣言以及收货地址
        args = application_post_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        # 验证试用ID
        trial_id = args['trial_id']
        if trial_id is None or len(trial_id) != 24:
            return Http.gen_failure_response(message='Invalid trial_id.')

        trial = Trial.objects(id=ObjectId(trial_id)).first()
        if trial is None:
            return Http.gen_failure_response(message='Trial not found.')

        if check_member_application(member, trial):
            return Http.gen_failure_response(message='您已经申请过该试用活动.')

        # 获取有效期内受助力和助力他人所获机会
        effective_invitation = Invitation.effective_invitation(host_member=member,
                                                               ttl_days=current_app.config['EFFECTIVE_INVITATION_TTL'])
        effective_helper = Invitation.effective_helper(guest_member=member,
                                                       ttl_days=current_app.config['EFFECTIVE_INVITATION_TTL'])
        current_point = effective_invitation.sum('current_point') + effective_helper.sum('helper_point')

        if current_point + member.point < 1:
            return Http.gen_failure_response(message='试用机会已耗尽.')

        # 提交申请宣言和地址
        content = args['content']
        application = Application(member=member, trial=trial)
        application.content = content
        application.status = 0
        application.created_time = application.updated_time = datetime.now()
        member_address = MemberAddress(username=args['username'],
                                       tel_number=args['tel_number'],
                                       province_name=args['province_name'],
                                       city_name=args['city_name'],
                                       detail_info=args['detail_info'],
                                       postal_code=args['postal_code'] if 'postal_code' in args else '',
                                       county_name=args['county_name'] if 'county_name' in args else '中国',
                                       national_code=args['national_code' if 'national_code' in args else '086']
                                       )

        member.address = application.address = member_address
        member.updated_time = datetime.now()
        application.save()

        if 'form_id' in args:
            MemberFormID.objects(member=member,
                                 form_id=args['form_id']).update_one(set__created_time=datetime.now(), upsert=True)
        # 优先使用7天内的受助力所获机会
        if current_point > 0:
            first_effective_invitation = effective_invitation.first()
            first_effective_help = effective_helper.first()
            # 减少一次7天内邀请所获使用机会，
            if first_effective_help is None:
                # 没有帮助他人获得的机会，扣除邀请他人得到的机会
                first_effective_invitation.current_point -= 1
                first_effective_invitation.updated_time = datetime.now()
                first_effective_invitation.save()
            elif first_effective_invitation is None:
                # 没有邀请他人获得的机会，扣除帮助他人得到的机会
                first_effective_help.helper_point -= 1
                first_effective_help.updated_time = datetime.now()
                first_effective_help.save()
            else:
                # 既有邀请也有帮助获得的机会，选择时间最早的扣除
                if first_effective_help.created_time <= first_effective_invitation.created_time:
                    first_effective_help.helpe_point -= 1
                    first_effective_help.updated_time = datetime.now()
                    first_effective_help.save()
                else:
                    first_effective_invitation.current_point -= 1
                    first_effective_invitation.updated_time = datetime.now()
                    first_effective_invitation.save()
        else:
            # 减少注册或助力赠送的机会
            member.point -= 1  # 为方便测试不执行此行，保留试用机会

        member.save()
        return Http.gen_success_response(data={'application_id': application.id.__str__()},
                                         data_format=data_format)


class MemberApplicationApi(Resource):
    def get(self):
        """
        获取会员全部/成功申请信息
        获取全部申请和成功申请信息
        ---
        tags:
          - 会员接口
        parameters:
          - name: uid
            in: query
            required: true
            description: 用户id
            schema:
              type: string
          - name: token
            in: query
            required: true
            description: AccessToken
            schema:
              type: string
        responses:
          200:
            description:
              code=0为正常，返回用户信息；code不等于0请查看message中的错误信息；</br>
              all_applications - 全部申请</br>
              {application_id:申请id，id:试用id，title:试用标题，thumb_image:缩略图，standard:规格，price:价格，visitors:人气，active:试用可用状态，
              stage:申请进度[0：已结束-等待公布获奖名单，1：已结束-未获得试用 ，2：体验报告已完成，3：写体验报告]}</br>
              success_applications - 已通过的申请</br>
              {application_id:申请id，id:试用id，title:试用标题，thumb_image:缩略图，standard:规格，price:价格，visitors:人气，active:试用可用状态，
              stage:申请进度[0：已结束-等待公布获奖名单，1：已结束-未获得试用 ，2：体验报告已完成，3：写体验报告]}</br>
            examples:
              json: {'code': 0, "message": "Success", 'data': {}}

        """
        data_format = {
            'all_applications': fields.List(
                fields.Nested({
                    'application_id': fields.String(attribute='id'),
                    'id': TrialID(attribute='trial'),
                    'title': TrialTitle(attribute='trial'),
                    'thumb_image': TrialThumbImage(attribute='trial'),
                    'standard': TrialStandard(attribute='trial'),
                    'price': TrialPrice(attribute='trial'),
                    'visitors': TrialVisitor(attribute='trial'),
                    'active': TrialActive(attribute='trial'),
                    'stage': fields.Nested({
                        'report_id': fields.String(default=''),
                        'number': fields.Integer,
                        'desc': fields.String,
                    })
                })),
            'success_applications': fields.List(
                fields.Nested({
                    'application_id': fields.String(attribute='id'),
                    'id': TrialID(attribute='trial'),
                    'title': TrialTitle(attribute='trial'),
                    'thumb_image': TrialThumbImage(attribute='trial'),
                    'standard': TrialStandard(attribute='trial'),
                    'price': TrialPrice(attribute='trial'),
                    'visitors': TrialVisitor(attribute='trial'),
                    'active': TrialActive(attribute='trial'),
                    'stage': fields.Nested({
                        'report_id': fields.String(default=''),
                        'number': fields.Integer,
                        'desc': fields.String,
                    })
                })),
        }
        # 我的试用申请
        args = memberinfo_get_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        all_applications = Application.objects(member=member)
        success_applications = Application.objects(member=member, status__in=[1, 2])
        return Http.gen_success_response(data={'all_applications': all_applications,
                                               'success_applications': success_applications},
                                         data_format=data_format)


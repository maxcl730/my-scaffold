# -*- coding: utf-8 -*-
from datetime import datetime
from bson.objectid import ObjectId
from flask import request, current_app
from flask_restful import Resource, fields, marshal_with, marshal, abort
from common.http import Http
from common.wechat import WXApp
from common.helper.member import check_member_like_report, check_member_application, check_token
from common.helper.invitation import get_invitation_data
from common.helper.mapping import StandardValue, INVITATION_TO_POINT, TimestampValue, good_standard_desc
from common.date import FieldDatetimeToTimestamp
from common import Log
from trialcenter.controllers.api.parser import memberlogin_get_parser, memberinfo_get_parser, memberinfo_post_parser,\
    application_get_parser, application_post_parser, favorite_post_parser, report_post_parser, invitation_get_parser,\
    favorite_get_parser, help_post_parser
from trialcenter.models.trial import Trial
from trialcenter.models.member import Member, MemberFavorite, MemberBindWechat, MemberAddress, Application, Report,\
    Invitation, MemberFormID
from trialcenter.models.notify import NotifyRecord


class MemberAvatar(fields.Raw):
    def format(self, value):
        return value.avatar


class MemberNickname(fields.Raw):
    def format(self, value):
        return value.nickname


class TrialID(fields.Raw):
    def format(self, value):
        return value.id.__str__()


class TrialTitle(fields.Raw):
    def format(self, value):
        return value.title


class TrialThumbImage(fields.Raw):
    def format(self, value):
        return value.thumb_image


class TrialPrice(fields.Raw):
    def format(self, value):
        return "{}".format(value.price)


class TrialStandard(fields.Raw):
    def format(self, value):
        return StandardValue.format(StandardValue, value.standard)


class TrialVisitor(fields.Raw):
    def format(self, value):
        return value.visitors


class TrialActive(fields.Raw):
    def format(self, value):
        if value.end_time > datetime.now():
            return True
        else:
            return False


class MemberLoginApi(Resource):
    def get(self):
        """
        微信用户登录/注册
        小程序获取用户code后访问该接口会自动注册用户并返回uid和AccessToken，相当于用户已登录
        ---
        tags:
          - 会员接口
        parameters:
          - name: code
            in: query
            required: true
            description: 微信用户code
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
        # 微信用户登录（返回uid、signature)
        args = memberlogin_get_parser.parse_args()
        code = args['code']
        wechat = WXApp(current_app)
        data = wechat.jscode2session(js_code=code)
        # data = {'openid':'wx_ttttteeeesssttt', 'session_key': 'tiihtNczf5v6AKRyjwEUhQ=='}
        if data is None:
            return Http.gen_failure_response(message='Networking failure.')
        elif 'errcode' in data:
            Log.warn('{}, {}'.format(data['errcode'], data['errmsg']))
            return Http.gen_failure_response(code=data['errcode'], message=data['errmsg'])
        elif 'openid' in data:
            member = Member.objects(bind_wechat__openid=data['openid']).first()
            if not member:
                new_member = Member()
                bind_wechat = MemberBindWechat()
                new_member.salt = Member.geneSalt()
                new_member.created_time = new_member.updated_time = datetime.now()
                try:
                    new_member.reg_ip = request.headers['X-Real-Ip']
                except KeyError:
                    new_member.reg_ip = request.remote_addr
                bind_wechat.openid = data['openid']
                bind_wechat.unionid = data['unionid'] if 'unionid' in data else ''
                bind_wechat.session_key = data['session_key'] if 'session_key' in data else ''
                bind_wechat.updated_time = datetime.now()
                new_member.bind_wechat = bind_wechat
                new_member.save()
                uid = str(new_member.id)
                token = new_member.geneToken()
            elif member.status == 2:
                # 会员已被禁用
                return Http.gen_failure_response(message="Member has been blocked.")
            else:
                member.bind_wechat.unionid = data['unionid'] if 'unionid' in data else ''
                member.bind_wechat.session_key = data['session_key'] if 'session_key' in data else ''
                member.bind_wechat.updated_time = datetime.now()
                member.salt = Member.geneSalt()
                member.save()
                uid = str(member.id)
                token = member.geneToken()
            return Http.gen_success_response(data={'uid': str(uid), 'token': token}, data_format=data_format)


class MemberInfoApi(Resource):
    def get(self):
        """
        获取会员信息
        获取昵称、头像、性别、状态、试用次数等个人信息
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
              json: {'code': 0, "message": "Success", 'data': {'nickname':'logan', 'avatar':'https://wx.logo.qq.com/xaafsf', 'sex':1, 'status':1, 'point':1}}

        """
        data_format = {
            'nickName': fields.String,
            'avatarUrl': fields.String,
            'gender': fields.Integer,
            'language': fields.String,
            'city': fields.String,
            'province': fields.String,
            'country': fields.String,
            'status': fields.Integer,
            'point': fields.Integer,
        }
        args = memberinfo_get_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        effective_invitation = Invitation.effective_invitation(host_member=member,
                                                               ttl_days=current_app.config['EFFECTIVE_INVITATION_TTL'])
        effective_helper = Invitation.effective_helper(guest_member=member,
                                                       ttl_days=current_app.config['EFFECTIVE_INVITATION_TTL'])
        current_point = effective_invitation.sum('current_point') + effective_helper.sum('helper_point')
        # Log.info("{}, {}".format(effective_invitation.sum('current_point'), effective_helper.sum('helper_point')))

        return Http.gen_success_response(data={'nickName': member.nickname,
                                               'avatarUrl': member.avatar,
                                               'gender': member.sex,
                                               'language': member.language,
                                               'city': member.city,
                                               'province': member.province,
                                               'country': member.county,
                                               'status': member.status,
                                               'point': current_point + member.point
                                               },
                                         data_format=data_format)

    def post(self):
        """
        更新会员信息
        更新会员信息
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
              required:
                - iv
                - encrypted_data
              properties:
                iv:
                  type: string
                  description: 微信获取的加密算法的初始向量.
                  example: "3uihfaefeDAFAa34fAFA"
                encrypted_data:
                  type: string
                  description: 包括敏感数据在内的完整用户信息的加密数据.
                  example: "3uihfaefeDAFAa34fAF3uihfaefeDAFAa34fAFAA"
        responses:
          200:
            description: code=0为正常，返回成功；code不等于0请查看message中的错误信息；
            examples:
              json: {'code': 0, 'message':'SUCCESS', 'data':{}}

        """
        # 提交更新会员信息
        args = memberinfo_post_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'])
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        session_key = member.bind_wechat.session_key
        if session_key is None:
            return Http.gen_failure_response(message='Invalid session_key')
        wechat = WXApp(current_app)
        try:
            userinfo = wechat.decrypt(session_key=session_key, encrypted_data=args['encrypted_data'], iv=args['iv'])
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())
        if 'gender' in userinfo:
            member.sex = userinfo['gender']
        if 'avatarUrl' in userinfo:
            member.avatar = userinfo['avatarUrl']
        if 'nickName' in userinfo:
            member.nickname = userinfo['nickName']
        if 'city' in userinfo:
            member.city = userinfo['city']
        if 'country' in userinfo:
            member.county = userinfo['country']
        if 'province' in userinfo:
            member.province = userinfo['province']
        if 'language' in userinfo:
            member.language = userinfo['language']
        if 'unionId' in userinfo: member.bind_wechat.unionid = userinfo['unionId']
        if 'phoneNumber' in userinfo:
            member.mobile = userinfo['phoneNumber']
        member.updated_time = datetime.now()
        member.save()
        return Http.gen_success_response()

    def delete(self):
        """
        删除会员信息
        删除会员信息，包括会员申请、报告、收藏等
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
            examples:
              json: {'code': 0, "message": "Success", 'data': {}}

        """
        # 删除用户信息
        args = memberinfo_get_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())
        Report.objects(member=member).delete()
        applications = Application.objects(member=member)
        NotifyRecord.objects(application__in=applications).delete()
        Application.objects(member=member).delete()
        MemberFavorite.objects(member=member).delete()
        Invitation.objects(host_member=member).delete()
        Invitation.objects(guest_member=member).delete()
        member.delete()
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


class MemberReportApi(Resource):
    def get(self):
        """
        获取会员全部体验报告信息
        获取全部体验报告
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
              nickname - 昵称</br>
              avatar - 头像</br>
              reports - 全部体验告别</br>
              reports:报告数组 {id:报告id，content:报告内容，image:报告图片数组，position_name:地理位置，like_num:喜欢数，created_time:创建时间，status:报告状态[0未审核、1审核通过、2审核不通过]}</br>
              like:喜欢动作数组{id:报告id， action：[add 添加/ delete 删除]}
            examples:
              json: {'code': 0, "message": "Success", 'data': {}}

        """
        # 我的体验报告
        data_format = {
            'nickname': fields.String,
            'avatar': fields.String,
            'reports': fields.List(
                fields.Nested({
                    'id': fields.String,
                    'content': fields.String,
                    'images': fields.List(fields.String),
                    'like_number': fields.Integer(attribute='like_num', default=0),
                    'position_name': fields.String(default=''),
                    'created_time': FieldDatetimeToTimestamp(attribute='created_time'),
                    'status': fields.Integer()
                })),
            'like': fields.List(fields.Nested({
                'id': fields.String,
                'action': fields.String(default='add'),
            })),
        }
        # 我的试用申请
        args = memberinfo_get_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        reports = Report.objects(member=member)
        # 检查用户是否已经收藏试用或者
        like_action = check_member_like_report(member, reports)
        return Http.gen_success_response(data={'nickname': member.nickname,
                                               'avatar': member.avatar,
                                               'reports': reports,
                                               'like': like_action},
                                         data_format=data_format)

    def post(self):
        """
        会员提交报告
        会员提交试用报告，包括：文字内容，多张图片，位置名称
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
          - name: application_id
            in: query
            required: true
            description: 申请ID
            schema:
              type: string
          - name: body
            in: body
            required: true
            schema:
              required: false
                - form_id
              required:
                - position_name
                - content
                - image
              properties:
                position_name:
                  type: string
                  description: 位置名称
                  example: "北京市朝阳区"
                content:
                  type: string
                  description: 报告内容
                  example: "very good!"
                images:
                  type: string
                  description: 报告图片,多张图片用逗号分隔
                  example: "https://images1.com/a.jpg,https://image2.com/b.jpg"
                form_id:
                  type: string
                  description: 小程序消息的form_id
        responses:
          200:
            description:
              code=0为正常，返回用户信息；code不等于0请查看message中的错误信息；</br>
              report_id - 报告ID</br>
            examples:
              json: {'code': 0, "message": "Success", 'data': {}}

        """
        # 会员提交报告
        data_format = {
            'report_id': fields.String,
        }

        args = report_post_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        # 验证申请
        application_id = args['application_id']
        application = Application.objects(id=ObjectId(application_id)).first()
        if application is None:
            return Http.gen_failure_response(message='Application not found!')
        if application.report is not None:
            return Http.gen_failure_response(message='您已提交试用报告，请不要重复提交')
        if application.status not in [1, 2]:
            return Http.gen_failure_response(message='您的申请尚未通过，无法提交报告')
        report = Report(member=member, trial=application.trial)
        report.content = args['content']
        report.images = args['images'].split(',')
        report.position_name = args['position_name']
        report.created_time = report.updated_time = datetime.now()
        report.save()
        application.report = report
        application.save()
        if 'form_id' in args:
            MemberFormID.objects(member=member,
                                 form_id=args['form_id']).update_one(set__created_time=datetime.now(), upsert=True)

        return Http.gen_success_response(data={'report_id': report.id.__str__()},
                                         data_format=data_format)


class MemberFavoriteApi(Resource):
    def get(self):
        # 我的收藏
        """
        获取会员收藏数据
        获取会员收藏数据，包括试用、报告
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
          - name: type
            in: query
            description: 收藏类型 trial/report，默认为trial
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
              code=0为正常，返回用户信息；code不等于0请查看message中的错误信息；</br>
              nickname - 昵称</br>
              avatar - 头像</br>
              pages - 总页数</br>
              trials - 用户收藏试用</br>
              {id:试用id，title:标题，standard:规格，price:价格，quantity:数量，thumb_image:缩略图， visitors:人气，</br>
               stage:申请进度[0：已结束-等待公布获奖名单，1：已结束-未获得试用 ，2：体验报告已完成，3：写体验报告]}</br>

              reports - 用户收藏报告</br>
              {id:报告id，nickname:用户昵称，avatar:用户头像，content:报告内容，image:报告图片数组，</br>
              like_num:喜欢数，share_number:分享数，created_time:创建时间，</br>
              trial:试用数据 {id:试用id，thumb_image:试用缩略图，title:试用标题}}</br>}</br>
              like - 喜欢报告动作数组{id:报告id， action：[add 添加/ delete 删除]}。
            examples:
              json: {'code': 0, "message": "Success", 'data': {}}

        """
        # 会员收藏
        data_format = {
            'nickname': fields.String,
            'avatar': fields.String,
            'pages': fields.Integer(default=1),
            'trials': fields.List(
                fields.Nested({
                    'id': fields.String,
                    'title': fields.String,
                    'standard': fields.String,
                    'price': fields.String,
                    'quantity': fields.Integer,
                    'thumb_image': fields.String,
                    'active': fields.Boolean(default=False),
                    'visitors': fields.Integer(attribute='visitors'),
                    'stage': fields.Nested({
                        'report_id': fields.String(default=''),
                        'number': fields.Integer,
                        'desc': fields.String,
                        })
                    })),
            'reports': fields.List(
                fields.Nested({
                    'id': fields.String,
                    'nickname': MemberNickname(attribute='member'),
                    'avatar': MemberAvatar(attribute='member'),
                    'content': fields.String,
                    'images': fields.List(fields.String),
                    'like_number': fields.Integer(attribute='like_num', default=0),
                    'share_number': fields.Integer(attribute='share_num', default=0),
                    'created_time': FieldDatetimeToTimestamp(attribute='created_time'),
                    'trial': fields.Nested({
                        'id': fields.String,
                        'thumb_image': fields.String,
                        'title': fields.String,
                    }),
                })),
            'like': fields.List(fields.Nested({
                'id': fields.String,
                'action': fields.String(default='add'),
            })),
        }
        # 我的收藏
        args = favorite_get_parser.parse_args()
        Log.info(args)
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        list_per_page = current_app.config['FRONTEND_LIST_PER_PAGE']
        page = args['page'] if args['page'] else 1

        member_favorite = MemberFavorite.objects(member=member).first()
        if member_favorite is None:
            return Http.gen_success_response(message='No available data.')
        favorite_type = args['type'] if 'type' in args else 'trial'
        from math import ceil
        if favorite_type == 'trial':
            # 返回收藏的试用
            data_format.pop('reports')
            data_format.pop('like')
            sorted_member_favorite_trials = sorted(member_favorite.trials,
                                                   key=lambda k: k.created_time,
                                                   reverse=True)
            member_favorite_trials_page = sorted_member_favorite_trials[(page-1)*list_per_page:page*list_per_page]
            pages = ceil(len(sorted_member_favorite_trials)/list_per_page)
            applications_stage = dict()
            for application in Application.objects(trial__in=member_favorite_trials_page, member=member):
                applications_stage[application.trial.id] = application.stage
            trials = list()
            for trial in member_favorite_trials_page:
                if trial.publish_status == 0:
                    # 跳过未发布的试用活动
                    continue
                if trial.id in applications_stage:
                    stage = {
                        'report_id': applications_stage[trial.id]['report_id'],
                        'number': applications_stage[trial.id]['number'],
                        'desc': applications_stage[trial.id]['desc'],
                    }
                else:
                    stage = dict()

                trials.append({
                    'id': trial.id,
                    'title': trial.title,
                    'standard': good_standard_desc(trial.standard),
                    'price': trial.price,
                    'quantity': trial.quantity,
                    'thumb_image': trial.thumb_image,
                    'active': trial.active,
                    'visitors': trial.visitors,
                    'stage': stage,
                })
            return Http.gen_success_response(data={'nickname': member.nickname,
                                                   'avatar': member.avatar,
                                                   'pages': pages,
                                                   'trials': trials,
                                                   },
                                             data_format=data_format)
        elif favorite_type == 'report':
            # 返回收藏的报告
            data_format.pop('trials')
            sorted_member_favorite_reports = sorted(member_favorite.reports,
                                                    key=lambda k: k.created_time,
                                                    reverse=True)
            pages = ceil(len(sorted_member_favorite_reports)/list_per_page)
            member_favorite_reports_page = sorted_member_favorite_reports[(page-1)*list_per_page:page*list_per_page]
            like_action = check_member_like_report(member, member_favorite_reports_page)
            return Http.gen_success_response(data={'nickname': member.nickname,
                                                   'avatar': member.avatar,
                                                   'pages': pages,
                                                   'reports': member_favorite_reports_page,
                                                   'like': like_action},
                                             data_format=data_format)
        else:
            return Http.gen_failure_response(message='Invalid type parameter.')

    def post(self):
        """
        会员收藏报告/试用
        会员收藏报告/试用
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
              required: false
                - trial_id
                - report_id
              required:
                - action
              properties:
                action:
                  type: string
                  description: 会员操作[ add / delete ]
                  example: "add"
                trial_id:
                  type: string
                  description: 待收藏的试用ID，trial_id/report_id至少要有一项
                  example: "a34fAF3uihfaefeDAFAa34fAFAA"
                report_id:
                  type: string
                  description: 待收藏的报告ID，trial_id/report_id至少要有一项
                  example: "a34fAF3uihfaefeDAFAa34fAFAA"
        responses:
          200:
            description: code=0为正常，返回成功；code不等于0请查看message中的错误信息；
            examples:
              json: {'code': 0, 'message':'SUCCESS', 'data':{}}

        """
        # 加入收藏
        args = favorite_post_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())
        # Log.info('{}   {}   {}'.format(args['trial_id'], args['report_id'], args['action']) )
        action = args['action'] if 'action' in args else None
        trial_id = args['trial_id'] if 'trial_id' in args else None
        report_id = args['report_id'] if 'report_id' in args else None
        if action not in ['add', 'delete']:
            return Http.gen_failure_response(message='Invalid action.')
        if trial_id is None and report_id is None:
            return Http.gen_failure_response(message='Either Trial_id or Report_id is required.')
        if trial_id:
            if len(trial_id) == 24:
                if action == 'add':
                    MemberFavorite.objects(member=member).update_one(add_to_set__trials=ObjectId(trial_id),
                                                                     updated_time=datetime.now(),
                                                                     upsert=True)
                    Trial.objects(id=ObjectId(trial_id)).update_one(inc__favors_num=1)
                else:
                    MemberFavorite.objects(member=member).update_one(pull__trials=ObjectId(trial_id),
                                                                     updated_time=datetime.now(),
                                                                     upsert=True)
                    Trial.objects(id=ObjectId(trial_id)).update_one(inc__favors_num=1)
            else:
                return Http.gen_failure_response(message='Invalid trial_id.')
        if report_id:
            if len(report_id) == 24:
                if action == 'add':
                    MemberFavorite.objects(member=member).update_one(add_to_set__reports=ObjectId(report_id),
                                                                     updated_time=datetime.now(),
                                                                     upsert=True)
                else:
                    MemberFavorite.objects(member=member).update_one(pull__reports=ObjectId(report_id),
                                                                     updated_time=datetime.now(),
                                                                     upsert=True)
            else:
                return Http.gen_failure_response(message='Invalid report_id.')

        return Http.gen_success_response()


class MemberInvitationCode(Resource):
    def get(self):
        """
        获取会员邀请码
        获取会员邀请码，邀请码24小时有效
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
              code=0为正常，返回成功；code不等于0请查看message中的错误信息；</br>
              invitation_code - 会员邀请码，24小时有效
            examples:
              json: {'code': 0, 'message':'SUCCESS', 'data':{}}

        """
        # 获取会员邀请码(24小时有效)，用于分享邀请页面
        data_format = {
            'invitation_code': fields.String,
        }
        args = memberinfo_get_parser.parse_args()
        # 验证token
        try:
            check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())
        from common.helper.member import generate_invitation_code
        invitation_code = generate_invitation_code(args['uid'])
        return Http.gen_success_response(data={'invitation_code': invitation_code},
                                         data_format=data_format)


class MemberInvitation(Resource):
    def get(self):
        """
        会员邀请页面
        会员邀请页面，会员可查看自己的邀请页面和其他人的邀请页面，分别进行'邀请朋友助力'和'为我朋友助力'
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
          - name: invitation_code
            in: query
            required: true
            description: 邀请码
            schema:
              type: string
        responses:
          200:
            description:
              code=0为正常，返回成功；code不等于0请查看message中的错误信息；</br>
              invitation_code - 会员邀请码，24小时有效</br>
              can_help - True 给朋友助力，False 邀请朋友为我助力</br>
              title - 试用title</br>
              thumb_image - 试用缩略图</br>
              nickname - Host member 昵称</br>
              avatar - Host member 头像</br>
              newest_invitations - 最新的5条邀请信息, 数组</br>
              { nickname - 用户昵称；created_time - 时间；point - 获得的试用机会} </br>
              invitation - Host member 邀请详情</br>
              { avatars - guest member头像；help_member_count - 为你助力人数；help_member_stage - 助力进度 {1：true/false，2：true/false，3：true/false，5：true/false}}</br>
              invitation_number - 成功邀请人数</br>
            examples:
              json: {'code': 0, 'message':'SUCCESS', 'data':{}}

        """
        # 会员邀请页面，根据uid和邀请码解密后的会员信息作对比
        # 如果为同一会员则显示其获得的助力信息，并开启"邀请朋友助力"
        # 如果为不同会员则显示邀请码对应会员的助力信息，并开启"为我朋友助力"
        data_format = {
            'invitation_active': fields.Boolean(default=False),
            'can_help': fields.Boolean(default=True),
            'title': fields.String,
            'thumb_image': fields.String,
            'nickname': fields.String,
            'avatar': fields.String,
            'newest_invitations': fields.List(fields.Nested(
                {'nickname': MemberNickname(attribute='host_member'),
                 'created_time': TimestampValue,
                 'point': fields.Integer(attribute='origin_point')
                 }
            )),
            'invitation': fields.Nested({
                'avatars': fields.List(fields.String),
                'help_member_count': fields.Integer(default=0),
                'help_member_stage': fields.Nested({
                    '1': fields.Boolean(default=False),
                    '2': fields.Boolean(default=False),
                    '3': fields.Boolean(default=False),
                    '5': fields.Boolean(default=False),
                }),
            }),
            'invitation_number': fields.Integer(default=0),
        }
        args = invitation_get_parser.parse_args()
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

        # 验证邀请码
        invitation_code = args['invitation_code']
        from common.helper.member import get_uid_from_invitation_code, check_invitation_code
        invitation_active = check_invitation_code(code=invitation_code)

        # 验证host、guest用户
        host_uid = get_uid_from_invitation_code(code=invitation_code)
        if host_uid == args['uid']:
            can_help = False
        else:
            can_help = True
        host_member = Member.objects(id=ObjectId(host_uid)).first()
        if host_member is None:
            return Http.gen_failure_response(message='Invalid invitation code.')

        # 当前邀请码已邀请到的人
        invitations = Invitation.objects(invitation_code=invitation_code,
                                         host_member=host_member).order_by("created_time").limit(5)
        help_member_count = invitations.count()
        # 助力用户头像
        avatars = list()
        if help_member_count > 0:
            for invitation in invitations[0:5]:
                avatars.append(invitation.guest_member.avatar)

        help_member_stage = {}
        for x in range(0, help_member_count):
            help_member_stage[str(x+1)] = True

        related_invitation_data = {
            'avatars': avatars,
            'help_member_count': help_member_count,
            'help_member_stage': help_member_stage,
        }

        # 获取接受助力的总人数(count host_member)
        all_invitation_data = get_invitation_data()
        invitation_number = all_invitation_data['invitation_number']
        # 最新一个活的助力的记录
        newest_invitations = all_invitation_data['newest_invitations']
        # Log.info(all_invitation_data)
        data = {
            'invitation_active': invitation_active,
            'can_help': can_help,
            'title': trial.title,
            'thumb_image': trial.thumb_image,
            'nickname': host_member.nickname,
            'avatar': host_member.avatar,
            'newest_invitations': newest_invitations,
            'invitation': related_invitation_data,
            'invitation_number': invitation_number
        }
        return Http.gen_success_response(data=data,
                                         data_format=data_format)


class MemberHelp(Resource):
    def post(self):
        """
        会员助力
        会员为其他人助力，增加一次试用机会，并增加收助力人的试用机会
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
          - name: invitation_code
            in: query
            required: true
            description: 邀请码
            schema:
              type: string
        responses:
          200:
            description:
              code=0为正常，返回成功；code不等于0请查看message中的错误信息；</br>
            examples:
              json: {'code': 0, 'message':'SUCCESS', 'data':{}}

        """
        # 被邀请会员助力其他会员
        # 为助力会员增加机会并记录信息
        # 为被助力会员增加机会并记录信息
        args = help_post_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())

        # 验证邀请码是否有效
        invitation_code = args['invitation_code']
        from common.helper.member import get_uid_from_invitation_code, check_invitation_code
        if not check_invitation_code(code=invitation_code):
            return Http.gen_failure_response(message='邀请码已过期')

        host_uid = get_uid_from_invitation_code(code=invitation_code)
        # 判断当前用户是否已经为邀请码发起者助力
        invitations = Invitation.objects(invitation_code=invitation_code, host_member=ObjectId(host_uid))
        if invitations.filter(guest_member=member).count() >= 1:
            return Http.gen_failure_response(message='今天已经给朋友助了')

        # 当前邀请码已邀请到的人数+1： 新助力的人次数
        help_member_count = invitations.count() + 1
        # 根据当前助力的人数增加试用次数
        try:
            assert help_member_count in INVITATION_TO_POINT.keys()
        except AssertionError:
            return Http.gen_failure_response(message='助力次数已达上限')

        # 为host_uid 和 guest_uid 增加受助力记录
        Invitation(invitation_code=invitation_code,
                   host_member=ObjectId(host_uid),
                   guest_member=member,
                   origin_point=INVITATION_TO_POINT[help_member_count],
                   current_point=INVITATION_TO_POINT[help_member_count],
                   helper_point=1,
                   created_time=datetime.now(),
                   updated_time=datetime.now()).save()
        return Http.gen_success_response(message='助力成功.')


"""
class TrialStage(fields.Raw):
    def format(self, value):
        args = memberinfo_get_parser.parse_args()
        # 验证token
        try:
            member = check_token(uid=args['uid'], token=args['token'], fake=False)
        except Exception as e:
            return Http.gen_failure_response(message=e.__str__())
        application = Application.objects(member=member, trial=ObjectId(value)).first()
        if application is None:
            return {'number': 0, 'desc': '申请试用'}
        else:
            return application.stage
"""

# -*- coding: utf-8 -*-
from flask_login import abort
from flask import jsonify
from flask_restful import Resource
from flask_login import current_app
from extensions import check_password
from common.date import Date
from common import Log
from .parser import user_post_parser
from trialcenter.models.admin import User


class AuthApi(Resource):
    def post(self):
        """
        系统(后台管理)用户认证
        调用接口需要提供Email/Password, 返回Token和有效时间。
        ---
        tags:
          - 系统接口
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  description: 用户邮箱.
                  example: "logan@52fisher.com"
                password:
                  type: string
                  description: 用户密码.
                  example: "helloworld"
        responses:
          401:
            description: 认证失败!
          200:
            description: 返回Token和有效时间
            examples:
              json: {'token': 'eyJhbGciOiJIUzI1NiIsImlhdCI6MTU0NzcyMjY0MCwiZXhwIjoxNTQ3NzIyOTQwfQ.eyJpZCI6IjVjMzgzNTNkNmZlYmJiMDcyNTE0OGE1OCJ9._BjoZS8TMAifNik21hO6xpSVyHXEzRDmMrmWiRVgx0s', 'expires_in':1547716978}

        """
        args = user_post_parser.parse_args()
        user = User.objects(email=args['email']).first()

        if user:
            if check_password(user.password, args['password']):
                Log.info('{} got auth token.'.format(user.email))
                expires_in = current_app.config['AUTH_TOKEN_MAX_AGE']
                token = user.generate_auth_token(expires_in=expires_in)
                return {'token': str(token, encoding="utf-8"), 'expires_in': Date.current_timestamp() + expires_in}, 200

        abort(401)

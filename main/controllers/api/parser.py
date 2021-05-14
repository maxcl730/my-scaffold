# -*- coding: utf-8 -*-
from werkzeug.datastructures import FileStorage
from flask_restful import reqparse

# 系统接口参数解析器
member_login_parser = reqparse.RequestParser()
member_login_parser.add_argument(
    'national_id',
    type=str,
    required=True,
    location=['args', 'form'],
    help="Member's national_id is required!"
)
member_login_parser.add_argument(
    'password',
    type=str,
    required=True,
    location=['args', 'form'],
    help="Password is required!"
)

# 会员注册参数解析器
member_register_parser = reqparse.RequestParser()
member_register_parser.add_argument(
    'national_id',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help="<national_id> is required!"
)
member_register_parser.add_argument(
    'mobile',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help="<mobile> is required!"
)
member_register_parser.add_argument(
    'password',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help="<password> is required!"
)
member_register_parser.add_argument(
    'birthday',
    type=str,
    required=False,
    location=['args', 'form', 'json'],
    # help="<password> is required!"
)
member_register_parser.add_argument(
    'sex',
    type=str,
    required=False,
    location=['args', 'form', 'json'],
    # help="<password> is required!"
)
member_register_parser.add_argument(
    'nickname',
    type=str,
    required=False,
    location=['args', 'form', 'json'],
    # help="<password> is required!"
)
member_register_parser.add_argument(
    'language',
    type=str,
    required=False,
    location=['args', 'form', 'json'],
    # help="<password> is required!"
)

uid_token_parser = reqparse.RequestParser()
uid_token_parser.add_argument(
    'uid',
    type=str,
    required=True,
    location=['args', 'form'],
    help="<uid> is required!"
)
uid_token_parser.add_argument(
    'token',
    type=str,
    required=True,
    location=['args', 'form'],
    help="<token> is required!"
)

# 分页参数
pagination_get_perser = uid_token_parser.copy()
pagination_get_perser.add_argument(
    'page',
    type=int,
    location=['args', 'form'],
)
pagination_get_perser.replace_argument(
    'uid',
    type=str,
    location=['args', 'form', 'json'],
)
pagination_get_perser.replace_argument(
    'token',
    type=str,
    location=['args', 'form', 'json'],
)

member_info_post_parser = member_register_parser.copy()
member_info_post_parser.remove_argument('national_id')
# member_info_post_parser.remove_argument('password')

# 用户申请试用
application_get_parser = uid_token_parser.copy()
application_get_parser.add_argument(
    'trial_id',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Trial_id is required.'
)

application_post_parser = application_get_parser.copy()
application_post_parser.add_argument(
    'content',
    type=str,
    required=True,
    location=['form', 'json'],
    help="Application's declaration is required."
)
application_post_parser.add_argument(
    'username',
    type=str,
    required=True,
    location=['form', 'json'],
    help="Username is required."
)
application_post_parser.add_argument(
    'tel_number',
    type=str,
    required=True,
    location=['form', 'json'],
    help="Tel_number is required."
)
application_post_parser.add_argument(
    'province_name',
    type=str,
    required=True,
    location=['form', 'json'],
    help="Province_name is required."
)
application_post_parser.add_argument(
    'city_name',
    type=str,
    required=True,
    location=['form', 'json'],
    help="City_name is required."
)
application_post_parser.add_argument(
    'detail_info',
    type=str,
    required=True,
    location=['form', 'json'],
    help="Detail_info is required."
)
application_post_parser.add_argument(
    'national_code',
    type=str,
    default='086',
    location=['form', 'json'],
)
application_post_parser.add_argument(
    'county_name',
    type=str,
    default='中国',
    location=['form', 'json'],
)
application_post_parser.add_argument(
    'postal_code',
    type=str,
    default='',
    location=['form', 'json'],
)
application_post_parser.add_argument(  # 小程序消息form_id
    'form_id',
    type=str,
    default='',
    location=['form', 'json'],
)

# 上传图片接口
upload_post_parser = uid_token_parser.copy()
upload_post_parser.add_argument(
    'file',
    type=FileStorage,
    location='files',
    required=True,
    help='<file> is required.'
)
upload_post_parser.add_argument(
    'width',
    type=int,
    location=['args', 'form', 'json'],
)
upload_post_parser.add_argument(
    'height',
    type=int,
    location=['args', 'form', 'json'],
)
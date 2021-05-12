# -*- coding: utf-8 -*-
from werkzeug.datastructures import FileStorage
from flask_restful import Resource, reqparse

# 系统接口参数解析器
user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument(
    'email',
    type=str,
    required=True,
    location=['form'],
    help="User's email is required!"
)
user_post_parser.add_argument(
    'password',
    type=str,
    required=True,
    location=['form'],
    help="Password is required!"
)


# 会员接口参数解析器
memberlogin_get_parser = reqparse.RequestParser()
memberlogin_get_parser.add_argument(
    'code',
    type=str,
    required=True,
    location=['args'],
    help="<code> is required!"
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


memberinfo_get_parser = uid_token_parser.copy()

memberinfo_post_parser = uid_token_parser.copy()
memberinfo_post_parser.add_argument(
    'iv',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help="<iv> is required."
)
memberinfo_post_parser.add_argument(
    'encrypted_data',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help="<encryptedData> is required."
)

favorite_get_parser = uid_token_parser.copy()
favorite_get_parser.add_argument(
    'type',
    type=str,
    default='trial',
    location=['args', 'form', 'json'],
)
favorite_get_parser.add_argument(
    'page',
    type=int,
    location=['args', 'form'],
)


favorite_post_parser = uid_token_parser.copy()
favorite_post_parser.add_argument(
    'trial_id',
    type=str,
    location=['args', 'form', 'json'],
)
favorite_post_parser.add_argument(
    'report_id',
    type=str,
    location=['args', 'form', 'json'],
)
favorite_post_parser.add_argument(
    'action',
    required=True,
    type=str,
    location=['args', 'form', 'json'],
)

# 喜欢报告参数
like_report_post_parser = uid_token_parser.copy()
like_report_post_parser.add_argument(
    'report_id',
    required=True,
    type=str,
    location=['args', 'form', 'json'],
)
like_report_post_parser.add_argument(
    'action',
    required=True,
    type=str,
    location=['args', 'form', 'json'],
)

# 分享报告参数
share_report_post_parser = uid_token_parser.copy()
share_report_post_parser.add_argument(
    'report_id',
    required=True,
    type=str,
    location=['args', 'form', 'json'],
)
share_report_post_parser.replace_argument(
    'uid',
    type=str,
    location=['args', 'form', 'json'],
)
share_report_post_parser.replace_argument(
    'token',
    type=str,
    location=['args', 'form', 'json'],
)

# 试用信息参数解析器
trial_get_parser = uid_token_parser.copy()
trial_get_parser.add_argument(
    'trial_id',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Trial_id is required.'
)
trial_get_parser.replace_argument(
    'uid',
    type=str,
    location=['args', 'form', 'json'],
)
trial_get_parser.replace_argument(
    'token',
    type=str,
    location=['args', 'form', 'json'],
)
trial_get_parser.add_argument(
    'page',
    type=int,
    location=['args', 'form'],
)


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

# 用户提交报告
report_post_parser = uid_token_parser.copy()
report_post_parser.add_argument(
    'application_id',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Application_id is required.'
)
report_post_parser.add_argument(
    'position_name',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Position_name is required.'
)
report_post_parser.add_argument(
    'content',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Content is required.'
)
report_post_parser.add_argument(
    'images',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='images is required.'
)
report_post_parser.add_argument(  # 小程序消息form_id
    'form_id',
    type=str,
    default='',
    location=['form', 'json'],
)

# 获取报告信息
reportinfo_get_parser = uid_token_parser.copy()
reportinfo_get_parser.replace_argument(
    'uid',
    type=str,
    location=['args', 'form', 'json'],
)
reportinfo_get_parser.replace_argument(
    'token',
    type=str,
    location=['args', 'form', 'json'],
)
reportinfo_get_parser.add_argument(
    'report_id',
    required=True,
    type=str,
    location=['args', 'form', 'json'],
)

# 更新报告信息参数
reportinfo_post_parser = report_post_parser.copy()
reportinfo_post_parser.remove_argument('application_id')
reportinfo_post_parser.add_argument(
    'report_id',
    required=True,
    type=str,
    location=['args', 'form', 'json'],
)

# 邀请页面接口
invitation_get_parser = uid_token_parser.copy()
invitation_get_parser.add_argument(
    'invitation_code',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Invitation_code is required.'
)
invitation_get_parser.add_argument(
    'trial_id',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Trial_id is required.'
)

# 助力接口
help_post_parser = uid_token_parser.copy()
help_post_parser.add_argument(
    'invitation_code',
    type=str,
    required=True,
    location=['args', 'form', 'json'],
    help='Invitation_code is required.'
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
# -*- coding: utf-8 -*-
from .member import MemberLoginApi, MemberAuthApi, MemberRegisterApi, MemberInfoApi
#from .homepage import HomepageApi
#from .application import ApplicationListApi, SuccessApplicationApi
from pprint import pprint


def api_setup(api=None):
    if not api:
        return False

    api.add_resource(
        MemberLoginApi,
        '/member/login',
        endpoint='api_member_login'
    )

    api.add_resource(
        MemberAuthApi,
        '/member/auth',
        endpoint='api_member_auth'
    )

    api.add_resource(
        MemberRegisterApi,
        '/member/register',
        endpoint='api_member_register'
    )

    api.add_resource(
        MemberInfoApi,
        '/member/info',
        endpoint='api_member_info'
    )

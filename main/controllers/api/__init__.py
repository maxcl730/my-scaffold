# -*- coding: utf-8 -*-
from .auth import AuthApi
from .member import MemberLoginApi, MemberInfoApi, MemberApplicationApi, MemberReportApi, MemberFavoriteApi, \
    MemberApplyApi, MemberInvitationCode, MemberInvitation, MemberHelp
from .homepage import HomepageApi
from .application import ApplicationListApi, SuccessApplicationApi


def api_setup(api=None):
    if not api:
        return False

    api.add_resource(
        AuthApi,
        '/auth',
        endpoint='api_auth'
    )
    # Add member relation api
    api.add_resource(
        MemberLoginApi,
        '/member/login',
        endpoint='api_member_bind'
    )
    api.add_resource(
        MemberInfoApi,
        '/member/info',
        endpoint='api_member_info'
    )
    api.add_resource(
        HomepageApi,
        '/homepage',
        endpoint='api_homepage'
    )
    api.add_resource(
        ApplicationListApi,
        '/application/list',
        endpoint='api_application_list'
    )
    api.add_resource(
        SuccessApplicationApi,
        '/application/list/success',
        endpoint='api_application_list_success'
    )
    api.add_resource(
        MemberApplicationApi,
        '/member/application',
        endpoint='api_member_application'
    )
    api.add_resource(
        MemberReportApi,
        '/member/report',
        endpoint='api_member_report'
    )
    api.add_resource(
        MemberFavoriteApi,
        '/member/favorite',
        endpoint='api_member_favorite'
    )
    api.add_resource(
        MemberApplyApi,
        '/member/apply',
        endpoint='api_member_apply'
    )
    api.add_resource(
        MemberInvitationCode,
        '/member/invitation/code',
        endpoint='api_member_invitation_code'
    )
    api.add_resource(
        MemberInvitation,
        '/member/invitation',
        endpoint='api_member_invitation'
    )
    api.add_resource(
        MemberHelp,
        '/member/help',
        endpoint='api_member_help'
    )

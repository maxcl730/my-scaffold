# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from flask import current_app
from trialcenter.models.notify import NotifyRecord
from trialcenter.models.member import MemberFormID
from common.wechat import WXApp
from common.date import Date
from common.helper.mapping import application_status_desc, report_status_desc
from common import Log


def new_notify(notify_id=0, trial=None, member_form_id=None, application=None, delay=300):
    # 新建一条通知, delay 默认延时5分钟后发送
    if notify_id not in current_app.config['WX_NOTIFY_TEMPLATES'].keys() or trial is None or member_form_id is None:
        return False
    Log.info("New notify {} - {}".format(notify_id, application))
    template = current_app.config['WX_NOTIFY_TEMPLATES'][notify_id]
    notify = NotifyRecord()
    notify.title = template['title']
    notify.form_id = member_form_id.form_id
    notify.template_id = template['template_id']
    member = member_form_id.member
    notify.trial = trial
    notify.member = member
    notify.application = application
    notify.created_time = notify.updated_time = datetime.now()
    notify.planning_time = datetime.now() + timedelta(seconds=delay)
    # 生成消息数据
    page_arguments = ''
    send_data = dict()
    send_data["keyword1"] = {"value": trial.title}  # 试用名称
    if notify_id == 1:
        page_arguments = '?id=' + trial.id.__str__() + '&uid=' + member.id.__str__() + '&token=' + member.geneToken()
        send_data["keyword2"] = {"value": Date.datetime_toString(trial.begin_time,
                                                                 with_time=False,
                                                                 date_separator='-')}  # 申请时间
        send_data["keyword3"] = {"value": trial.good_name}  # 商品名称
        # Log.info(send_data)
    elif notify_id in [2, 3]:
        if application is None:
            return False
        send_data["keyword2"] = {"value": application_status_desc(application.status)}  # 试用结果
        if application.status == 4:
            page_arguments = '?uid=' + member.id.__str__() + '&token=' + member.geneToken()
            send_data["keyword3"] = {"value": '您与体验产品擦肩而过，更多好物免费体验中，点击查看。'}
        else:
            page_arguments = '?id=' + trial.id.__str__() + '&uid=' + member.id.__str__() + '&token=' + member.geneToken()
            send_data["keyword3"] = {"value": '恭喜你获得好物体验，为了保证安全快速我们采用顺丰到付，收到后5日内提交报告，点击查看新的免费体验。加微信jing-muxuan拉你进体验群，获得优先试用资格。'}
        send_data["keyword4"] = {"value": member.nickname}  # 申请人
        send_data["keyword5"] = {"value": Date.datetime_toString(application.created_time,
                                                                 with_time=False,
                                                                 date_separator='-')}  # 申请时间
        # Log.info(send_data)
    notify.data = json.dumps(send_data)
    notify.page = template['page'] + page_arguments
    notify.save()
    return True


def send_notify(app):
    all_pending_notify = NotifyRecord.objects(planning_time__lte=datetime.now(),
                                              cancelled=False,
                                              result_code=-1)
    wechat_app = WXApp(app)
    success_count = 0
    failed_count = 0
    for notify in all_pending_notify:
        result = wechat_app.push_notify(template_id=notify.template_id,
                                        openid=notify.application.member.bind_wechat.openid,
                                        form_id=notify.form_id,
                                        page=notify.page,
                                        data=notify.data)
        notify.result_code = result['errcode'] if 'errcode' in result else -1
        if notify.result_code == 0:
            success_count += 1
        else:
            failed_count += 1
        notify.result_msg = result['errmsg'] if 'errmsg' in result else ''
        notify.sent_time = notify.updated_time = datetime.now()
        notify.save()
    return {'success_count': success_count, 'failed_count': failed_count}

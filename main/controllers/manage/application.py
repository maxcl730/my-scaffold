# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from bson.son import SON
from flask import current_app, Blueprint, request, abort, jsonify, flash, redirect
from flask_security import login_required
from common.helper import ops_render
from trialcenter.models.member import Application, Member, MemberFormID
from trialcenter.models.trial import Trial
from trialcenter.form import ApplicationSearchForm, GoodNameForm
from extensions import cache
from common import Log

application_bp = Blueprint('manage_application', __name__,)


@cache.cached(timeout=600, key_prefix='province_list')
def list_province_name():
    # 获取省份列表
    province_set = set(Application.objects(address__ne=None).values_list('address__province_name'))
    province_list = list()
    province_list.append(('全部', '全部'))
    for province in province_set:
        province_list.append((province, province))
    return province_list


def filter_application(form, temp_applications):
    if form.good_name.data:
        # 产品名称
        trials = Trial.objects(good_name__icontains=form.good_name.data)
        temp_applications = temp_applications.filter(trial__in=trials)
    if form.nickname.data:
        # 用户昵称
        members = Member.objects(nickname__icontains=form.nickname.data)
        temp_applications = temp_applications.filter(member__in=members)
    if form.mobile.data:
        # 用户地址中的手机号
        temp_applications = temp_applications.filter(address__tel_number__icontaions=form.mobile.data)
    if form.province_name.data != '全部':
        # 所在省份
        temp_applications = temp_applications.filter(address__province_name=form.province_name.data)
    if form.running_status.data in [1, 2]:
        # 试用状态
        if form.running_status.data == 1:  # 进行中
            trials = Trial.objects(begin_time__lt=datetime.now(),
                                   end_time__gt=datetime.now())
        else:  # 已结束
            trials = Trial.objects(end_time__lt=datetime.now())
        temp_applications = temp_applications.filter(trial__in=trials)
    if form.Apply_number.data:
        # 申请次数
        members_count = list(Application.objects.aggregate({'$group': {'_id': '$member', 'count': {'$sum': 1}}},
                                                     {"$sort": SON([("count_member", -1)])},
                                                     {'$match': {"count": {"$gt": form.Apply_number.data}}}))
        members = [member['_id'] for member in members_count]
        temp_applications = temp_applications.filter(member__in=members)
    if form.created_time_begin.data:
        temp_applications = temp_applications.filter(created_time__gte=form.created_time_begin.data)
    if form.created_time_end.data:
        temp_applications = temp_applications.filter(created_time__lte=form.created_time_end.data + timedelta(seconds=86399))

    return temp_applications


@application_bp.route("/all_application", methods=['GET', 'POST'])
@application_bp.route("/all_application/<int:page>", methods=['GET', 'POST'])
@login_required
def list_application_all(page=1):
    list_per_page = current_app.config['MANAGEMENT_LIST_PER_PAGE']
    navbar_title = '全部申请列表'
    form = ApplicationSearchForm()
    form.province_name.choices = list_province_name()
    applications = Application.objects()
    if request.method == 'POST':
        applications = filter_application(form=form, temp_applications=applications)
    response_data = {
        'form': form,
        'navbar_title': navbar_title,
        'show_download': False,
        'list': applications.paginate(page=page, per_page=list_per_page),
        'filter': sys._getframe().f_code.co_name,
    }
    return ops_render('manage/application/index.html', response_data)


@application_bp.route("/noaudit_application", methods=['GET', 'POST'])
@application_bp.route("/noaudit_application/<int:page>", methods=['GET', 'POST'])
@login_required
def list_application_noaudit(page=1):
    list_per_page = current_app.config['MANAGEMENT_LIST_PER_PAGE']
    navbar_title = '未审核申请列表'
    form = ApplicationSearchForm()
    form.province_name.choices = list_province_name()
    applications = Application.objects(status=0)
    if request.method == 'POST':
        applications = filter_application(form=form, temp_applications=applications)
    response_data = {
        'form': form,
        'navbar_title': navbar_title,
        'show_download': False,
        'list': applications.paginate(page=page, per_page=list_per_page),
        'filter': sys._getframe().f_code.co_name,
    }
    return ops_render('manage/application/index.html', response_data)


@application_bp.route("/success_application", methods=['GET', 'POST'])
@application_bp.route("/success_application/<int:page>", methods=['GET', 'POST'])
@login_required
def list_application_success(page=1):
    list_per_page = current_app.config['MANAGEMENT_LIST_PER_PAGE']
    navbar_title = '申请成功列表'
    form = ApplicationSearchForm()
    form_download = GoodNameForm()
    form.province_name.choices = list_province_name()
    applications = Application.objects(status=1)
    if request.method == 'POST':
        applications = filter_application(form=form, temp_applications=applications)
    response_data = {
        'form': form,
        'form_download': form_download,
        'navbar_title': navbar_title,
        'show_download': True,
        'list': applications.paginate(page=page, per_page=list_per_page),
        'filter': sys._getframe().f_code.co_name,
    }
    return ops_render('manage/application/index.html', response_data)


@application_bp.route("/success_application_xls", methods=['POST'])
@login_required
def download_application_success():
    form = GoodNameForm()
    trials = Trial.objects(good_name__icontains=form.good_name.data)
    applications = Application.objects(status=1).filter(trial__in=trials)
    # applications = Application.objects().filter(trial__in=trials)
    from flask import send_from_directory, make_response
    import os
    from common.excel import Excel
    from urllib.parse import quote
    recipients = list()
    path = '/tmp/'
    filename = form.good_name.data + '-发货名单.xls'
    if os.path.exists(path+filename):
        os.remove(path+filename)
    excel = Excel(filename=path+filename)
    column = 0
    excel.write(column, 0, content='收方姓名')
    excel.write(column, 1, content='收方联系方式')
    excel.write(column, 2, content='收方地址')
    excel.write(column, 3, content='商品名称')
    for app in applications:
        column += 1
        if app.member.address.province_name == app.member.address.city_name:
            province_city = app.member.address.city_name
        else:
            province_city = app.member.address.province_name + app.member.address.city_name
        excel.write(column, 0, content=app.member.address.username)
        excel.write(column, 1, content=app.member.address.tel_number)
        excel.write(column, 2, content=province_city + app.member.address.county_name + app.member.address.detail_info)
        excel.write(column, 3, content=app.trial.good_name)
        recipients.append({
            'name': app.member.address.username,
            'mobile': app.member.address.tel_number,
            'address': province_city + app.member.address.county_name + app.member.address.detail_info,
            'good_name': app.trial.good_name,

        })
        # Log.info(recipients)
    excel.save()
    response = make_response(send_from_directory(path, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(quote(filename.encode().decode('utf-8')))
    return response


@application_bp.route("/delivered_application", methods=['GET', 'POST'])
@application_bp.route("/delivered_application/<int:page>", methods=['GET', 'POST'])
@login_required
def list_application_delivered(page=1):
    list_per_page = current_app.config['MANAGEMENT_LIST_PER_PAGE']
    navbar_title = '已发货列表'
    form = ApplicationSearchForm()
    form.province_name.choices = list_province_name()
    applications = Application.objects(status=2)
    if request.method == 'POST':
        applications = filter_application(form=form, temp_applications=applications)
    response_data = {
        'form': form,
        'navbar_title': navbar_title,
        'show_download': False,
        'list': applications.paginate(page=page, per_page=list_per_page),
        'filter': sys._getframe().f_code.co_name,
    }
    return ops_render('manage/application/index.html', response_data)


@application_bp.route("/change_application_status", methods=['POST'])
@login_required
def change_application_status():
    data = request.get_json()
    application_id = data['id'] if 'id' in data else ''
    status = data['status'] if 'status' in data else None
    # Log.info(application_id)
    if len(application_id) != 24 or status not in ['0', '1', '2', '4', '99']:
        abort(400)
    try:
        application = Application.objects(id=ObjectId(application_id)).first()
        if application.trial.end_time > datetime.now() and status != '99':
            return jsonify({'code': -1, 'message': '试用仍未结束，不能审批申请', 'data': {}})
        success_application_count = Application.objects(trial=application.trial, status__in=[1, 2]).count()
        if status in ['1', '2'] and success_application_count >= application.trial.quantity:
            # Log.info(success_application_count)
            from common.helper.urlmanager import redirect_back
            flash('【{}】活动的可申请数量已经达到上限({})!'.format(application.trial.title, application.trial.quantity))
            redirect(redirect_back('manage_application.list_application_all'))
            # return jsonify({'code': -1, 'message': '可申请数量已经达到上限！', 'data': {}})
        application.status = int(status)
        application.updated_time = datetime.now()
        application.save()
        if status in ['1', '2', '4']:
            from common.helper.notify import new_notify
            member_form_id = MemberFormID.objects(member=application.member).order_by('created_time').first()
            if status == 4:
                new_notify(notify_id=3, trial=application.trial, member_form_id=member_form_id, application=application)
            else:
                new_notify(notify_id=2, trial=application.trial, member_form_id=member_form_id, application=application)
            member_form_id.delete()
        return jsonify({'code': 0, 'message': 'success', 'data': {}})
    except:
        return jsonify({'code': -1, 'message': 'failure', 'data': {}})

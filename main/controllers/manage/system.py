# -*- coding: utf-8 -*-
from flask import current_app, Blueprint, redirect, abort, url_for, flash, jsonify, request
from flask_security import login_required
from bson.objectid import ObjectId
from common.helper import ops_render
from main.models.admin import User
from extensions import user_datastore, set_password
from main.form import UserForm, UserPasswdForm
from common import Log

system_bp = Blueprint('manage_system', __name__,)


@system_bp.route("/list_user", methods=['GET', 'POST'])
@system_bp.route("/list_user/<int:page>", methods=['GET', 'POST'])
@login_required
def list_user(page=1):
    list_per_page = current_app.config['MANAGEMENT_LIST_PER_PAGE']
    users = User.query.paginate(page=page, per_page=list_per_page, error_out=False)
    response_data = {
        'list': users,
    }
    return ops_render('manage/system/userlist.html', response_data)


@system_bp.route("/ajax_focus/update", methods=['PUT'])
@login_required
def update_user():
    if request.method != 'PUT':
        return jsonify({'code': -1, 'message': 'Request method is not allowed.', 'data': {}})

    args = request.values
    uid = args['pk'] if 'pk' in args else ''
    # Log.info(focus_id)
    if len(uid) != 24:
        return jsonify({'code': -1, 'message': 'Invalid uid', 'data': {}})
    value = args['value'] if 'value' in args else None
    name = args['name'] if 'name' in args else None
    if value is None or name is None:
        return jsonify({'code': -1, 'message': 'Miss parameter or invalid parameter value.', 'data': {}})

    if name == 'name':
        # 修改姓名
        User.query.filter_by(id='uid').update({'name': value})
        return jsonify({'code': 0, 'message': 'success', 'data': {}})
    elif name == 'active':
        # 修改状态
        if value == '1':
            User.query.filter_by(id='uid').update({'active': True})
        else:
            User.query.filter_by(id='uid').update({'active': False})
        return jsonify({'code': 0, 'message': 'success', 'data': {}})
    else:
        return jsonify({'code': -1, 'message': 'Miss parameter or invalid parameter value.', 'data': {}})


@system_bp.route("/new_user", methods=['GET', 'POST'])
@login_required
def new_user():
    # 创建新用户
    form = UserForm()
    response_data = {
        'form': form,
    }
    if request.method == 'POST' and form.validate_on_submit():
        # 创建新账号
        if user_datastore.get_user(form.email.data):
            flash('该邮箱已注册!')
            Log.info(form.email.errors) # = '该邮箱已注册，请使用其他邮箱!'
            return ops_render('manage/system/useredit.html', response_data)
        admin_role = user_datastore.find_role('Admin')
        admin = user_datastore.create_user(email=form.email.data,
                                           name=form.name.data,
                                           password=set_password(form.passwd.data))
        # 为admin添加Admin角色(admin_role)
        user_datastore.add_role_to_user(admin, admin_role)
        flash('账号创建成功!')
        return redirect(url_for('manage_system.list_user'))
    return ops_render('manage/system/useredit.html', response_data)


@system_bp.route("/user_reset_password/<string:uid>", methods=['GET', 'POST'])
@login_required
def user_reset_password(uid=None):
    # 初始化用户密码
    if uid is None:
        abort(400)
    if len(uid) != 24:
        abort(404)
    form = UserPasswdForm()
    user = User.objects(id=ObjectId(uid)).first()
    if user is None:
        abort(404)
    response_data = {
        'form': form,
        'uid': uid,
        'email': user.email,
        'name': user.name,
    }
    if request.method == 'POST' and form.validate_on_submit():
        User.query.filter_by(id='uid').update({'password': set_password(form.passwd.data)})
        flash('账号密码已重置.')
        return redirect(url_for('manage_system.list_user'))
    return ops_render('manage/system/userpasswd.html', response_data)


@system_bp.route("/delete_user/<string:uid>", methods=['GET'])
@login_required
def delete_user(uid=None):
    if uid and len(uid) == 24:
        user_datastore.delete_user(User.objects(id=ObjectId(uid)).first())
        flash('账号已删除!')
        return redirect(url_for('manage_system.list_user'))
    else:
        abort(404)

# -*- coding: utf-8 -*-
from flask import current_app, Blueprint, render_template
from flask_babelex import Domain, refresh, lazy_gettext, _
from flask_security import login_required
from common.helper import ops_render
from common.helper.urlmanager import UrlManager
from .member import member_bp
#from .homepage import homepage_pb
#from .application import application_bp
from .system import system_bp
from common import Log

manage_bp = Blueprint('manage', __name__,)


@manage_bp.route('/')
@login_required
def index():
    refresh()
    # day = "Saturday"
    response_data = {
        'day': "Saturday",
    }
    return ops_render('manage/index.html', response_data)
    #return render_template('manage/index.html', day=day)
    #return render_template('index.html', day=day)


def reg_bp(app):
    app.register_blueprint(manage_bp, url_prefix="/manage")
    app.register_blueprint(member_bp, url_prefix="/manage/member")
    #app.register_blueprint(homepage_pb, url_prefix='/manage/homepage')
    #app.register_blueprint(application_bp, url_prefix='/manage/application')
    app.register_blueprint(system_bp, url_prefix='/manage/system')

# -*- coding: utf-8 -*-
from flask import Flask, Blueprint, redirect, url_for, request
import pkg_resources
from flask_restful import Api
# from flask_debugtoolbar import DebugToolbarExtension
from .controllers import manage  # , api
from .config import config
from extensions import flask_security, user_datastore, flask_bable, swagger  # ,login_manager, flask_session, flask_bootstrap
from database import db
from common import Log


def create_app(config_name='production'):
    """Create the app instance via Factory Method"""

    app = Flask(__name__)

    # Set the app config
    app.config.from_object(config[config_name])
    app.config["SECURITY_I18N_DIRNAME"] = [pkg_resources.resource_filename("flask_security", "translations"),
                                           "translations"]
    app.secret_key = app.config['SECRET_KEY']
    # setup autoreload jinja cache
    app.jinja_env.auto_reload = True
    # Init db
    db.init_app(app)

    # DebugToolbarExtension(app)

    # Init the Flask-Session via app object
    # flask_session.init_app(app)

    # Init the Flask-Login via app object
    # login_manager.init_app(app)

    # Setup Flask-Security
    flask_security.init_app(app, user_datastore)  # register_form=ExtendedRegisterForm)

    # Init the Flask-Bable via app object
    flask_bable.init_app(app)

    # Init the Flask-bootstrap via app object
    # flask_bootstrap.init_app(app)

    # Init the swgger via app object
    swagger.init_app(app)

    # Init the Flask-Restful via app object
    restful_api_bp = Blueprint('api_v1', __name__, url_prefix=app.config['API_PREFIX'] + '/v1')
    #restful_api = Api(restful_api_bp)
    #api.api_setup(restful_api)

    app.register_blueprint(restful_api_bp)

    #函数模板
    from common.helper.urlmanager import UrlManager
    app.add_template_global(UrlManager.makeup_static_url, 'makeup_static_url')
    app.add_template_global(UrlManager.makeup_image_url, 'makeup_image_url')
    from common.fields import str2json
    app.add_template_global(str2json, 'str2json')
    from common.date import Date
    app.add_template_global(Date.datetime_calculate, 'datetime_calculate')
    manage.reg_bp(app)

    @app.route('/')
    def index():
        from flask_babelex import refresh
        refresh()
        return redirect(url_for('security.login'))

    @flask_bable.localeselector
    def get_local():
        language = request.accept_languages.best_match(['zh', 'en'])
        language = 'zh_Hans_CN' if language == 'zh' else 'en'
        # Log.info(language)
        return language

    return app


if __name__ == '__main__':
    # Entry the application
    flask_app = create_app()
    flask_app.run()

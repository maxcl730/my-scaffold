# -*- coding: utf-8 -*-
# from flask_login import LoginManager
from flask_babelex import Babel
# from flask_session import Session
from flask_bootstrap import Bootstrap
from flasgger import Swagger
from flask_security import Security, SQLAlchemySessionUserDatastore, login_required
from flask_security.utils import hash_password, verify_password
from database import db
from main.models.admin import User, Role

# flask-security
flask_security = Security()
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)

# Create the Flask-login's instance
# login_manager = LoginManager()
# Setup the configuration for login manager
# 1. Set the login page.
# 2. Set the more stronger auth-protection.
# 3. Show the information when you are logging.
# 4. Set the Login Messages type as 'information'.
# login_manager.login_view = 'security.login'
# login_manager.session_protection = 'strong'
# login_manager.login_message = 'Please login to access this page.'
# login_manager.login_message_category = 'info'

# Flask-Babel
flask_bable = Babel()

# Create the Flask-Session instance
# flask_session = Session()

# Create the Flask-bootstrap instance
flask_bootstrap = Bootstrap()

# Create the Swagger instance
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apidoc/spec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
swagger = Swagger(config=swagger_config)

'''
@login_manager.user_loader
def load_user(user_id):
    """ Load the user's info."""
    return User.get_id(user_id)
'''


def set_password(password):
    return hash_password(password)


def check_password(pw_hash, password):
    return verify_password(password, pw_hash)


# -*- coding: utf-8 -*-
class Config(object):
    """Base config class."""
    SECRET_KEY = '\2\1banruzangshouhuli\1\2\e\y\y\h'
    PORT = 33201
    LISTEN = '*:' + str(PORT)
    BIND = '0.0.0.0'
    RELEASE_VERSION = '2021051017'

    INVITATION_CODE_TTL = 86400
    APP = {
        'domain': 'https://loan.com/',
    }
    MANAGEMENT_LIST_PER_PAGE = 20
    FRONTEND_LIST_PER_PAGE = 10

    # Images upload config
    # UPLOAD_FOLDER = '/data/app/upload'
    # IMAGE_URL_PREFIX = 'https://app.rushouli.com/upload/'
    # ALLOWED_EXTENSIONS = set(['jpg', 'gif', 'jpeg', 'png', 'bmp'])
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16M

    # Restful API
    API_PREFIX = '/api'

    # Swgger
    SWAGGER = {
        'title': 'Loan API',
        'version': 'v1',
    }

    # Debug
    DEBUG = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Auto reload template when they have been changed
    TEMPLATES_AUTO_RELOAD = True
    # Flask-Security config
    # SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "logan&fisher"
    # SECURITY_USER_IDENTITY_ATTRIBUTES = 'email'
    SECURITY_I18N_DOMAIN = "messages"
    # Flask-Security URLs, overridden because they don't put a / at the end
    # SECURITY_URL_PREFIX = "/admin"
    SECURITY_LOGIN_URL = "/manage/user/login/"
    SECURITY_LOGOUT_URL = "/manage/user/logout/"
    SECURITY_RESET_URL = "/manage/user/resetpwd/"
    SECURITY_CHANGE_URL = "/manage/user/changepwd/"
    # SECURITY_REGISTER_URL = "/register/"

    SECURITY_POST_LOGIN_VIEW = "/manage/"
    SECURITY_POST_LOGOUT_VIEW = SECURITY_LOGIN_URL
    # SECURITY_POST_REGISTER_VIEW = "/admin/"
    # Flask-Security features
    # SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_TRACKABLE = True

    # The allowed translation for you app
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGE = ['zh', 'en', 'fr']
    # BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'

    # Flask-Session configuration
    # SESSION_TYPE = 'redis'
    SESSION_TYPE = 'filesystem'
    # SESSION_REDIS = Redis(host='192.168.1.203', port=6379)
    SESSION_KEY_PREFIX = '52loan'

    # Auth token
    AUTH_TOKEN_MAX_AGE = 300


class ProductionConfig(Config):
    """Production config calss."""
    # Flask-Cache's config
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'trial_'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    # CACHE_REDIS_PASSWORD = ''
    # CACHE_REDIS_DB = 1
    # CACHE_REDIS_URL = redis://user:password@localhost:6379/1


class DevelopmentConfig(Config):
    """Development config class."""
    PORT = 5000
    LISTEN = '*:' + str(PORT)

    # Open Debug
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PANELS=['flask_debugtoolbar.panels.timer.TimerDebugPanel',
                     # 'flask_mongoengine.panels.MongoDebugPanel',
                     'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
                     'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                     'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
                     'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                     'flask_debugtoolbar.panels.logger.LoggingPanel',
                     'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
                     'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
                     ]
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://logan:chengliang@192.168.0.70/logan_test?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENCODING = "utf8mb4"

    # Images upload config
    # UPLOAD_FOLDER = '/Users/chengliang/work/dev/trialcenter/trialcenter/static/upload'
    # IMAGE_URL_PREFIX = 'https://tc.self.com.cn/static/upload/'

    # Flask-Cache's config
    CACHE_TYPE = 'simple'


config = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        }

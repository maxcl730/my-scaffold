from flask import current_app
from common.date import Date
from datetime import datetime


class Log(object):

    @classmethod
    def debug(cls, message=""):
        current_app.logger.debug("[%s] %s" %(Date.datetime_toString(datetime.now(), date_separator='-'), message))

    @classmethod
    def info(cls, message=""):
        current_app.logger.info("[%s] %s" %(Date.datetime_toString(datetime.now(), date_separator='-'), message))

    @classmethod
    def warn(cls, message=""):
        current_app.logger.warn("[%s] %s" %(Date.datetime_toString(datetime.now(), date_separator='-'), message))

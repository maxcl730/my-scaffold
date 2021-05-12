# -*- coding: utf-8 -*-
from flask_restful import fields, marshal


class Http(object):
    @classmethod
    def gen_success_response(cls, code=0, message='Success', data={}, data_format={}):
        resource_fields = {
            'code': fields.Integer(default=0),
            'message': fields.String(default='Success'),
            'data': fields.Nested(data_format),
        }

        return marshal({'code': code,
                        'message': message,
                        'data': data
                        }, resource_fields)

    @classmethod
    def gen_failure_response(cls, code=-1, message='failure'):
        return {'code': code,
                'message': message,
                }

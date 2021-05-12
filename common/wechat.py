# -*- coding: utf-8 -*-
import os
import binascii
import base64
import requests
from Crypto.Cipher import AES
from datetime import datetime
from .date import Date
import json
from pprint import pprint
import urllib3
urllib3.disable_warnings()


class WXApp(object):
    appid = ''
    secret = ''
    notify_templates = dict()

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.appid = app.config['WX_APPID']
        self.secret = app.config['WX_SECRET_KEY']
        self.notify_templates = app.config['WX_NOTIFY_TEMPLATES']

    def jscode2session(self, js_code):
        url = ('https://api.weixin.qq.com/sns/jscode2session?'
               'appid={}&secret={}&js_code={}&grant_type=authorization_code'
               ).format(self.appid, self.secret, js_code)
        # Log.info(url)
        r = requests.get(url)
        return r.json()

    def decrypt(self, session_key, encrypted_data, iv):
        # base64 decode
        session_key = base64.b64decode(session_key)
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        decrypted = json.loads(self._unpad(cipher.decrypt(encrypted_data)))

        if decrypted['watermark']['appid'] != self.appid:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def get_access_token_from_wechat(self):
        # 获取AccessToken
        payload = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.secret,
        }
        r = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=payload, timeout=3, verify=False)
        access_token_data = r.json()
        return access_token_data

    def get_access_token(self):
        data = WechatData.get_data(key='access_token')
        if data is None:
            # 新数据
            data = self.get_access_token_from_wechat()
            WechatData.set_data(key='access_token', value=data)
            data = WechatData.get_data(key='access_token')
        if data['updated_time'] + data['expires_in'] - 300 <= Date.datetime_toTimestamp(datetime.now()):
            # access_token 已过期， 300秒为更新access_token提前时间量
            data = self.get_access_token_from_wechat()
            WechatData.set_data(key='access_token', value=data)
        return data['access_token']

    def push_notify(self, template_id=None, openid=None, form_id=None, page='', data=None):
        if template_id is None or openid is None or form_id is None:
            return -1
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return -1
        post_data = {
            "touser": openid,
            "template_id": template_id,
            "page": page,
            "form_id": form_id,
            "data": json_data,
            "emphasis_keyword": '',  # "keyword1.DATA"
        }
        access_token = self.get_access_token()
        push_url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={}'.format(access_token)
        try:
            r = requests.post(push_url, json=post_data, timeout=3, verify=False)
        except requests.exceptions.ConnectionError:
            return {'errcode': -1}
        return r.json()


class WechatData(object):
    @classmethod
    def set_data(cls, key=None, value=None):
        if key is None or value is None:
            return False
        # 记录微信数据
        from trialcenter.models.wechat import Wechat
        Wechat.objects(key=key).update_one(set__value=json.dumps(value),
                                           set__updated_time=datetime.now(),
                                           upsert=True)
        return True

    @classmethod
    def get_data(cls, key=None):
        if key is None:
            return None
        # 记录微信数据
        from trialcenter.models.wechat import Wechat
        wechat_data = Wechat.objects(key=key).first()
        if wechat_data:
            data = json.loads(wechat_data['value'])
            data['updated_time'] = Date.datetime_toTimestamp(wechat_data['updated_time'])
            return data
        else:
            return None


def gen_3rd_session_key():
    """生成长度为32位的hex字符串，用于第三方session的key"""
    return binascii.hexlify(os.urandom(16)).decode()

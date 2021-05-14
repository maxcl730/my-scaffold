import requests
import json
import sys
import os.path as op
from pprint import pprint


def test_member_login(national_id, password):
    url = "http://127.0.0.1:5000/api/v1/member/login"
    params = {
        'national_id': national_id,
        'password': password,
    }
    # print(url)
    # headers = {"Content-Type": "application/text"}
    r = requests.post(url, data=params,)
    r.encoding = 'utf-8'
    return r.json()


def test_member_register(user_info):
    url = "http://127.0.0.1:5000/api/v1/member/register"
    # print(url)
    # headers = {"Content-Type": "application/text"}
    r = requests.post(url, data=user_info,)
    r.encoding = 'utf-8'
    return r.json()


def test_user_auth(auth_info):
    url = "http://127.0.0.1:5000/api/v1/member/auth?uid={}&token={}".format(auth_info['uid'], auth_info['token'])
    params = {
        'encrypted_data': 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew==',
        'iv': 'r7BXXKkLb8qrSNn05n0qiA==',
    }
    # print(url)
    # headers = {"Content-Type": "application/text"}
    #r = requests.post(url, data=params,)
    r = requests.get(url)
    r.encoding = 'utf-8'
    return r.json()


def test_user_info(auth_info):
    url = "http://127.0.0.1:5000/api/v1/member/info?uid={}&token={}".format(auth_info['uid'], auth_info['token'])
    #r = requests.post(url, data=params,)
    r = requests.get(url)
    r.encoding = 'utf-8'
    return r.json()

def post_image(filename=''):
    # url = 'http://127.0.0.1:5000/api/v1/upload'
    url = 'http://127.0.0.1:5000/manage/summernote'
    (filepath, tempfilename) = op.split(filename);
    if len(tempfilename) > 1:
        files = {
            'file': (tempfilename, open(filename, 'rb'), 'image/png', {})
        }
        res = requests.request("POST", url, data={'width': 0, 'height': 0}, files=files)
        print(res.text)


if __name__ == '__main__':
    #fn = sys.argv[1]
    #post_image(fn)

    user_info = {
        'national_id': '20210522',
        'password': 'helloworld',
        'mobile': '13911155544',
        'language': 'zh_CN',
        'birthday': '11/33/1999',
    }

    #resp_data = test_member_register(user_info)
    resp_data = test_member_login(user_info['national_id'], user_info['password'])
    #resp_data = test_user_auth(resp_data['data'])
    resp_data = test_user_info(resp_data['data'])
    pprint(resp_data)


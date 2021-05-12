import requests
import json
import sys
import os.path as op
from pprint import pprint

def post_userauth():
    url = "http://127.0.0.1:5000/api/v1/auth"
    params = {
        'email': 'logan@52fisher.com',
        'password': 'chengliang',
    }
    # print(url)
    # headers = {"Content-Type": "application/text"}
    r = requests.post(url, data=params,)
    r.encoding = 'utf-8'
    # data = json.load(r.text)
    pprint(r.text)

def post_userinfo():
    uid='5c38408b6febbb0907667e44'
    token='f08ef4cefd4218c570ebb66bb60b83cc'

    url = "http://127.0.0.1:5000/api/v1/member/info?uid={}&token={}".format(uid, token)
    params = {
        'encrypted_data': 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew==',
        'iv': 'r7BXXKkLb8qrSNn05n0qiA==',
    }
    # print(url)
    # headers = {"Content-Type": "application/text"}
    r = requests.post(url, data=params,)
    r.encoding = 'utf-8'
    # data = json.load(r.text)
    pprint(json.load(r.text))


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
    #post_userinfo()

    fn = sys.argv[1]
    post_image(fn)

    #post_userauth()

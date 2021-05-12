import base64
import json
from Crypto.Cipher import AES
import chardet


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        print(chardet.detect(sessionKey))
        encryptedData = base64.b64decode(encryptedData)
        print(chardet.detect(encryptedData))
        iv = base64.b64decode(iv)
        print(chardet.detect(iv))

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        tmp = cipher.decrypt(encryptedData)
        tmp1 = self._unpad(tmp)
        decrypted = json.loads(tmp1)

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


def main():
    appId = 'wx139b2771c0b8c381'
    secretkey = '7f9c6b60a47e7f379185a64d33212eea'

    sessionKey = '6vBcVkB0Lo8egJPeHXNopg=='
    encryptedData = 'A/7QYRwZnIMC6KIX10PUfH7W5yRhaEmJVjyzT7XNBtsIHj/WKtKUrFyYkOqbX52nILM2PS3eky42jXLMsHS+pnBLhLBfcztDINSvsoVrl0qPOw6MaYBcaz2amtLOGI8nEJJdeoW5H9Zd5BgNGWnUoZ+hU7fn0jTdBQo7iN+TzlD/03YzXybr9SUUofOipQssSmceVHDe70r+kUrqSwYruZ5ACSkdJMZnyppH2Yj9ZjedykOpz3YLzE28UcctVueZAQSunh9HV7d5Jg/oHubYMcoMetnL2KSw14Y0111HzrTvM5+CUFaSQvH1uqzjg+EeFylDqE385UozJnqUqFKfz52UoDgY95yFiXa6NTXJsLZ3rcMrcKo5z+hmDqzj/5Yp/SRiuS88d5CefOZPsMUjsQW0mfir70AdG3cVdX3RTxIjy9xpZQqb7CEjVoZ1MGgixSXqqYpU6Q9nlzSzF1bn6A=='
    iv = 'qhHXc8RUfoRIdT4wgpPTaw=='
    # pc = WXBizDataCrypt(appId, sessionKey)
    # print(pc.decrypt(encryptedData, iv))


if __name__ == '__main__':
    main()

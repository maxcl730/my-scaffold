import codecs
import string
from datetime import datetime
import time

# prepare map from numbers to letters
_encode_table = {str(number): bytes(letter, 'ascii') for number, letter in enumerate(string.ascii_lowercase)}
# prepare inverse map
_decode_table = {ord(v): k for k, v in _encode_table.items()}


def custom_encode(text: str) -> bytes:
    # example encoder that converts ints to letters
    # see https://docs.python.org/3/library/codecs.html#codecs.Codec.encode
    return b''.join(_encode_table[x] for x in text), len(text)


def custom_decode(binary: bytes) -> str:
    # example decoder that converts letters to ints
    # see https://docs.python.org/3/library/codecs.html#codecs.Codec.decode
    return ''.join(_decode_table[x] for x in binary), len(binary)


def custom_search_function(encoding_name):
    return codecs.CodecInfo(custom_encode, custom_decode, name='Reasons')


expires = 30

def sort_and_unique_list(l, reverse=False):
    origin_list = [x for x in l]
    new_list = sorted(set(origin_list), key=origin_list.index)
    new_list.sort(reverse=reverse)
    return new_list


def generate_invitation_code(uid):
    timestamp = int(time.mktime((datetime.now().timetuple())))
    code_table = sort_and_unique_list(uid, reverse=True)
    x = len(code_table)
    b = []
    while True:
        s = timestamp // x  # 商
        y = timestamp % x  # 余数
        b = b + [y]
        if s == 0:
            break
        timestamp = s
    b.reverse()
    return uid[:8] + '-' + uid[8:16] + '-' + uid[16:] + '-' + "".join(code_table[i] for i in b)


def check_invitation_code(code):
    uid = code[0:27].replace('-', '')
    invitation_code = code[27:]
    code_table = sort_and_unique_list(uid, reverse=True)
    x = len(code_table)
    mapping = {}
    count = 0
    for letter in [x for x in code_table]:
        mapping[letter] = count
        count += 1
    count = 0
    for i in str(invitation_code)[:len(invitation_code)-1]:
        count = count + mapping[i]
        count = count * x
    timestamp = count + mapping[str(invitation_code)[len(invitation_code)-1]]
    if int(time.mktime((datetime.now().timetuple()))) > timestamp + expires:
        return False
    else:
        return True


def main():
    uid = '5c38408b6febbb0917c91e44'
    invitation_code = generate_invitation_code(uid)
    print(invitation_code)
    time.sleep(3)
    print(check_invitation_code(invitation_code))
    # register your custom codec
    # note that CodecInfo.name is used later

    codecs.register(custom_search_function)

    binary = b'abcdefg'
    # decode letters to numbers
    text = codecs.decode(binary, encoding='Reasons')
    #print(text)
    # encode numbers to letters
    binary2 = codecs.encode(text, encoding='Reasons')
    #print(binary2)
    # encode(decode(...)) should be an identity function
    assert binary == binary2


if __name__ == '__main__':
    main()

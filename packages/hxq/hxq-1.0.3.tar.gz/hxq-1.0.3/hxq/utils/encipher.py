# -*- coding: utf-8 -*-
# @Time    : 2022/7/10 20:40
# @Author  : hxq
# @Software: PyCharm
# @File    : encipher.py
# 加密类
import base64
import hashlib


def encode_bytes(data):
    if isinstance(data, str):
        return data.encode('utf-8')
    if isinstance(data, bytes):
        return data
    raise TypeError('传入类型错误')


# 加密器
class Encipher(object):
    @staticmethod
    def get_file_md5(file):
        with open(file, 'rb') as f:
            h1 = hashlib.md5()
            data = f.read(10240)
            while data:
                h1.update(data)
                data = f.read(10240)
        return h1.hexdigest()

    @staticmethod
    def get_file_base64(fp):
        with open(fp, 'rb') as f:
            return base64.b64encode(f.read())

    @staticmethod
    def md5(data):
        """
        md5加密
        """
        return hashlib.md5(encode_bytes(data)).hexdigest()

    @staticmethod
    def hash(data):
        """
        哈希加密
        """
        return hashlib.sha1(encode_bytes(data)).hexdigest()

    @staticmethod
    def base64(data):
        """
        base64编码
        """
        return base64.b64encode(encode_bytes(data)).decode('utf-8')

    @staticmethod
    def debase64(string):
        """
        base64解码
        """
        return base64.b64decode(encode_bytes(string)).decode('utf-8')


if __name__ == '__main__':
    print(Encipher.get_file_md5('encipher.py'))

# -*- coding: utf-8 -*-
# @Time    : 2022/7/10 20:42
# @Author  : hxq
# @Software: PyCharm
# @File    : common.py
import asyncio
import os
import random
import string
import sys
import pkgutil
import socket
import subprocess
from functools import wraps

from hxq.utils.decorator import except_desc, func_run_times


# 生成资源文件目录访问路径
def resource_path(relative_path=''):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = getattr(sys, '_MEIPASS')
    else:
        base_path = os.path.abspath(".")  # 获取当前工作路径,
    return os.path.join(base_path, relative_path)


def run_event_loop(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapped


@except_desc
def url2ip(url):
    socket_list = socket.getaddrinfo(url, None, 0, socket.SOCK_STREAM)
    ip_info = socket_list[0][4][0]
    print('【{}】 IP地址：{}'.format(url, ip_info))
    return ip_info


def random_password(length=12):
    """
    随机密码生成
    """
    return ''.join(random.sample(string.digits + string.ascii_letters * 1, length))


@func_run_times()
def array_subtotal(this_list):
    """
    将数组重复数据进行分类汇总，生成一个汇总字典
    """
    data = dict()
    [data.update({item: data[item] + 1}) if item in data else data.update({item: 1}) for item in this_list].clear()
    return data


def run_command(command: str) -> str:
    """
    执行cmd命令
    """
    env = os.environ.copy()
    env["LANG"] = "C"
    output, _ = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL,
                                 shell=True,
                                 env=env).communicate()
    return output.decode("gbk").rstrip("\r\n")


def get_root_path(import_name: str) -> str:
    """
    通过这个import_name确定Flask这个核心对象被创建的根目录，以获得静态文件和模板文件的目录。
    """
    mod = sys.modules.get(import_name)
    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))
    loader = pkgutil.get_loader(import_name)
    if loader is None or import_name == "__main__":
        return os.getcwd()
    if hasattr(loader, "get_filename"):
        filepath = loader.get_filename(import_name)
    else:
        __import__(import_name)
        mod = sys.modules[import_name]
        filepath = getattr(mod, "__file__", None)
        if filepath is None:
            raise RuntimeError(f'找不到{import_name}模块的根路径.')
    return os.path.dirname(os.path.abspath(filepath))


def split_str(text, keys):
    """
    文本多分组分割
    """
    return (lambda _text, _keys: (lambda x:
                                  [(x.update(text=x['text'].replace(k, _keys[0])), x['text'].split(_keys[0]))[1]
                                   for k in _keys if len(x['text'].split(k)) > 1][-1])(dict(text=_text)))(text, keys)


if __name__ == '__main__':
    content = '测试;多组,分割,123.lk'
    split_key = ['.', ',', ';']
    print(split_str(content, split_key), 'text_split 结果')
    print(sys.modules.get('subprocess').__file__)
    print(get_root_path('db'))
    # print(url2ip('z1.m1907.cn'))
    # arr = [1, 3, 5, 7, 9, 5, 1, 3, 6, 7]  # 用于在本地测试的数据，使用时需注释掉前两行
    # print(array_subtotal(arr))
    # for i in range(1, 10000):
    #     arr.append(random.randint(1, 99999))
    # print(run_command('ipconfig'))

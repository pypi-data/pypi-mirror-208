# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 10:33
# @Author  : hxq
# @Software: PyCharm
# @File    : httpx.py
from hxq.libs.httpx.http import HTTPRequest
from hxq.libs.httpx.session import SessionRequest

__all__ = [
    "http",
    "HTTP",
]
HTTP = SessionRequest
http = HTTPRequest

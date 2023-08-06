# -*- coding: utf-8 -*-
# @Time    : 2022/5/7 22:35
# @Author  : hxq
# @Software: PyCharm
# @File    : session.py
from typing import Union
from urllib.parse import urlparse

from requests import Session
from requests.structures import CaseInsensitiveDict
from requests.utils import default_headers

from hxq.libs.httpx.http import HTTPRequest, requests_catch_exception, HTTPResponse, HTTPError, iter_write_file
from hxq.libs.httpx.chrome_agent import random_version


class SessionRequest(HTTPRequest):
    """基于requests 方便日常使用的简单二次封装"""

    def __init__(self, ignore_status=True):
        """
        :param ignore_status: 是否忽略错误状态码
        """
        self.__http = Session()
        self.headers = {"User-Agent": random_version()}
        self.ignore_status = ignore_status

    def get(self, url, params=None, timeout=None, proxies=None, **kwargs) -> Union[HTTPResponse, HTTPError]:
        """
        GET请求
        """
        kwargs.setdefault('allow_redirects', True)
        r = self.request('GET', url, params=params, timeout=timeout, proxies=proxies, **kwargs)
        r.close()
        return r

    def post(self, url, data=None, timeout=None, proxies=None, **kwargs) -> Union[HTTPResponse, HTTPError]:
        """
        POST请求
        """
        r = self.request('POST', url, data=data, timeout=timeout, proxies=proxies, **kwargs)
        r.close()
        return r

    def download(self, url, file_path=None, params=None, data=None, **kwargs):
        """
        session 下载文件
        """
        return HTTPRequest.download(url, request=self.request, file_path=file_path, params=params, data=data, **kwargs)

    @requests_catch_exception
    def request(self, method, url, **kwargs):
        """
        :param method: 大小不敏感，在Session内部upper统一转化为大写
        :param url: 地址
        :param kwargs:
        :return:
        """
        # with self.__http.request(method, url, **kwargs) as r:
        results = HTTPResponse(self.__http.request(method, url, **kwargs))
        if not self.ignore_status and results.code != 200:
            return HTTPError(results.code, '请求状态错异常!')
        return results

    @property
    def cookies(self) -> dict:
        """
        读取cookies
        """
        return self.cookiejar2dict(self.__http.cookies)

    @cookies.setter
    def cookies(self, cookie: dict):
        """
        设置cookies
        """
        self.__http.cookies = self.dict2cookiejar(cookie)

    @property
    def headers(self) -> CaseInsensitiveDict:
        """
        读取当前headers
        """
        self.__http.headers.items()
        return self.__http.headers

    @headers.setter
    def headers(self, header: dict or str):
        """
        设置headers
        """
        self.__http.headers.clear()
        self.__http.headers = default_headers()
        self.add_headers(header)

    def add_headers(self, header: dict or str) -> CaseInsensitiveDict:
        """
        追加headers
        """
        if isinstance(header, str):
            header = self._raw_headers_to_dict(header)
        if isinstance(header, dict):
            return [self.__http.headers.update({k: v}) for k, v in header.items()].clear() or self.__http.headers

# -*- coding: utf-8 -*-
# @Time    : 2022/5/7 22:22
# @Author  : hxq
# @Software: PyCharm
# @File    : http.py
import importlib
import sys
import json
from functools import wraps
from typing import Union, List
from lxml import etree, html
from requests.packages import urllib3
from requests import Session, Response, exceptions
from requests.cookies import cookiejar_from_dict, RequestsCookieJar
from hxq.utils.common import run_event_loop

if sys.version_info >= (3,):
    from urllib.parse import urlencode, urlparse
    from urllib import parse
else:
    from urllib import urlencode, parse
# 关闭错误提示
urllib3.disable_warnings()


@run_event_loop
async def iter_write_file(file_path: str, r: Response):
    import aiofiles
    async with aiofiles.open(file_path, 'wb') as file:
        for chunk in r.iter_content(1024 * 10):
            await file.write(chunk)


def requests_catch_exception(func):
    """
    requests异常捕获装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Union[HTTPResponse, HTTPError]:
        try:
            return func(*args, **kwargs)
        except exceptions.HTTPError:
            return HTTPError(1000, 'HTTP错误!')
        except exceptions.SSLError:
            return HTTPError(1001, 'SSL错误!')
        except exceptions.ProxyError:
            return HTTPError(1002, '代理错误!')
        except exceptions.ConnectTimeout:
            return HTTPError(1003, '请求响应超时!')
        except exceptions.ConnectionError:
            return HTTPError(1004, '网络连接错误!')
        except exceptions.ChunkedEncodingError:
            return HTTPError(1005, 'chunked编码错误!')
        except exceptions.ContentDecodingError:
            return HTTPError(1006, '内部解码错误!')
        except Exception as e:
            return HTTPError(1007, e)

    return wrapper


class HTTPResponse:

    def __init__(self, response: Response):
        """
        :param response:http响应请求体
        """
        self.ok = True
        self.__html = None
        self.__response = response
        self.code = response.status_code
        if response.encoding and response.encoding.lower() in ['iso-8859-1', 'gb2312']:
            """
            部分页面没有编码"说明"，无法检测到编码类型,如果默认编码在常用编码类型之外将强制转化为最常见的gbk编码
            也可手动更改或使用apparent_encoding做自适应
            虽然默认编码是GB2312,但是实际上使用的是GBK编码 且 GB2312 是 GBK子集
            """
            self.encoding = 'GBK'

    def apparent_encoding(self):
        """
        应用自适应检测网页编码,会大幅度降低速度且不能做到完全匹配
        """
        self.encoding = self.__response.apparent_encoding
        if self.encoding.lower() == 'gb2312':
            self.encoding = 'GBK'
        return self.encoding

    @property
    def encoding(self):
        return self.__response.encoding

    @encoding.setter
    def encoding(self, encode):
        self.__response.encoding = encode

    @property
    def json(self) -> dict:
        if (3,) <= sys.version_info < (3, 6):
            return json.loads(self.res.content.decode(self.encoding), encoding=self.encoding)
        return self.__response.json()

    @property
    def lxml(self):
        # 按需install bs4
        """
        使用难度最低,解析速度最慢
        @return:
        """
        bs4 = importlib.import_module('bs4')
        return getattr(bs4, 'BeautifulSoup')(self.__response.text, "lxml")

    def xpath(self, *args) -> List[html.HtmlElement]:
        """
        使用难度中等，解析速度中等
        @param args:
        @return:
        """
        self.__html = self.__html if self.__html is not None else etree.HTML(self.text)
        return self.__html.xpath(*args)

    @property
    def text(self):
        return self.__response.text

    @property
    def content(self):
        return self.__response.content

    @property
    def res(self):
        return self.__response

    @property
    def cookies(self):
        return HTTPRequest.cookiejar2dict(self.__response.cookies)

    @property
    def headers(self):
        return self.__response.headers

    def xml2dict(self, xml_data=None) -> dict:
        xml_to_dict = importlib.import_module('xmltodict')
        # 按需安装
        _parse = getattr(xml_to_dict, 'parse')
        dict_xml = _parse(xml_data) if xml_data else _parse(self.text.encode("utf-8"))
        return json.loads(json.dumps(dict_xml))

    def dict2xml(self, json_str: Union[dict, str] = None):
        json_str = json_str if json_str else self.json
        if isinstance(json_str, str):
            json_str = json.loads(json_str)
        if len(json_str.keys()) > 1:
            json_str = {'root': json_str}

        xml_to_dict = importlib.import_module('xmltodict')
        _unparse = getattr(xml_to_dict, 'unparse')
        return _unparse(json_str, pretty=1)

    def close(self):
        # print('链接关闭')
        self.res.close()

    def __str__(self):
        return "{}:{}".format(self.__response, self.encoding)


class HTTPError:
    """请求错误"""

    def __init__(self, code, error_reason=None):
        """
        :param code: http状态码
        :param error_reason: http状态原因
        """
        self.ok = False
        self.code = code
        self.error_reason = error_reason

    def close(self):
        pass
        # self.res.close()

    def __str__(self):
        return "HTTP {}: {}".format(self.code, self.error_reason)


class HTTPRequest:

    @classmethod
    def get(cls, url, params=None, timeout=None, proxies=None, **kwargs) -> Union[HTTPResponse, HTTPError]:
        """
        GET请求
        """
        kwargs.setdefault('allow_redirects', True)
        r = cls.request('GET', url, params=params, timeout=timeout, proxies=proxies, **kwargs)
        r.close()
        return r

    @classmethod
    def post(cls, url, data=None, timeout=None, proxies=None, **kwargs) -> Union[HTTPResponse, HTTPError]:
        """
        POST请求
        """
        r = cls.request('POST', url, data=data, timeout=timeout, proxies=proxies, **kwargs)
        r.close()
        return r

    @classmethod
    def download(cls, url, file_path=None, params=None, data=None, **kwargs):
        """
        下载文件
        """
        kwargs['stream'] = True
        request = kwargs.pop('request', cls.request)
        r = request(kwargs.pop('method', "get").upper(), url, params=params, data=data, **kwargs)
        if not r.ok:
            return r.error_reason
        if not file_path:
            file_path = urlparse(r.res.url).path.split('/')[-1]
        iter_write_file(file_path, r.res)
        r.close()
        return True

    @staticmethod
    @requests_catch_exception
    def request(method, url, **kwargs):
        """
        :param method: 大小不敏感，在Session内部upper统一转化为大写
        :param url: 地址
        :param kwargs:
        :return:
        """

        kwargs.setdefault('ignore_status', True)
        ignore_status = kwargs.pop('ignore_status')
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 " \
             "Safari/537.36"
        kwargs.setdefault('headers', {"User-Agent": ua})
        results = HTTPResponse(Session().request(method, url, **kwargs))
        if not ignore_status and results.code != 200:
            return HTTPError(results.code, '请求状态错异常!')
        return results

    @staticmethod
    def cookiejar2dict(cookiejar: RequestsCookieJar) -> dict:
        """
        CookieJar转dict
        """
        return (lambda ck: [[ck.update({k: v}) for k, v in cookiejar.items()], ck][1])(dict())

    @staticmethod
    def dict2cookiejar(cookie_dict: dict) -> RequestsCookieJar:
        """
        dict转CookieJar
        """
        return cookiejar_from_dict(cookie_dict)

    @staticmethod
    def _raw_headers_to_dict(this_headers_str: str) -> dict:
        """
        抓包raw字符串解析为headers
        """
        # lambda
        return (lambda x: [[(lambda xx: (
            lambda items: [xx.update({items[0].strip(): ':'.join(items[1:]).strip()}), xx][1]))(x)(
            item.strip().split(':')) for item in this_headers_str.strip().split('\n') if item.strip()], x])(dict())[1]

    @staticmethod
    def dict2url(dict_params) -> str:
        """
        字典转url
        """
        return urlencode(dict_params)

    @staticmethod
    def quote(content, encoding='utf-8', **kwargs):
        """
        url编码
        """
        return parse.quote(content, encoding=encoding, **kwargs)

    @staticmethod
    def unquote(content, encoding='utf-8', **kwargs):
        """
        url解码
        """
        return parse.unquote(content, encoding=encoding, **kwargs)

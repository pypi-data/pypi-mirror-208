# -*- coding: utf-8 -*-
# @Time    : 2022/5/7 21:47
# @Author  : hxq
# @Software: PyCharm
# @File    : decorator.py
import time
from datetime import datetime
from functools import wraps


def func_run_times(length: int = 3):
    """
    函数运行耗时装饰器
    :param length:默认3位小数
    :return:
    """
    """
    # @functools.wraps(func),这是python提供的装饰器。
    # 它能把原函数的元信息拷贝到装饰器里面的 func 函数中。函数的元信息包括docstring,name,参数列表等等
    # 可以尝试去除@functools.wraps(func),你会发现"func".__name__的输出变成了inter
    # 经过装饰后实质上是得到的函数体是wrapper
    @func_run_times()
    def a():
        ...
    print(a.__name__)
    """

    def wrapper(fn):
        def print_red(string):
            print(f"\033[36m{string}\033[0m")

        @wraps(fn)
        def inter(*args, **kwargs):
            start = time.time()
            res = fn(*args, **kwargs)
            print_red("run time of the func is '%s' %.*f Ms" % (fn.__name__, length, (time.time() - start) * 1000))
            return res

        return inter

    return wrapper


# 统一的异常输出
def except_desc(func):
    @wraps(func)
    def inter(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print('=' * 30)
            print('程序出现了异常')
            print(f'----异常时间：\t{datetime.now()}\n----异常函数：\t{func.__name__}\n----异常原因：\t{e}')
            print('=' * 30)
            return e

    return inter

# -*- coding: utf-8 -*-
# @Time    : 2022/5/7 22:17
# @Author  : hertx
# @Software: PyCharm
# @File    : chrome_agent.py
import random


def random_version():
    version_list = ['85.0.4183.83', '85.0.4183.87', '86.0.4240.22', '87.0.4280.20', '87.0.4280.88',
                    '88.0.4324.96', '89.0.4389.23', '90.0.4430.24', '91.0.4472.19', '90.0.4430.212']
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} ' \
                 'Safari/537.36'
    return user_agent.format(random.choice(version_list))


if __name__ == '__main__':
    print(random_version())

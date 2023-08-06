# -*- coding: utf-8 -*-
# @Time    : 2022/4/5 12:51
# @Author  : hxq
# @Software: PyCharm
# @File    : __init__.py.py
import os
import importlib
import getpass

winshell = importlib.import_module("winshell")


class Client:
    def __init__(self):
        ...

    @property
    def desktop(self):
        """
        桌面路径
        """
        return getattr(winshell, 'desktop')()

    @property
    def username(self):
        """
        系统用户名
        """
        return getpass.getuser()

    @staticmethod
    def start_file(path):
        """
        启动文件/应用
        """
        os.startfile(path)

    @property
    def startup_path(self) -> str:
        """
        自启动目录
        """
        startup_path = r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
        return os.path.join(os.getenv("SystemDrive"), r"\users", self.username, startup_path)

    @staticmethod
    def create_shortcut(exe_path: str, shortcut_name: str, desc: str):
        """
        生成快捷方式
        :param exe_path: exe路径
        :param shortcut_name: 需要创建快捷方式的路径
        :param desc: 描述，鼠标放在图标上面会有提示
        :return:
        """
        if not shortcut_name.endswith('.lnk'):
            shortcut_name = shortcut_name + ".lnk"
        try:
            getattr(winshell, 'CreateShortcut')(
                Path=shortcut_name,
                Target=exe_path,
                Icon=(exe_path, 0),
                Description=desc
            )
            return True
        except ImportError as err:
            print("'winshell' lib may not available on current os")
            print("error detail %s" % str(err))
        return False

    def create_startup(self, exe_path: str, lnk_name: str, desc: str):
        return self.create_shortcut(exe_path, os.path.join(self.startup_path, lnk_name), desc)

# -*- coding: utf-8 -*-
# @Time    : 2022/6/9 22:03
# @Author  : hxq
# @Software: PyCharm
# @File    : 多线程.py
# -*- coding: utf-8 -*-
import ctypes
import inspect
import threading
from threading import Thread, Timer, enumerate, Event, RLock


# 定时器(每N秒执行一次)
class TimerAlways(object):
    def __init__(self, func, time=1.0, daemon=True, *args, **kwargs):
        self.func = func
        self.time = time
        self.daemon = daemon
        self.args = args
        self.kwargs = kwargs
        self.__timer = None

    # 开启
    def start(self):
        print('{} 秒后开始执行'.format(self.time))
        self.__set_wall_timer()

    # 定时等待循环执行任务
    def __set_wall_timer(self):
        self.func(*self.args, **self.kwargs)
        self.__timer = Timer(self.time, self.__set_wall_timer)
        self.__timer.setDaemon(self.daemon)
        self.__timer.start()

    # def start_timer(self, seconds, callback):
    #     def timer():
    #         threading.Timer(seconds, timer).start()
    #         callback()
    #
    #     timer()
    # 终止定时
    def exit(self):
        self.__timer.cancel()


# 多线程操作
class ThreadX(Thread):
    lock = RLock()

    def __init__(self, func: callable, *args, **kwargs):
        daemon = kwargs.pop("daemon", False)
        super().__init__(target=func, args=args, kwargs=kwargs, name=func.__name__)
        self.setDaemon(daemon)
        self.start()
        self.__flag = Event()  # 用于暂停线程的标识

    def pause(self):
        """
        线程阻塞
        """
        self.__flag.clear()

    def resume(self):
        """
        阻塞
        """
        self.__flag.set()

    def stop_thread(self):
        """
        终止线程
        """
        if self.ident:
            self._async_raise(self.ident, SystemExit)

    @classmethod
    def show_time(cls):
        """
        显示当前线程数量
        """
        length = len(enumerate())  # 枚举返回个列表
        print('当前运行的线程数为：%d' % length)
        # 当发现子线程没结束时，会增加一个线程，如果让在线程最后，那么就不会新增一个线程
        timer = Timer(3, cls.show_time)
        timer.setDaemon(True)
        timer.start()

    @staticmethod
    def _async_raise(tid, exctype):
        """引发异常，如果需要，执行清理"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            # 触发异常
            raise ValueError("无效的线程ID")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, target, args=()):
        thread = threading.Thread(target=target, args=args)
        self.threads.append(thread)
        thread.start()

    def wait_for_threads(self):
        for thread in self.threads:
            thread.join()

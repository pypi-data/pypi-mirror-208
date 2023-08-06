# -*- coding: utf-8 -*-
# @Time    : 2022/12/6 23:18
# @Author  : hxq
# @Software: PyCharm
# @File    : __init__.py
import contextlib
import re
import json
import datetime
import importlib
from typing import Union
from json import JSONEncoder
from dbutils.pooled_db import PooledDB, PooledDedicatedDBConnection


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat(sep=" ")
        return super().default(obj)


class DBHelper:
    """简单的数据库连接池助手"""

    def __init__(self, config):
        self.config = self.import_config(config)
        self.pool = None
        sql_conns = {
            'MySQL': 'pymysql',
            'SQLServer': 'pymssql'
        }
        """
        初始化连接池
        """
        database = importlib.import_module(sql_conns.get(self.config.setdefault('SQL_CREATOR', 'MySQL')))
        self.pool = PooledDB(
            creator=database,
            maxconnections=self.config.setdefault('SQL_MAX_CONNECT', 16),
            mincached=self.config.setdefault('SQL_MIN_CACHED', 1),
            blocking=self.config.setdefault('SQL_BLOCKING', True),
            ping=self.config.setdefault('SQL_PING', 0),
            host=self.config.setdefault('SQL_HOST', '127.0.0.1'),
            port=self.config.setdefault('SQL_PORT', 3306),
            user=self.config.setdefault('SQL_USER', 'root'),
            password=self.config.setdefault('SQL_PASSWORD', 'key123123'),
            database=self.config.setdefault('SQL_DATABASE', None),
            charset=self.config.setdefault('SQL_CHARSET', 'utf8mb4')
        )

    """导入配置"""

    @staticmethod
    def import_config(obj) -> dict:
        """
        导入字典or类对象中的配置信息
        """
        config = dict()
        if isinstance(obj, dict):
            [config.update({k.upper(): v}) for k, v in obj.items()]
        elif hasattr(obj, '__dict__'):
            [config.update({k: getattr(obj, k)}) if k.isupper() else '' for k in dir(obj)]
        else:
            raise ValueError('请导入正确的config对象!')
        return config

    """列表类型转字典"""

    @staticmethod
    def _tuple2dict(results, cursor) -> dict:
        result = [dict(zip([desc[0] for desc in cursor.description], item)) for item in results]
        return json.loads(DateTimeEncoder().encode(result))

    """执行增删改查sql语句"""

    def execute(self, sql_statement: str) -> Union[dict, int]:
        with self.connect() as conn:
            cursor = conn.cursor()
            row_count = cursor.execute(sql_statement)
            # 匹配对大小写不敏感
            if re.search(r"SELECT", sql_statement, re.I):
                result = cursor.fetchall()
                return self._tuple2dict(result, cursor)

            cursor.connection.commit()
            return row_count if row_count else 0

    """查询一条数据"""

    def first(self, sql_statement) -> dict:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_statement)
            result = cursor.fetchone()

        return self._tuple2dict([result], cursor)

    """查询所有数据"""

    def all(self, sql_statement) -> dict:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_statement)
            result = cursor.fetchall()

        return self._tuple2dict(result, cursor)

    """创建连接"""

    @contextlib.contextmanager
    def connect(self) -> PooledDedicatedDBConnection:
        conn = self.pool.connection()  # 创建连接
        yield conn  # 游标
        self.close(conn)

    """关闭连接"""

    @staticmethod
    def close(conn):
        conn.cursor().close()
        conn.close()

    # def __enter__(self):
    #     """
    #     # 实现with obj as f 主动从连接池中拿连接对象 并存放至线程堆中
    #     """
    #     conn, cursor = self.connect()
    #     return cursor
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     """
    #     # 实现with 结束 从线程堆中获取链接对象，并回收连接至连接池
    #     """
    #     print(exc_type, exc_val, exc_tb)

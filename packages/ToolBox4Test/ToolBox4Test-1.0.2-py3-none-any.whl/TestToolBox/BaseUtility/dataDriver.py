#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2021/12/6 16:19
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : dataDriver.py
@Describe  : 数据库连接
————————————————————
@Version   : 0.1 
"""
# update   : 2021/12/6
# 1. 
# 2. 
# ————————————————————
# update   : 
# 1. 
# 2. 
# ————————————————————

import pymysql
import redis
from loguru import logger


def getRedis():
    # 单实例连接redis
    # r = redis.Redis(host='.com', port=6379, password="", db=35, decode_responses=True)

    # 连接池 多实例共享
    pool = redis.ConnectionPool(host="", port=6379, password="", db=35, decode_responses=True)
    _redis = redis.Redis(connection_pool=pool)
    return _redis


def redisDemo():
    r = getRedis()
    # r.set('name', 'runoob')  # 设置 name 对应的值
    print(r.get('SMOOTH:35522'))  # 取出键 name 对应的值
    print(r.keys('SMOOTH:*:35543'))  # 取出键 name 对应的值

    print(r.keys('SMOOTH*35540'))  # 取出键 name 对应的值
    for key in r.keys('SMOOTH*35543'):
        print(r.type(key))  # 查看类型
        if r.type(key) == "string":
            print(key, r.get(key))

    # print(r.keys())     # 查询所有的Key
    # print(r.dbsize())   # 当前redis包含多少条数据
    # print(r.randomkey())    # 随机获取一个redis的name（不删除）


# 缓存 Redis
class FRedis:
    def __init__(self, dbNo):
        self.db = dbNo
        self.connect = self._connect(dbNo)
        
    def _connect(self, dbNo=0):
        # 连接池 多实例共享
        pool = redis.ConnectionPool(
            host="", port=6379,
            password="", db=dbNo, decode_responses=True)
        _redis = redis.Redis(connection_pool=pool)
        return _redis
    
    def getOne(self, target):
        return self.connect.get(target)
    
    def getAll(self, target):
        return self.connect.keys(target)
    
    # def setOne(self, key, value):
    #     con = self._connet()
    #     con.sadd(key, value)      # hset
    #     return con.scard(key)   # 返回总数量

    # def set(self):
    #     return self.connect


# 数据库 DB
class FDB:
    def __init__(self, dbName, env="QA"):
        self.DB = dbName
        self.env = env

    def _connect(self):
        if self.env == "QA":
            return self._connect_QA()
        if self.env == "DEV":
            return self._connect_DEV()

    def _connect_QA(self):
        sqlConnect = pymysql.connect(  # 连接数据库服务器
            user="",
            password="",
            host="",  # IP地址
            port=3306,
            database=self.DB,
            # database="smooth",
            charset="utf8"
        )
        return sqlConnect

    def _connect_DEV(self):
        sqlConnect = pymysql.connect(  # 连接数据库服务器
            user="",
            password="",
            host="",  # IP地址
            port=3306,
            database=self.DB,
            # database="smooth",
            charset="utf8"
        )
        return sqlConnect

    # 数据库游标
    @staticmethod
    def _cursor(connect):
        # _cursor = sqlConnect.cursor()  # 创建操作游标 - 列表结果
        _cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)  # 字典结果
        return _cursor  # sqlConnect

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self._cursor().close()
        self._connect().close()
        del self

    # execute 一次执行提交
    def _execute(self, SQL):
        db = self._connect()
        cursor = db.cursor()  # 创建操作游标 - 列表结果
        try:
            logger.debug(f"SQL 执行：\n{SQL}")
            result = cursor.execute(SQL)
            # result = cursor.fetchall()
            lastId = cursor.lastrowid
            # # 如果插入多条数据，cursor.lastrowid 显示的是最后一条的ID
            db.commit()
            logger.debug(f"Done! 执行数：{result}，操作数据起始id：{lastId}")
        except Exception as err:
            logger.error(f"SQL 执行异常：{err}")
            db.rollback()
        db.close()

    # executemany 批量执行提交
    def _executeAll(self, SQL, value_list):
        db = self._connect()
        cursor = db.cursor()  # 创建操作游标 - 列表结果
        try:
            logger.debug(f"SQL 批量执行：\n{SQL}\n\n{value_list}")
            result = cursor.executemany(SQL, value_list)
            # result = cursor.fetchall()
            lastId = cursor.lastrowid
            db.commit()
            logger.debug(f"Done! 执行总数：{result}， 操作数据起始id：{lastId}")
        except Exception as err:
            logger.error(f"SQL 执行异常：{err}")
            db.rollback()
        db.close()

    # 单条数据 - 查询
    def fetchone(self, SQL):
        db = self._connect()
        cursor = self._cursor(db)
        result = None
        try:
            cursor.execute(SQL)
            result = cursor.fetchone()
        # results = cursor.fetchall()
        except Exception as err:
            logger.error(f"SQL 执行异常：{err}")
            db.rollback()
        cursor.close()
        logger.debug(f"SQL 查询结果：{SQL}\n{result}")
        # 返回列表数据
        # return list(result) if result else None
        return result if result else None

    # 多条数据 - 查询
    def fetchall(self, SQL):
        db = self._connect()
        cursor = self._cursor(db)
        result = None
        try:
            cursor.execute(SQL)
            result = cursor.fetchall()
        except Exception as err:
            logger.error(f"SQL 执行异常：{err}")
            db.rollback()
        cursor.close()
        logger.debug(f"SQL 查询结果：{SQL}\n{result}")
    
        return result

    def Desc(self, table):
        # SQL = f"""
        # SELECT
        #     '字段名' = CONVERT (VARCHAR(100), a.name),
        #     '表名' = CONVERT (VARCHAR(50), d.name),
        #     '类型' = CONVERT (VARCHAR(50), b.name),
        #     '库名' = {table},
        #     '字段说明' = CONVERT (
        #         VARCHAR (50), isnull(g.[value], '')
        #     )
        # FROM
        #     dbo.syscolumns a
        # LEFT JOIN dbo.systypes b ON a.xusertype = b.xusertype
        # INNER JOIN dbo.sysobjects d ON a.id = d.id
        # AND d.xtype = 'U'
        # AND d.name <> 'dtproperties'
        # LEFT JOIN dbo.syscomments e ON a.cdefault = e.id
        # LEFT JOIN sys.extended_properties g ON a.id = g.major_id
        # AND a.colid = g.minor_id
        # LEFT JOIN sys.extended_properties f ON d.id = f.major_id
        # AND f.minor_id = 0
        # WHERE
        #     d.name = 'DOC_ORDERS'
        # """
        SQL = f"DESC {table}"
        cursor = self._cursor()
        cursor.execute(SQL)
        # result = cursor.fetchone()
        result = cursor.fetchall()
        cursor.close()
        fields = [field.get("Field") for field in result]
        logger.debug(f"查询结果：{SQL}\n{fields}")

    # 自定义 获取表格最新数据
    def getAll(self, table, fields="*", clause="True", order="DESC", limit=10):
        SQL = f"""
        SELECT {fields}
        FROM {table}
        WHERE {clause}
        ORDER BY id {order}
        LIMIT {limit}
        """
        result = self.fetchall(SQL)
        return result

    # 自定义 - 搜索
    def getOne(self, table, fields="*", clause="True"):
        SQL = f"""
        SELECT {fields}
        FROM {table}
        WHERE {clause}
        ORDER BY id DESC
        LIMIT 1
        """
        result = self.fetchone(SQL)
        return result
    
    def join(self, tables, fields="*", on="True", clause="True", order="DESC", limit=10):
        SQL = f"""
        SELECT {fields}
        FROM {tables} ON {on}
        WHERE {clause}
        ORDER BY A.id {order}
        LIMIT {limit}
        """
        result = self.fetchall(SQL)
        return result

    # insert
    def insert(self, table, fields="", values=""):
        SQL = f"""
        INSERT INTO {table} {fields}
        VALUES ({values})
        """
        if not values:
            logger.error(f"SQL 执行插入数据列表不能为空！\n{SQL}")
            return
        self._execute(SQL)

    # insert
    def insertAll(self, table, fields="", value_list=None):
        if not value_list:
            logger.error(f"SQL 执行插入数据列表不能为空！")
            return
        placeholder = "%s"
        for i in range(len(value_list[0]) - 1):
            placeholder += ",%s"
        SQL = f"""
        INSERT INTO {table} {fields}
        VALUES ({placeholder})
        """
        # logger.debug(f"SQL 执行插入操作：\n{SQL}")
        self._executeAll(SQL, value_list)


if __name__ == '__main__':
    pass

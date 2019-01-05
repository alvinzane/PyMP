#!/usr/bin/env python# coding=utf-8import loggingimport randomimport tracebackimport osimport pymysqlimport logging.handlersimport sysfrom pymysql import OperationalError, InternalErrorfrom py_mysql_server.lib.log import init_loggerclass PyProxy:    def __init__(self, connection_settings=None, logger=None):        self.connection = None        self.logger = logger if logger else init_logger()        if not connection_settings:            connection_settings = {                'host': "192.168.1.100",                'port': 3306,                'user': "admin",                'password': "aaaaaa",                'charset': "utf8mb4",                'db': "production"            }        self.conn_setting = connection_settings        self.connect()    def __del__(self):        self.disconnect()    def set_logger(self, val):        self.logger = val    def connect(self):        if not self.connection:            try:                self.connection = pymysql.connect(                    host=self.conn_setting["host"],                    port=self.conn_setting["port"],                    user=self.conn_setting["user"],                    password=self.conn_setting["password"],                    db=self.conn_setting["db"],                    charset=self.conn_setting["charset"],                    cursorclass=pymysql.cursors.DictCursor                )            except OperationalError as oe:                self.logger.error("MySQL Operational Error:")                print(oe)            except InternalError as ie:                self.logger.error("MySQL Internal Error:")                print(ie)        return self.connection    def disconnect(self):        if self.connection:            self.connection.close()    def query2one(self, sql, para=None):        with self.connect() as cursor:            cursor.execute(sql, para)            return cursor.fetchone()    def query2list(self, sql, para=None):        with self.connect() as cursor:            cursor.execute(sql, para)            return cursor.fetchall()    def insert(self, sql, para=None, auto_inc=True):        conn = self.connect()        conn.autocommit(False)        conn.begin()        with conn.cursor() as cursor:            result = cursor.execute(sql, para)            if auto_inc:                result = cursor.lastrowid            conn.commit()        return result    def batch_execute(self, sql_list=None):        if sql_list is None:            return False        conn = self.connect()        conn.autocommit(False)        conn.begin()        try:            with conn.cursor() as cursor:                for sql in sql_list:                    cursor.execute(sql)                conn.commit()                opt_success = True        except:            self.logger.error(traceback.format_exc())            conn.rollback()            opt_success = False        return opt_success    def trx_begin(self):        conn = self.connect()        conn.autocommit(False)        conn.begin()        return conn    def trx_end(self):        conn = self.connect()        conn.commit()        return conn
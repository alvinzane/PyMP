import re

from py_mysql_server.lib.py_proxy import PyProxy


mysql = PyProxy(connection_settings={
    'host': "192.168.1.100",
    'port': 6066,
    'user': "admin",
    'password': "myguard",
    'charset': "utf8mb4",
    'db': "production"
})

db = mysql.query2list("show databases")
print(db)

db = mysql.query2list("select user from mysql.user")
print(db)

db = mysql.query2list("show tables from db_dba")
print(db)

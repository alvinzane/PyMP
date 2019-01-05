import re

from py_mysql_server.lib.py_proxy import PyProxy


mysql = PyProxy(connection_settings={
    'host': "192.168.1.100",
    'port': 3306,
    'user': "admin",
    'password': "aaaaaa",
    'charset': "utf8mb4",
    'db': "db_dba"
})

db = mysql.query2list("CALL multi()")
print(db)


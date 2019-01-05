import os

from mysql_proto.packet import dump_my_packet
from py_mysql_server.lib.packet import file2packet

file_name = "select_2"
file_name = "show_databases"
# file_name = "select__from_dbdbat2_where_id1"
# file_name = "auth_result.cap"
# file_name = "auth_failed.cap"
cap_files = [name for name in os.listdir('/tmp') if name.startswith(file_name)]
for _file in cap_files:
    buff = file2packet(_file)
    print("[%s]:" % (_file,))
    dump_my_packet(buff)

import socket

import os
from pprint import pprint

from mysql_proto.packet import dump_my_packet, send_client_socket, file2packet, getSequenceId, getType
from py_mysql_server.auth.challenge import Challenge
from py_mysql_server.auth.response import Response
from py_mysql_server.com.query import Query
from py_mysql_server.guard_server import scramble_native_password
from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import read_server_packet

HOST = '192.168.1.100'
PORT = 3306
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

packet = read_server_packet(s)
print("received 1:")
dump_my_packet(packet)

challenge = Challenge.loadFromPacket(packet)

password = "aaaaaa"
challenge1 = challenge.challenge1
challenge2 = challenge.challenge2

scramble_password = scramble_native_password(password, challenge1 + challenge2)
# packet = file2packet("auth_reply.cap")
# response = Response.loadFromPacket(packet)
response = Response()
response.sequenceId = 1
response.capabilityFlags = 33531397
response.characterSet = 33
response.maxPacketSize = 16777216
response.clientAttributes["_client_name"] = 'pymysql'
response.clientAttributes["_pid"] = str(os.getpid())
response.clientAttributes["_client_version"] = '5.6'
response.clientAttributes["program_name"] = 'mysql'
response.pluginName = 'mysql_native_password'
response.username = "admin"
response.schema = "mysql"
response.authResponse = scramble_password
response.removeCapabilityFlag(Flags.CLIENT_COMPRESS)
response.removeCapabilityFlag(Flags.CLIENT_SSL)
response.removeCapabilityFlag(Flags.CLIENT_LOCAL_FILES)

packet = response.toPacket()
print("login 1:")
dump_my_packet(packet)

send_client_socket(s, packet)

packet = read_server_packet(s)
print("received 2:")
dump_my_packet(packet)

sql = Query()
sql.sequenceId = 0
sql.query = "select user,host from mysql.user"
packet = sql.toPacket()

print("query 1:")
dump_my_packet(packet)

send_client_socket(s, packet)

while True:
    packet = read_server_packet(s)
    sequenceId = getSequenceId(packet)
    print("received query [%s]:" % (sequenceId,))
    dump_my_packet(packet)
    packetType = getType(packet)

    if packetType == Flags.EOF or packetType == Flags.ERR:
        break

sql = Query()
sql.sequenceId = 0
sql.query = "select user,host from mysql.user limit 1"
packet = sql.toPacket()

print("query 2:")
dump_my_packet(packet)

send_client_socket(s, packet)

while True:
    packet = read_server_packet(s)
    sequenceId = getSequenceId(packet)
    print("received query [%s]:" % (sequenceId,))
    dump_my_packet(packet)
    packetType = getType(packet)

    if packetType == Flags.EOF or packetType == Flags.ERR:
        break

s.close()

import socket

import os
from pprint import pprint

from mysql_proto.packet import dump_my_packet, send_client_socket, file2packet, getSequenceId, getType
from py_mysql_server.auth.challenge import Challenge
from py_mysql_server.auth.response import Response
from py_mysql_server.com.initdb import Initdb
from py_mysql_server.com.query import Query
from py_mysql_server.guard_server import scramble_native_password
from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import read_server_packet


def get_socket(host='192.168.1.100', port=3306, user="", password="", schema=""):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    packet = read_server_packet(s)
    print("received 1:")
    dump_my_packet(packet)

    challenge = Challenge.loadFromPacket(packet)

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
    response.username = user
    response.schema = schema
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

    return s


def read_packet(skt):
    while True:
        packet = read_server_packet(skt)
        sequenceId = getSequenceId(packet)
        print("read packet [%s]:" % (sequenceId,))
        dump_my_packet(packet)
        packetType = getType(packet)

        if packetType == Flags.EOF or packetType == Flags.ERR or packetType == Flags.OK:
            break


def send_socket(skt, buff):
    print("send packet:")
    dump_my_packet(buff)
    skt.sendall(buff)


if __name__ == "__main__":
    s = get_socket(host="192.168.1.100", user="admin", password="aaaaaa", schema="mysql")
    sql = Query()
    sql.sequenceId = 0
    sql.query = "select * from t2"
    packet = sql.toPacket()

    print("query 1:")
    dump_my_packet(packet)
    send_socket(s, packet)
    read_packet(s)

    sql = Initdb()
    sql.sequenceId = 0
    sql.schema = "db_dba"
    packet = sql.toPacket()

    print("Initdb:")
    dump_my_packet(packet)
    send_socket(s, packet)
    read_packet(s)

    sql = Query()
    sql.sequenceId = 0
    sql.query = "select * from t2"
    packet = sql.toPacket()

    print("query 2:")
    dump_my_packet(packet)
    send_socket(s, packet)
    read_packet(s)

    s.close()

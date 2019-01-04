# coding=utf-8
import hashlib
import re
import struct
from functools import partial
from hashlib import sha1
import logging
import threading
import SocketServer
import sys

import os

from py_mysql_server.auth.challenge import Challenge
from py_mysql_server.auth.response import Response
from py_mysql_server.com.initdb import Initdb
from py_mysql_server.com.query import Query
from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import read_client_packet, send_client_socket, getType, dump
from py_mysql_server.lib.packet import file2packet
from py_mysql_server.lib.py_proxy import PyProxy
from py_mysql_server.lib.py_upstream import PyUpstream

SCRAMBLE_LENGTH = 20
PY2 = sys.version_info[0] == 2
sha1_new = partial(hashlib.new, 'sha1')


def scramble_native_password(password, message):
    """Scramble used for mysql_native_password"""
    if not password:
        return b''

    stage1 = sha1_new(password).digest()
    stage2 = sha1_new(stage1).digest()
    s = sha1_new()
    s.update(message[:SCRAMBLE_LENGTH])
    s.update(stage2)
    result = s.digest()
    return _my_crypt(result, stage1)


def _my_crypt(message1, message2):
    result = bytearray(message1)
    if PY2:
        message2 = bytearray(message2)

    for i in range(len(result)):
        result[i] ^= message2[i]

    return bytes(result)


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    timeout = 5
    proxies = dict()
    upstreams = dict()
    logger = logging.getLogger('server')

    def setup(self):
        self.proxies["main"] = PyProxy(logger=logger)
        self.upstreams["main"] = PyUpstream(logger=logger)
        pass

    def handle(self):

        # 认证
        challenge1 = '12345678'
        challenge2 = '123456789012'
        challenge = self.create_challenge(challenge1, challenge2)
        send_client_socket(self.request, challenge.toPacket())

        packet = read_client_packet(self.request)
        response = Response()
        response = response.loadFromPacket(packet)

        username = response.username
        self.logger.info("login user:" + username)

        sql_user_password = "select user_password from mysql_users where user_name = %s"
        result = self.proxies["main"].query2one(sql_user_password, (username,))
        password = result["user_password"]

        # 验证密码
        native_password = scramble_native_password(password, challenge1 + challenge2)
        if response.authResponse != native_password:
            buff = file2packet("auth_failed.cap")
            send_client_socket(self.request, buff)
            self.finish()

        buff = file2packet("auth_result.cap")
        send_client_socket(self.request, buff)

        # 查询
        while True:

            packet = read_client_packet(self.request)
            packet_type = getType(packet)

            if packet_type == Flags.COM_QUIT:
                self.finish()
            elif packet_type == Flags.COM_INIT_DB:
                schema = Initdb.loadFromPacket(packet).schema
            elif packet_type == Flags.COM_QUERY:
                self.handle_query(packet)
            elif packet_type == Flags.COM_FIELD_LIST:
                pass

    @staticmethod
    def create_challenge(challenge1, challenge2):
        # 认证
        challenge = Challenge()
        challenge.protocolVersion = 10
        challenge.serverVersion = '5.7.20-log'
        challenge.connectionId = 83
        challenge.challenge1 = challenge1
        challenge.challenge2 = challenge2
        challenge.capabilityFlags = 4160717151
        challenge.characterSet = 224
        challenge.statusFlags = 2
        challenge.authPluginDataLength = 21
        challenge.authPluginName = 'mysql_native_password'
        challenge.sequenceId = 0
        return challenge

    def handle_query(self, packet):
        query = Query.loadFromPacket(packet).query
        self.logger.info("query: " + query)
        file_name = re.sub(r'[^a-zA-Z\s\d]', '', query)
        file_name = re.sub(r'\s', '_', file_name)

        tmp_dir = "/tmp"
        if os.path.isfile(tmp_dir + "/" + file_name + "_0.cap"):

            cap_files = [name for name in os.listdir('/tmp') if name.startswith(file_name)]
            for _file in cap_files:
                buff = file2packet(_file)
                print("[%s] send_client_socket:" % (_file,))
                send_client_socket(self.request, buff)
            return

        upstream = self.upstreams["main"]
        upstream.sendall(packet)
        buff_list = upstream.read_query_result()
        response = bytearray()
        for i, buff in enumerate(buff_list):
            buff[3] = i + 1
            logger.debug("send_client_socket [%s]:" % (i, ))
            send_client_socket(self.request, buff)
            # response.extend(buff)
        # send_client_socket(self.request, response)
        pass


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 6069

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    FORMAT = "%(asctime)s %(message)s"
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    server_thread.start()
    logger.info("Server loop running in thread: %s %s %s" % (server_thread.name, HOST, PORT))
    # server.shutdown()
    # server.server_close()

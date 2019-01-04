# coding=utf-8
import hashlib
import struct
from functools import partial
from hashlib import sha1
import logging
import threading
import SocketServer
import sys

from py_mysql_server.auth.challenge import Challenge
from py_mysql_server.auth.response import Response
from py_mysql_server.com.initdb import Initdb
from py_mysql_server.com.query import Query
from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import read_client_packet, send_client_socket, getType, dump
from py_mysql_server.lib.packet import file2packet
from py_mysql_server.lib.py_proxy import PyProxy

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
    logger = logging.getLogger('server')

    def setup(self):
        pass

    def handle(self):

        # 认证
        challenge1 = '12345678'
        challenge2 = '123456789012'
        password = 'aaaaaa'
        challenge = self.create_challenge(challenge1, challenge2)
        send_client_socket(self.request, challenge.toPacket())

        packet = read_client_packet(self.request)
        response = Response()
        response = response.loadFromPacket(packet)

        username = response.username
        self.logger.info("login user:" + username)

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
                query = Query.loadFromPacket(packet).query
                self.logger.info("query: " + query)
            elif packet_type == Flags.COM_FIELD_LIST:
                pass

            self.logger.debug("query_result:")
            buff = file2packet("query_result_1.cap")
            send_client_socket(self.request, buff)

            buff = file2packet("query_result_2.cap")
            send_client_socket(self.request, buff)

            buff = file2packet("query_result_3.cap")
            send_client_socket(self.request, buff)

            buff = file2packet("query_result_4.cap")
            send_client_socket(self.request, buff)

    def create_challenge(self, challenge1, challenge2):
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


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 6066

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

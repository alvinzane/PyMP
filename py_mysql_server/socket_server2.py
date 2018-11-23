# coding=utf-8
import logging
import threading
import SocketServer

from py_mysql_server.auth.challenge import Challenge
from py_mysql_server.com.initdb import Initdb
from py_mysql_server.com.query import Query
from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import read_client_packet, send_client_socket, getType, dump
from py_mysql_server.lib.packet import file2packet


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    timeout = 5
    logger = logging.getLogger('server')

    def setup(self):
       pass

    def handle(self):

        # 认证
        challenge = Challenge()
        challenge.protocolVersion = 10
        challenge.serverVersion = '5.7.20-log'
        challenge.connectionId = 83
        challenge.challenge1 = '(&^4R=2>'
        challenge.challenge2 = 'aaaaaaaa'
        challenge.capabilityFlags = Flags.CLIENT_PROTOCOL_41
        challenge.characterSet = 224
        challenge.statusFlags = 2
        challenge.authPluginDataLength = 21
        challenge.authPluginName = 'mysql_native_password'
        challenge.sequenceId = 0

        cbuff = challenge.toPacket()
        buff = file2packet("handshake.cap")

        challenge2 = Challenge()
        challenge2 = challenge2.loadFromPacket(buff)

        dump(challenge.toPacket())
        dump(challenge2.toPacket())

        send_client_socket(self.request, buff)

        # todo 验证密码
        read_client_packet(self.request)
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

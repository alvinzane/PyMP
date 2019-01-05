# coding=utf-8
import SocketServer
import logging
import threading

from pymysql._auth import scramble_native_password

from py_mysql_server.auth.challenge import Challenge
from py_mysql_server.auth.response import Response
from py_mysql_server.com.initdb import Initdb
from py_mysql_server.com.query import Query
from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import file2packet
from py_mysql_server.lib.packet import read_client_packet, send_client_socket, getType
from py_mysql_server.lib.py_proxy import PyProxy
from py_mysql_server.lib.py_upstream import PyUpstream

connection_counter = 0
logger = None


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    connection_id = 0
    timeout = 5
    proxies = dict()
    upstreams = dict()
    user_id = 0
    logger = logging.getLogger('server')

    def setup(self):
        global connection_counter
        connection_counter += 1
        self.connection_id = connection_counter
        self.proxies["main"] = PyProxy(logger=logger)
        self.upstreams["main"] = PyUpstream(logger=logger)
        pass

    def handle(self):

        # 认证
        challenge1 = '12345678'
        challenge2 = '123456789012'
        challenge = self.create_challenge(challenge1, challenge2, self.connection_id)
        send_client_socket(self.request, challenge.toPacket())

        packet = read_client_packet(self.request)
        response = Response()
        response = response.loadFromPacket(packet)

        username = response.username
        self.logger.info("login user:" + username)

        sql_user_password = "select user_id, user_password from mysql_users where user_name = %s"
        result = self.proxies["main"].query2one(sql_user_password, (username,))
        password = result["user_password"]
        self.user_id = result["user_id"]

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
                self.logger.info("use " + schema)
                self.dispatch_packet(packet)

            elif packet_type == Flags.COM_QUERY:
                self.handle_query(packet)
            elif packet_type == Flags.COM_FIELD_LIST:
                self.dispatch_packet(packet)

    @staticmethod
    def create_challenge(challenge1, challenge2, connection_id):
        # 认证
        challenge = Challenge()
        challenge.protocolVersion = 10
        challenge.serverVersion = '5.7.20-log'
        challenge.connectionId = connection_id
        challenge.challenge1 = challenge1
        challenge.challenge2 = challenge2
        challenge.capabilityFlags = 4160717151
        challenge.characterSet = 224
        challenge.statusFlags = 2
        challenge.authPluginDataLength = 21
        challenge.authPluginName = 'mysql_native_password'
        challenge.sequenceId = 0
        return challenge

    def dispatch_packet(self, packet):
        upstream = self.upstreams["main"]
        upstream.sendall(packet)
        buff_list = upstream.read_query_result()
        for buff in buff_list:
            send_client_socket(self.request, buff)

    def handle_query(self, packet):
        query = Query.loadFromPacket(packet).query
        self.logger.info("query: " + query)
        sql_add_com_history = "insert into com_history set user_id = %s,command_text= %s"
        self.proxies["main"].insert(sql_add_com_history, (self.user_id, query))
        # file_name = re.sub(r'[^a-zA-Z\s\d]', '', query)
        # file_name = re.sub(r'\s', '_', file_name)

        # tmp_dir = "/tmp"
        # if os.path.isfile(tmp_dir + "/" + file_name + "_0.cap"):
        #
        #     cap_files = [name for name in os.listdir('/tmp') if name.startswith(file_name)]
        #     for _file in cap_files:
        #         buff = file2packet(_file)
        #         print("[%s] send_client_socket:" % (_file,))
        #         send_client_socket(self.request, buff)
        #     return

        upstream = self.upstreams["main"]
        upstream.sendall(packet)
        buff_list = upstream.read_query_result()
        for i, buff in enumerate(buff_list):
            logger.debug("send_client_socket [%s]:" % (i, ))
            send_client_socket(self.request, buff)
        pass


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def main():
    global logger
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 6067

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    FORMAT = "%(asctime)s %(message)s"
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    server_thread = threading.Thread(target=server.serve_forever)

    server_thread.start()
    logger.info("Server loop running in thread: %s %s %s" % (server_thread.name, HOST, PORT))


if __name__ == "__main__":
    main()

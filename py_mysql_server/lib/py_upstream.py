#!/usr/bin/env python# coding=utf-8import pymysqlfrom pymysql import OperationalError, InternalErrorfrom mysql_proto.packet import getSize, getSequenceId, getTypefrom py_mysql_server.lib import Flagsfrom py_mysql_server.lib.log import init_loggerfrom py_mysql_server.lib.packet import dumpclass PyUpstream:    def __init__(self, connection_settings=None, logger=None):        self.serverSocket = None        self.connection = None        self.logger = logger if logger else init_logger()        if not connection_settings:            connection_settings = {                'host': "192.168.1.100",                'port': 3306,                'user': "admin",                'password': "aaaaaa",                'charset': "utf8mb4",                'db': "production"            }        self.conn_setting = connection_settings        self.connect()    def __del__(self):        self.disconnect()    def sendall(self, buff):        self.serverSocket.sendall(buff)        if __debug__:            self.logger.debug("send_server_socket:")            dump(buff)    def connect(self):        if not self.serverSocket:            try:                self.connection = pymysql.connect(                    host=self.conn_setting["host"],                    port=self.conn_setting["port"],                    user=self.conn_setting["user"],                    password=self.conn_setting["password"],                    db=self.conn_setting["db"],                    charset=self.conn_setting["charset"],                    cursorclass=pymysql.cursors.DictCursor                )            except OperationalError as oe:                self.logger.error("MySQL Operational Error:")                print(oe)            except InternalError as ie:                self.logger.error("MySQL Internal Error:")                print(ie)            self.serverSocket = self.connection._sock        return self.serverSocket    def disconnect(self):        if self.connection:            self.connection.close()    def read_server_packet(self):        """        Reads a packet from a socket        """        # Read the size of the packet        psize = bytearray(3)        self.serverSocket.recv_into(psize, 3)        size = getSize(psize) + 1        # Read the rest of the packet        packet_payload = bytearray(size)        self.serverSocket.recv_into(packet_payload, size)        # Combine the chunks        psize.extend(packet_payload)        # if __debug__:        #     dump(psize)        return psize    def read_query_result(self):        # return        buff_list = []        buff = self.read_server_packet()        sequenceId = getSequenceId(buff)        print("sequenceId", sequenceId)        buff_list.append(buff)        # context.sequenceId = getSequenceId(packet)        packet_type = getType(buff)        if packet_type != Flags.OK and packet_type != Flags.ERR:            # read_full_result_set(            #     self.serverSocket,            #     context.clientSocket,            #     context.buff,            #     context.bufferResultSet,            #     resultsetType=context.expectedResultSet            # )            self.read_full_result_set(                buff_list,                buff,                packedPacketSize=65535,                bufferResultSet=False,                resultsetType=Flags.RS_OK            )        print("===== buff_list =====")        for buff in buff_list:            dump(buff)        print("===== buff_list =====")        return buff_list    def read_full_result_set(self, buff_list, buff, bufferResultSet=False,                             packedPacketSize=65535,                             resultsetType=Flags.RS_FULL):        """        Reads a full result set        """        from colcount import ColCount        from eof import EOF        colCount = ColCount.loadFromPacket(buff).colCount        # Read columns        for i in xrange(0, colCount):            packet = self.read_server_packet()            sequenceId = getSequenceId(packet)            print("sequenceId", sequenceId)            buff_list.append(packet)        # Check for OK or ERR        # Stop on ERR        packet = self.read_server_packet()        sequenceId = getSequenceId(packet)        print("sequenceId", sequenceId)        # buff_list.append(packet)        packetType = getType(packet)        # Error? Stop now        if packetType == Flags.ERR:            return        if packetType == Flags.EOF and resultsetType == Flags.RS_HALF:            return        # Read rows        while True:            packet = self.read_server_packet()            sequenceId = getSequenceId(packet)            print("sequenceId", sequenceId)            buff_list.append(packet)            packetType = getType(packet)            if packetType == Flags.EOF:                moreResults = EOF.loadFromPacket(packet).hasStatusFlag(                    Flags.SERVER_MORE_RESULTS_EXISTS)            if packetType == Flags.EOF or packetType == Flags.ERR:                break        # Show Create Table or similar?        if packetType == Flags.ERR:            return        # Multiple result sets?        if moreResults:            packet = self.read_server_packet()            sequenceId = getSequenceId(packet)            print("sequenceId", sequenceId)            buff_list.append(packet)            self.read_full_result_set(                buff_list,                self.read_server_packet(),                bufferResultSet=bufferResultSet,                packedPacketSize=packedPacketSize,                resultsetType=resultsetType)        return    def read_full_result_set_bak(self, buff_list, buff, bufferResultSet=True,                             packedPacketSize=65535,                             resultsetType=Flags.RS_FULL):        """        Reads a full result set        """        from colcount import ColCount        from eof import EOF        colCount = ColCount.loadFromPacket(buff).colCount        buff_list.append(buff)        # Read columns        for i in xrange(0, colCount):            buff = self.read_server_packet()            buff_list.append(buff)        # Check for OK or ERR        # Stop on ERR        buff = self.read_server_packet()        buff_list.append(buff)        packetType = getType(buff)        # Error? Stop now        if packetType == Flags.ERR:            return        if packetType == Flags.EOF and resultsetType == Flags.RS_HALF:            return        # Read rows        while True:            buff = self.read_server_packet()            buff_list.append(buff)            packetType = getType(buff)            if packetType == Flags.EOF:                moreResults = EOF.loadFromPacket(buff).hasStatusFlag(                    Flags.SERVER_MORE_RESULTS_EXISTS)            if 0 < packedPacketSize < len(buff):                buff_list.append(buff)            if packetType == Flags.EOF or packetType == Flags.ERR:                break        # Show Create Table or similar?        if packetType == Flags.ERR:            return        # Multiple result sets?        if moreResults:            self.read_full_result_set(                buff_list,                self.read_server_packet(),                bufferResultSet=bufferResultSet,                packedPacketSize=packedPacketSize,                resultsetType=resultsetType)        return
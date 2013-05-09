# coding=utf-8

import socket
import sys
import multiprocessing
import logging
from multiprocessing.reduction import rebuild_handle
from mysql_proto.flags import Flags

class Engine(multiprocessing.Process):
    # Config
    config = None
    logger = None
    
    # Connection Data
    port = None
    clientSocket = None
    
    # Packet Buffer
    buff = bytearray()
    offset = 0
    
    # Result set we expect?
    expectedResultSet = Flags.RS_OK

    authChallenge = None
    authReply = None
    
    schema = None
    query = None
    statusFlags = 0
    sequenceId = 0
    
    # Buffer or passthough?
    bufferResultSet = True
    packResultSet = True
    
    mode = Flags.MODE_INIT
    nextMode = Flags.MODE_INIT
    
    def __init__(self, config, clientSocket):
        clientSocket = rebuild_handle(clientSocket)
        clientSocket = socket.fromfd(clientSocket,
                                     socket.AF_INET,
                                     socket.SOCK_STREAM)
        
        self.config = config
        self.clientSocket = clientSocket
        self.kill_received = False
        
        self.logger = logging.getLogger('pymp')
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)
        streamHandler.setLevel(logging.DEBUG)
        self.logger.addHandler(streamHandler)
        if config['log']['verbose'] > 2:
            self.logger.setLevel(logging.DEBUG)
        elif config['log']['verbose'] > 1:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
            
        self.logger.debug('Accepted connection')
    
    def run(self):
        while not self.kill_received:
            if self.mode == Flags.MODE_INIT:
                self.logger.debug("MODE_INIT");
                self.nextMode = Flags.MODE_READ_HANDSHAKE;
            elif self.mode == Flags.MODE_READ_HANDSHAKE:
                self.logger.debug("MODE_READ_HANDSHAKE");
                self.nextMode = Flags.MODE_SEND_HANDSHAKE;
            elif self.mode == Flags.MODE_SEND_HANDSHAKE:
                self.logger.debug("MODE_SEND_HANDSHAKE");
                self.nextMode = Flags.MODE_READ_AUTH;
            elif self.mode == Flags.MODE_READ_AUTH:
                self.logger.debug("MODE_READ_AUTH");
                self.nextMode = Flags.MODE_SEND_AUTH;
            elif self.mode == Flags.MODE_SEND_AUTH:
                self.logger.debug("MODE_SEND_AUTH");
                self.nextMode = Flags.MODE_READ_AUTH_RESULT;
            elif self.mode == Flags.MODE_READ_AUTH_RESULT:
                self.logger.debug("MODE_READ_AUTH_RESULT");
                self.nextMode = Flags.MODE_SEND_AUTH_RESULT;
            elif self.mode == Flags.MODE_SEND_AUTH_RESULT:
                self.logger.tradebugce("MODE_SEND_AUTH_RESULT");
                self.nextMode = Flags.MODE_READ_QUERY;
            elif self.mode == Flags.MODE_READ_QUERY:
                self.logger.debug("MODE_READ_QUERY");
                self.nextMode = Flags.MODE_SEND_QUERY;
            elif self.mode == Flags.MODE_SEND_QUERY:
                self.logger.debug("MODE_SEND_QUERY");
                self.nextMode = Flags.MODE_READ_QUERY_RESULT;
            elif self.mode == Flags.MODE_READ_QUERY_RESULT:
                self.logger.debug("MODE_READ_QUERY_RESULT");
                self.nextMode = Flags.MODE_SEND_QUERY_RESULT;
            elif self.mode == Flags.MODE_SEND_QUERY_RESULT:
                self.logger.debug("MODE_SEND_QUERY_RESULT");
                self.nextMode = Flags.MODE_READ_QUERY;
            elif self.mode == Flags.MODE_CLEANUP:
                self.logger.debug("MODE_CLEANUP");
                self.nextMode = Flags.MODE_CLEANUP;
                self.kill_received = True
            else:
                self.logger.fatal("UNKNOWN MODE "+self.mode);
                self.kill_received = True
            # Set the next mode
            self.mode = self.nextMode
        
        self.logger.info('Exiting thread')

# coding=utf-8

from flags import Flags
import logging
import multiprocessing
from multiprocessing.reduction import rebuild_handle
import socket
import sys
import datetime

# Define our own log formatter to handle the removal of the date
class EngineLogFormat(logging.Formatter):
    converter = datetime.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
        return s

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
    
    plugins = {}
    
    def __init__(self, config, clientSocket):
        super(Engine, self).__init__()
        self.clientSocket = rebuild_handle(clientSocket)
        self.clientSocket = socket.fromfd(self.clientSocket,
                                          socket.AF_INET,
                                          socket.SOCK_STREAM)
        
        self.clientSocket.setsockopt(socket.IPPROTO_TCP,
                                     socket.TCP_NODELAY,
                                     1)
        
        self.clientSocket.setsockopt(socket.SOL_SOCKET,
                                     socket.SO_KEEPALIVE,
                                     1)
        
        self.clientSocket.settimeout(None)
        
        self.config = config
        self.kill_received = False
        
        self.logger = logging.getLogger('pymp.engine')
        
        if len(self.logger.handlers) == 0:
            streamHandler = logging.StreamHandler(sys.stdout)
            
            if int(config['log']['verbose']) > 2:
                self.logger.setLevel(logging.DEBUG)
                formatter = EngineLogFormat( '[%(asctime)s %(process)d '
                                            + '%(filename)s:%(lineno)d] '
                                            + '%(message)s')
            elif int(config['log']['verbose']) > 1:
                self.logger.setLevel(logging.INFO)
                formatter = EngineLogFormat( '[%(asctime)s %(process)d] '
                                            + '%(message)s')
            else:
                self.logger.setLevel(logging.WARNING)
                formatter = logging.Formatter('[%(asctime)s %(process)d] '
                                            + '%(filename)s:%(lineno)d '
                                            + '%(message)s')

            streamHandler.setFormatter(formatter)
            streamHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(streamHandler)
            
        self.logger.info('Accepted connection')
        
        if 'Proxy' in config['plugins']['enabled']:
            from plugins.proxy import Proxy
            self.plugins['Proxy'] = Proxy()
            
    def run(self):
        self.logger.info('Running')
        try:
            while not self.kill_received:
                if self.mode == Flags.MODE_INIT:
                    self.nextMode = Flags.MODE_READ_HANDSHAKE;
                    self.logger.info("MODE_INIT");
                    for plugin in self.plugins:
                        self.plugins[plugin].init(self)
                    
                elif self.mode == Flags.MODE_READ_HANDSHAKE:
                    self.nextMode = Flags.MODE_SEND_HANDSHAKE;
                    self.logger.info("MODE_READ_HANDSHAKE");
                    for plugin in self.plugins:
                        self.plugins[plugin].read_handshake(self)
                    
                elif self.mode == Flags.MODE_SEND_HANDSHAKE:
                    self.nextMode = Flags.MODE_READ_AUTH;
                    self.logger.info("MODE_SEND_HANDSHAKE");
                    for plugin in self.plugins:
                        self.plugins[plugin].send_handshake(self)
                    
                elif self.mode == Flags.MODE_READ_AUTH:
                    self.nextMode = Flags.MODE_SEND_AUTH;
                    self.logger.info("MODE_READ_AUTH");
                    for plugin in self.plugins:
                        self.plugins[plugin].read_auth(self)
                    
                elif self.mode == Flags.MODE_SEND_AUTH:
                    self.nextMode = Flags.MODE_READ_AUTH_RESULT;
                    self.logger.info("MODE_SEND_AUTH");
                    for plugin in self.plugins:
                        self.plugins[plugin].send_auth(self)
                    
                elif self.mode == Flags.MODE_READ_AUTH_RESULT:
                    self.nextMode = Flags.MODE_SEND_AUTH_RESULT;
                    self.logger.info("MODE_READ_AUTH_RESULT");
                    for plugin in self.plugins:
                        self.plugins[plugin].read_auth_result(self)
                    
                elif self.mode == Flags.MODE_SEND_AUTH_RESULT:
                    self.nextMode = Flags.MODE_READ_QUERY;
                    self.logger.info("MODE_SEND_AUTH_RESULT");
                    for plugin in self.plugins:
                        self.plugins[plugin].send_auth_result(self)
                    
                elif self.mode == Flags.MODE_READ_QUERY:
                    self.nextMode = Flags.MODE_SEND_QUERY;
                    self.logger.info("MODE_READ_QUERY");
                    for plugin in self.plugins:
                        self.plugins[plugin].read_query(self)
                    
                elif self.mode == Flags.MODE_SEND_QUERY:
                    self.nextMode = Flags.MODE_READ_QUERY_RESULT;
                    self.logger.info("MODE_SEND_QUERY");
                    for plugin in self.plugins:
                        self.plugins[plugin].send_query(self)
                    
                elif self.mode == Flags.MODE_READ_QUERY_RESULT:
                    self.nextMode = Flags.MODE_SEND_QUERY_RESULT;
                    self.logger.info("MODE_READ_QUERY_RESULT");
                    for plugin in self.plugins:
                        self.plugins[plugin].read_query_result(self)
                    
                elif self.mode == Flags.MODE_SEND_QUERY_RESULT:
                    self.nextMode = Flags.MODE_READ_QUERY;
                    self.logger.info("MODE_SEND_QUERY_RESULT");
                    for plugin in self.plugins:
                        self.plugins[plugin].send_query_result(self)
                    
                elif self.mode == Flags.MODE_CLEANUP:
                    self.nextMode = Flags.MODE_CLEANUP;
                    self.logger.info("MODE_CLEANUP");
                    for plugin in self.plugins:
                        self.plugins[plugin].cleanup(self)
                    self.halt()
                    
                else:
                    self.logger.fatal("UNKNOWN MODE "+self.mode);
                    self.halt()
                # Set the next mode
                self.mode = self.nextMode
        finally:
            self.logger.info('Exiting thread')
            self.clientSocket.close()
            
    def halt(self):
        self.logger.info('halt called')
        self.kill_received = True
        self.mode = Flags.MODE_CLEANUP
        self.nextMode = Flags.MODE_CLEANUP

# coding=utf-8

from plugin import Plugin
import socket
from ..packet import Packet
from ..auth.challenge import Challenge
from ..auth.response import Response
from ..flags import Flags
from ..resultset import ResultSet

class Proxy(Plugin):
    serverSocket = None
    
    def init(self, context):
        context.logger.debug('Proxy.init')
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.IPPROTO_TCP,
                                     socket.TCP_NODELAY,
                                     1)
        self.serverSocket.connect((context.config[
            'plugins']['Proxy']['remoteHost'],
                                   int(
                                    context.config[
                                        'plugins']['Proxy']['remotePort']
                                    )))
    
    def read_handshake(self, context):
        context.logger.debug('Proxy.read_handshake')
        packet = Packet.read_packet(self.serverSocket)
        Packet.dump(packet)
        context.authChallenge = Challenge.loadFromPacket(packet)
        context.authChallenge.removeCapabilityFlag(Flags.CLIENT_COMPRESS)
        context.authChallenge.removeCapabilityFlag(Flags.CLIENT_SSL)
        context.authChallenge.removeCapabilityFlag(Flags.CLIENT_LOCAL_FILES)
        
        ResultSet.characterSet = context.authChallenge.characterSet
        
        context.buff.extend(context.authChallenge.toPacket())
    
    def send_handshake(self, context):
        context.logger.debug('Proxy.send_handshake')
        context.clientSocket.sendall(context.buff)
        context.buff = bytearray()
    
    def read_auth(self, context):
        context.logger.debug('Proxy.read_auth')
        packet = Packet.read_packet(context.clientSocket)
        Packet.dump(packet)
        context.authReply = Response.loadFromPacket(packet)
        
        if not context.authReply.hasCapabilityFlag(Flags.CLIENT_PROTOCOL_41):
            this.logger.fatal('We do not support Protocols under 4.1')
            context.kill_received = True
            return
        
        context.authReply.removeCapabilityFlag(Flags.CLIENT_COMPRESS)
        context.authReply.removeCapabilityFlag(Flags.CLIENT_SSL)
        context.authReply.removeCapabilityFlag(Flags.CLIENT_LOCAL_FILES)
        
        context.schema = context.authReply.schema
        
        context.buff.extend(context.authReply.toPacket())
    
    def send_auth(self, context):
        context.logger.debug('Proxy.send_auth')
        self.serverSocket.sendall(context.buff)
        context.buff = bytearray()
    
    def read_auth_result(self, context):
        context.logger.debug('Proxy.read_auth_result')
        packet = Packet.read_packet(self.serverSocket)
        if Packet.getType(packet) != Flags.OK:
            this.logger.fatal('Auth is not okay!')
        context.buff.extend(packet)
    
    def send_auth_result(self, context):
        context.logger.debug('Proxy.send_auth_result')
        context.clientSocket.sendall(context.buff)
        context.buff = bytearray()
    
    def read_query(self, context):
        context.logger.debug('Proxy.read_query')
        context.bufferResultSet = false
        
        packet = Packet.read_packet(context.clientSocket)
        context.sequenceId = Packet.getSequenceId(packet)
        this.logger.debug('Client sequenceId: %s' % context.sequenceId)
        
        packet_type = Packet.getType(packet)
        
        if packet_type == Flags.COM_QUIT:
            context.logger.trace('COM_QUIT')
            context.kill_received = True
        elif packet_type == Flags.COM_INIT_DB:
            context.logger.trace('COM_INIT_DB');
            context.schema = Com_Initdb.loadFromPacket(packet).schema
        elif packet_type == Flags.COM_QUERY:
            context.logger.debug('COM_QUERY')
            context.query = Com_Query.loadFromPacket(packet).query
    
    def send_query(self, context):
        context.logger.debug('Proxy.send_query')
        self.serverSocket.sendall(context.buff)
        context.buff = bytearray()
    
    def read_query_result(self, context):
        context.logger.debug('Proxy.read_query_result')
        packet = Packet.read_packet(self.serverSocket)
    
    def send_query_result(self, context):
        context.logger.debug('Proxy.send_query_result')
        context.clientSocket.sendall(context.buff)
        context.buff = bytearray()
    
    def cleanup(self, context):
        context.logger.debug('Proxy.cleanup')
        context.kill_received = True

# coding=utf-8

import abc
from proto import Proto
from flags import Flags
import logging

class Packet(object):
    """
    Basic class for all mysql proto classes to inherit from
    """
    sequenceId = None
    
    @abc.abstractmethod
    def getPayload(self):
        """
        Return the payload as a bytearray
        """
        raise NotImplementedError('getPayload')
    
    def toPacket(self):
        """
        Convert a Packet object to a byte array stream
        """
        payload = self.getPayload()
        
        # Size is payload + packet size + sequence id
        size = len(payload)
        
        packet = bytearray(size+4)
        
        packet[0:2] = Proto.build_fixed_int(3, size)
        packet[3] = Proto.build_fixed_int(1, self.sequenceId)[0]
        packet[4:] = payload
        
        return packet
    
    def __len__(self):
        pass
    
    @staticmethod
    def getSize(packet):
        """
        Returns a specified packet size
        """
        return Proto(packet).get_fixed_int(3)
    
    @staticmethod
    def getType(packet):
        """
        Returns a specified packet type
        """
        return packet[4]
    
    @staticmethod
    def getSequenceId(packet):
        """
        Returns the Sequence ID for the given packet
        """
        return Proto(packet, 3).get_fixed_int(1)
    
    @staticmethod
    def dump(packet):
        """
        Dumps a packet to the logger
        """
        logger = logging.getLogger('pymp.engine.packet')
        offset = 0
        
        if not logger.isEnabledFor(logging.DEBUG):
            return
        
        dump = 'Packet Dump\n'
        
        while offset < len(packet):
            dump += hex(offset)[2:].zfill(8).upper()
            dump += '  '
            
            for x in xrange(16):
                if offset+x >= len(packet):
                    dump += '   '
                else:
                    dump += hex(packet[offset+x])[2:].upper().zfill(2)
                    dump += ' '
                    if x == 7:
                        dump += ' '
                
            dump += '  '
            
            for x in xrange(16):
                if offset+x >= len(packet):
                    break
                c = chr(packet[offset+x])
                if ( len(c) > 1
                     or packet[offset+x] < 32
                     or packet[offset+x] == 255 ):
                    dump += '.'
                else:
                    dump += c
                    
                if x == 7:
                    dump += ' '
                
            dump += '\n'
            offset += 16
            
        logger.debug(dump)
    
    @staticmethod
    def read_packet(socket_in, direction='unknown'):
        """
        Reads a packet from a socket
        """
        logger = logging.getLogger('pymp.engine.packet')
        logger.info('Packet.read_packet %s', direction)
        # Read the size of the packet
        psize = bytearray(3)
        socket_in.recv_into(psize, 3)
        
        size = Packet.getSize(psize)+1
        
        # Read the rest of the packet
        packet_payload = bytearray(size)
        socket_in.recv_into(packet_payload, size)
        
        # Combine the chunks
        psize.extend(packet_payload)
        Packet.dump(psize)
        
        return psize
    
    @staticmethod
    def read_full_result_set(socket_in, socket_out, buff, bufferResultSet=True,
                             packedPacketSize = 65535):
        """
        Reads a full result set
        """
        from colcount import ColCount
        from eof import EOF
        
        colCount = ColCount.loadFromPacket(buff).colCount
        
        # Evil optimization
        if not bufferResultSet:
            Packet.write_packet(socket_out, buff)
            buff = bytearray()
        
        # Read columns
        for i in xrange(0, colCount+1):
            packet = Packet.read_packet(socket_in)
            
            # Evil optimization
            if not bufferResultSet:
                Packet.write_packet(socket_out, packet)
            else:
                buff.extend(packet)
                
        packedPacket = bytearray()
        
        # Read rows
        while True:
            packet = Packet.read_packet(socket_in)
            packetType = Packet.getType(packet)
            
            if len(packedPacket) + len(packet) > packedPacketSize:
                subsize = packedPacketSize - len(packedPacket)
                packedPacket.extend(packet[0:subsize])
                
                # Evil optimization
                if not bufferResultSet:
                    Packet.write_packet(socket_out, packedPacket)
                else:
                    buff.extend(packedPacket)
                    
                packedPacket = bytearray(packet[subsize:])
                
            else:
                packedPacket.extend(packet)
                
            if packetType == Flags.EOF or packetType == Flags.ERR:
                break
                
        # Evil optimization
        if not bufferResultSet:
            Packet.write_packet(socket_out, packedPacket)
        else:
            buff.extend(packedPacket)
            
        # Show Create Table or similar?
        if packetType == Flags.ERR:
            return buff
        
        # Multiple result sets?
        if EOF.loadFromPacket(packet).hasStatusFlag(
            Flags.SERVER_MORE_RESULTS_EXISTS):
            buff.extend(Packet.read_packet(socket_in))
            buff.extend(Packet.read_full_result_set(socket_in,
                                                    socket_out,
                                                    buff,
                                                    bufferResultSet=bufferResultSet,
                                                    packedPacketSize=packedPacketSize))
        return buff

    @staticmethod
    def write_packet(socket_out, packet, direction='unknown'):
        """
        Writes a packet to a socket
        """
        logger = logging.getLogger('pymp.engine.packet')
        logger.info('Packet.write_packet %s', direction)
        Packet.dump(packet)
        socket_out.sendall(packet)
        packet = bytearray()

#!/usr/bin/env python
# coding=utf-8

import abc
from mysql_proto.proto import Proto
from mysql_proto.colcount import ColCount
from mysql_proto.flags import Flags
from mysql_proto.eof import EOF

class Packet(object):
    """
    Basic class for all mysql proto classes to inherit from
    """
    sequenceId = 0;
    
    @abc.abstractmethod
    def getPayload():
        """
        Return the payload as a bytearray
        """
        raise NotImplementedError('getPayload')
        pass
    
    def toPacket():
        """
        Convert a Packet object to a byte array stream
        """
        payload = self.getPayload();
        
        # Size is payload + packet size + sequence id
        size = len(payload)+4
        
        packet = bytearray(size+4)
        
        packet += Proto.build_fixed_int(3, len(payload))
        packet += Proto.build_fixed_int(1, self.sequenceId)
        packet += payload
        
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
        pass
    
    @staticmethod
    def read_packet(socket):
        """
        Reads a packet from a socket
        """
        # Read the size of the packet
        psize = bytearray(3)
        (nbytes, address) = socket.recvfrom_into(psize, 3)
        size = Packet.getSize(psize)
        
        # Read the rest of the packet
        packet_payload = bytearray(size+1)
        (nbytes, address) = socket.recvfrom_into(packet_payload, size+1)
        
        # Combine the chunks
        packet = bytearray(size+4)
        packet += psize
        packet += packet_payload
        
        return packet
    
    @staticmethod
    def read_full_result_set(socket_in, socket_out, buff, bufferResultSet=True,
                             packedPacketSize = 65535):
        """
        Reads a full result set
        """
        colCount = ColCount.loadFromPacket(buff).colCount
        
        # Evil optimization
        if not bufferResultSet:
            Packet.write(socket_out, buff)
            buff = bytearray()
        
        # Read columns
        for i in xrange(0, colCount):
            packet = Packet.read_packet(socket_in)
            
            # Evil optimization
            if not bufferResultSet:
                Packet.write(socket_out, packet)
            else:
                buff.extend(packet)
                
        packedPacket = bytearray()
        
        # Read rows
        while True:
            packet = Packet.read_packet(socket_in)
            packetType = Packet.getType(packet)
            
            if packetType == Flags.EOF or packetType == Flags.ERR:
                buff.extend(packedPacket)
                packedPacket = packet
                break
            
            if len(packedPacket) + len(packet) > packedPacketSize:
                subsize = packedPacketSize - len(packedPacket)
                packedPacket.extend(packet[0:subsize])
                
                # Evil optimization
                if not bufferResultSet:
                    Packet.write(socket_out, packedPacket)
                else:
                    buff.extend(packedPacket)
                    
                packedPacket = bytearray(packet[subsize:])
                
            else:
                packedPacket.extend(packet)
                
        # Evil optimization
        if not bufferResultSet:
            Packet.write(socket_out, packedPacket)
        else:
            buff.extend(packedPacket)
            
        # Show Create Table or similar?
        if Packet.getType(packet) == Flags.ERR:
            return buff
        
        # Multiple result sets?
        if EOF.loadFromPacket(packet).hasStatusFlags(
            Flags.SERVER_MORE_RESULTS_EXISTS):
            buff.extend(Packet.read_packet(socket_in))
            buff = Packet.read_full_result_set(socket_id,
                                               socket_out,
                                               buff,
                                               bufferResultSet,
                                               packetPacketSize)
        
        return buff
    
    @staticmethod
    def write(socket, buff):
        """
        Write a buffer to a socket
        """
        socket.sendAll(buff)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

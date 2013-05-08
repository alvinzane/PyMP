#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from flags import Flags

class Send_Log_data(Packet):
    data = bytearray()
    
    def getPayload(self):
        payload = bytearray()
        
        payload.extend(self.data)
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Send_Log_data()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        obj.data = proto.packet[proto.offset:]
        
        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

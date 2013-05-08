#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from flags import Flags

class Processkill(Packet):
    schema = ""
    
    def getPayload(self):
        payload = bytearray()
        
        payload.extend(Proto.build_byte(Flags.COM_PROCESS_KILL))
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Processkill()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        
        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

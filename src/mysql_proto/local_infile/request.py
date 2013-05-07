#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from flags import Flags

class Request(Packet):
    filename = ""
    
    def getPayload(self):
        payload = bytearray()
        
        payload.extend(Proto.build_eop_str(self.filename))
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Request()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        obj.filename = proto.get_eop_str()

        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

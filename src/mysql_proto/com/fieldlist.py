#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from flags import Flags

class Fieldlist(Packet):
    table = ""
    fields = ""
    
    def getPayload(self):
        payload = bytearray()
        
        payload.extend(Proto.build_byte(Flags.COM_FIELD_LIST))
        payload.extend(Proto.build_null_str(self.table))
        payload.extend(Proto.build_eop_str(self.fields))
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Fieldlist()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        obj.table = proto.get_null_str()
        obj.fields = proto.get_eop_str()
        
        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

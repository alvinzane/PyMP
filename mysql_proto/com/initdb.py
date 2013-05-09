# coding=utf-8

from ..packet import Packet
from ..proto import Proto
from ..flags import Flags

class Initdb(Packet):
    schema = ""
    
    def getPayload(self):
        payload = bytearray()
        
        payload.extend(Proto.build_byte(Flags.COM_INIT_DB))
        payload.extend(Proto.build_eop_str(self.schema))
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Initdb()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        obj.schema = proto.get_eop_str()
        
        return obj

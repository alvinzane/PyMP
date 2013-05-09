#!/usr/bin/env python
# coding=utf-8

from ..packet import Packet
from ..proto import Proto
from ..flags import Flags

class Response(Packet):
    capabilityFlags = Flags.CLIENT_PROTOCOL_41
    maxPacketSize = 0
    characterSet = 0
    username = ""
    authResponse = ""
    schema = ""
    
    def setCapabilityFlag(self, flag):
        self.capabilityFlags |= flag
    
    def removeCapabilityFlag(self, flag):
        self.capabilityFlags &= ~flag
    
    def toggleCapabilityFlag(self, flag):
        self.capabilityFlags ^= flag
    
    def hasCapabilityFlag(self, flag):
        return ((self.capabilityFlags & flag) == flag)
    
    def getPayload(self):
        payload = bytearray()
        
        if self.hasCapabilityFlag(Flags.CLIENT_PROTOCOL_41):
            payload.extend( Proto.build_fixed_int(4, self.capabilityFlags));
            payload.extend( Proto.build_fixed_int(4, self.maxPacketSize));
            payload.extend( Proto.build_fixed_int(1, self.characterSet));
            payload.extend( Proto.build_fixed_str(23, ""));
            payload.extend( Proto.build_null_str(self.username));
            if this.hasCapabilityFlag(Flags.CLIENT_SECURE_CONNECTION):
                payload.extend( Proto.build_lenenc_str(self.authResponse));
            else:
                payload.extend( Proto.build_null_str(self.authResponse));
            payload.extend( Proto.build_fixed_str(len(self.schema), self.schema));
        else:
            payload.extend( Proto.build_fixed_int(2, self.capabilityFlags));
            payload.extend( Proto.build_fixed_int(3, self.maxPacketSize));
            payload.extend( Proto.build_null_str(self.username));
            payload.extend( Proto.build_null_str(self.authResponse));
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Response()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        obj.capabilityFlags = proto.get_fixed_int(2)
        proto.offset -= 2
        
        print obj.capabilityFlags
        print Flags.CLIENT_PROTOCOL_41
        import sys
        sys.exit(1)
        
        if obj.hasCapabilityFlag(Flags.CLIENT_PROTOCOL_41):
            obj.capabilityFlags = proto.get_fixed_int(4)
            obj.maxPacketSize = proto.get_fixed_int(4)
            obj.characterSet = proto.get_fixed_int(1)
            proto.get_fixed_str(23)
            obj.username = proto.get_null_str()
            
            if obj.hasCapabilityFlag(Flags.CLIENT_SECURE_CONNECTION):
                obj.authResponse = proto.get_null_str()
            else:
                obj.authResponse = proto.get_lenenc_str()
            
            obj.schema = proto.get_eop_str()
            
        else:
            obj.capabilityFlags = proto.get_fixed_int(2)
            obj.maxPacketSize = proto.get_fixed_int(3)
            obj.username = proto.get_null_str()
            obj.schema = proto.get_null_str()
        
        return obj;

if __name__ == "__main__":
    import doctest
    doctest.testmod()

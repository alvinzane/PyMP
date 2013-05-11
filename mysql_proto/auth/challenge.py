# coding=utf-8

from ..packet import Packet
from ..proto import Proto
from ..flags import Flags

class Challenge(Packet):
    protocolVersion = 0x0a
    serverVersion = ""
    connectionId = 0
    challenge1 = ""
    capabilityFlags = Flags.CLIENT_PROTOCOL_41
    characterSet = 0
    statusFlags = 0
    challenge2 = ""
    
    def setCapabilityFlag(self, flag):
        self.capabilityFlags |= flag
    
    def removeCapabilityFlag(self, flag):
        self.capabilityFlags &= ~flag
    
    def toggleCapabilityFlag(self, flag):
        self.capabilityFlags ^= flag
    
    def hasCapabilityFlag(self, flag):
        return ((self.capabilityFlags & flag) == flag)
    
    def setStatusFlag(self, flag):
        self.statusFlags |= flag
    
    def removeStatusFlag(self, flag):
        self.statusFlags &= ~flag
    
    def toggleStatusFlag(self, flag):
        self.statusFlags ^= flag
    
    def hasStatusFlag(self, flag):
        return ((self.statusFlags & flag) == flag)
    
    def getPayload(self):
        payload = bytearray()
        
        payload.extend(Proto.build_fixed_int(1, self.protocolVersion))
        payload.extend(Proto.build_null_str(self.serverVersion))
        payload.extend(Proto.build_fixed_int(4, self.connectionId))
        payload.extend(Proto.build_fixed_str(8, self.challenge1))
        payload.extend(Proto.build_filler(1))
        payload.extend(Proto.build_fixed_int(2, self.capabilityFlags))
        payload.extend(Proto.build_fixed_int(1, self.characterSet))
        payload.extend(Proto.build_fixed_int(2, self.statusFlags))
        payload.extend(Proto.build_fixed_str(13, ""))
        
        if self.hasCapabilityFlag(Flags.CLIENT_SECURE_CONNECTION):
            payload.extend( Proto.build_fixed_str(12, self.challenge2))
            payload.extend( Proto.build_filler(1))
        
        return payload
    
    @staticmethod
    def loadFromPacket(packet):
        obj = Challenge()
        proto = Proto(packet, 3)
        
        obj.sequenceId = proto.get_fixed_int(1)
        obj.protocolVersion = proto.get_fixed_int(1)
        obj.serverVersion = proto.get_null_str()
        obj.connectionId = proto.get_fixed_int(4)
        obj.challenge1 = proto.get_fixed_str(8)
        proto.get_filler(1)
        obj.capabilityFlags = proto.get_fixed_int(2)
        obj.characterSet = proto.get_fixed_int(1)
        obj.statusFlags = proto.get_fixed_int(2)
        proto.get_filler(13)
        
        if (obj.hasCapabilityFlag(Flags.CLIENT_SECURE_CONNECTION)):
            obj.challenge2 = proto.get_fixed_str(12)
            proto.get_filler(1)
        
        return obj

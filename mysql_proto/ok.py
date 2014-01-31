#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from flags import Flags


class OK(Packet):
    __slots__ = ('affectedRows', 'lastInsertId', 'statusFlags',
                 'warnings') + Packet.__slots__

    def __init__(self):
        super(OK, self).__init__()
        self.affectedRows = 0
        self.lastInsertId = 0
        self.statusFlags = 0
        self.warnings = 0

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

        payload.extend(Proto.build_byte(Flags.OK))
        payload.extend(Proto.build_lenenc_int(self.affectedRows))
        payload.extend(Proto.build_lenenc_int(self.lastInsertId))
        payload.extend(Proto.build_fixed_int(2, self.statusFlags))
        payload.extend(Proto.build_fixed_int(2, self.warnings))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = OK()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        obj.affectedRows = proto.get_lenenc_int()
        obj.lastInsertId = proto.get_lenenc_int()
        obj.statusFlags = proto.get_fixed_int(2)
        obj.warnings = proto.get_fixed_int(2)

        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

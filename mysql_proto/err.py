#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from mysql_proto import flags as Flags


class ERR(Packet):
    __slots__ = ('errorCode', 'sqlState', 'errorMessage') + Packet.__slots__

    def __init__(self):
        self.errorCode = 0
        self.sqlState = 'HY000'
        self.errorMessage = ''

    def getPayload(self):
        payload = bytearray()

        payload.extend(Proto.build_byte(Flags.ERR))
        payload.extend(Proto.build_fixed_int(2, self.errorCode))
        payload.extend(Proto.build_byte('#'))
        payload.extend(Proto.build_fixed_str(5, self.sqlState))
        payload.extend(Proto.build_eop_str(self.errorMessage))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = ERR()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        obj.errorCode = proto.get_fixed_int(2)
        proto.get_filler(1)
        obj.sqlState = proto.get_fixed_str(5)
        obj.errorMessage = proto.get_eop_str()

        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

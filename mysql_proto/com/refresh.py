# coding=utf-8

from ..packet import Packet
from ..proto import Proto
from ..flags import Flags


class Refresh(Packet):
    __slots__ = ('flags', ) + Packet.__slots__

    def __init__(self):
        super(Refresh, self).__init__()
        self.flags = 0x00

    def getPayload(self):
        payload = bytearray()

        payload.extend(Proto.build_byte(Flags.COM_REFRESH))
        payload.extend(Proto.build_fixed_int(1, self.flags))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Refresh()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        obj.flags = proto.get_fixed_int(1)

        return obj

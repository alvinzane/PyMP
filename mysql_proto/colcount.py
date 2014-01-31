#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto


class ColCount(Packet):
    __slots__ = ('colCount',) + Packet.__slots__

    def __init__(self):
        super(ColCount, self).__init__()
        self.colCount = None

    def getPayload(self):
        payload = Proto.build_lenenc_int(self.colCount)
        return payload

    @staticmethod
    def loadFromPacket(packet):
        """
        >>> colcount = ColCount()
        >>> colcount.sequenceId = 1
        >>> colcount.colCount = 5
        >>> colcount.colCount
        5
        >>> pkt = colcount.toPacket()
        >>> pkt
        bytearray(b'\\x01\\x00\\x00\\x01\\x05')
        >>> colcount2 = ColCount.loadFromPacket(pkt)
        >>> colcount2.colCount
        5
        >>> colcount2.sequenceId
        1
        """
        obj = ColCount()
        proto = Proto(packet, 3)
        obj.sequenceId = proto.get_fixed_int(1)
        obj.colCount = proto.get_lenenc_int()

        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# coding=utf-8


from py_mysql_server.lib.packet import Packet
from py_mysql_server.lib.proto import Proto


class Execute(Packet):
    __slots__ = ('data', ) + Packet.__slots__

    def __init__(self):
        super(Execute, self).__init__()
        self.data = bytearray()

    def getPayload(self):
        payload = bytearray()

        payload.extend(self.data)

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Execute()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        obj.data = proto.packet[proto.offset:]

        return obj

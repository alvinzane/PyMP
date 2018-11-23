# coding=utf-8

from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import Packet
from py_mysql_server.lib.proto import Proto

class Debug(Packet):
    def getPayload(self):
        payload = bytearray()

        payload.extend(Proto.build_byte(Flags.COM_DEBUG))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Debug()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)

        return obj

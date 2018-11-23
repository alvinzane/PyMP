# coding=utf-8

from py_mysql_server.lib import Flags
from py_mysql_server.lib.packet import Packet
from py_mysql_server.lib.proto import Proto


class Query(Packet):
    __slots__ = ('query',) + Packet.__slots__

    def __init__(self):
        super(Query, self).__init__()
        self.query = ''

    def getPayload(self):
        payload = bytearray()

        payload.extend(Proto.build_byte(Flags.COM_QUERY))
        payload.extend(Proto.build_eop_str(self.query))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Query()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)
        obj.query = proto.get_eop_str()

        return obj

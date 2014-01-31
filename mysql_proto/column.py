#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from resultset import ResultSet
from flags import Flags


class Column(Packet):
    __slots__ = ('catalog', 'schema', 'table', 'org_table', 'name', 'org_name',
                 'characterSet', 'columnLength', 'colType', 'flags',
                 'decimals') + Packet.__slots__

    def __init__(self, name=''):
        super(Column, self).__init__()
        self.characterSet = ResultSet.characterSet
        self.name = name
        self.catalog = 'def'
        self.schema = ''
        self.table = ''
        self.org_table = ''
        self.org_name = ''
        self.columnLength = 0
        self.colType = Flags.MYSQL_TYPE_VAR_STRING
        self.flags = 0
        self.decimals = 31

    def getPayload(self):
        payload = bytearray()

        payload.extend(Proto.build_lenenc_str(self.catalog))
        payload.extend(Proto.build_lenenc_str(self.schema))
        payload.extend(Proto.build_lenenc_str(self.table))
        payload.extend(Proto.build_lenenc_str(self.org_table))
        payload.extend(Proto.build_lenenc_str(self.name))
        payload.extend(Proto.build_lenenc_str(self.org_name))
        payload.extend(Proto.build_filler(1, b'\x0c'))
        payload.extend(Proto.build_fixed_int(2, self.characterSet))
        payload.extend(Proto.build_fixed_int(4, self.columnLength))
        payload.extend(Proto.build_fixed_int(1, self.colType))
        payload.extend(Proto.build_fixed_int(2, self.flags))
        payload.extend(Proto.build_fixed_int(1, self.decimals))
        payload.extend(Proto.build_filler(2))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Column()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        obj.catalog = proto.get_lenenc_str()
        obj.schema = proto.get_lenenc_str()
        obj.table = proto.get_lenenc_str()
        obj.org_table = proto.get_lenenc_str()
        obj.name = proto.get_lenenc_str()
        obj.org_name = proto.get_lenenc_str()
        proto.get_filler(1)
        obj.characterSet = proto.get_fixed_int(2)
        obj.columnLength = proto.get_fixed_int(4)
        obj.type = proto.get_fixed_int(1)
        obj.flags = proto.get_fixed_int(2)
        obj.decimals = proto.get_fixed_int(1)
        proto.get_filler(2)

        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

#!/usr/bin/env python
# coding=utf-8

from packet import Packet
from proto import Proto
from mysql_proto import flags as Flags


class Row(Packet):
    __slots__ = ('rowType', 'colType', 'data') + Packet.__slots__

    def __init__(self, *args, **kwargs):
        super(Row, self).__init__()

        self.rowType = Flags.ROW_TYPE_TEXT
        self.colType = Flags.MYSQL_TYPE_VAR_STRING
        self.data = list()

        for x in args:
            self.data.append(x)
        for x in kwargs:
            self.data.append(x)

    def getPayload(self):
        payload = bytearray()

        for col in self.data:
            if self.rowType == Flags.ROW_TYPE_TEXT:
                if isinstance(col, basestring):
                    payload.extend(Proto.build_lenenc_str(col))
                elif isinstance(col, (int, long)):
                    payload.extend(Proto.build_lenenc_int(col))
                elif isinstance(col, (float, complex)):
                    payload.extend(Proto.build_lenenc_str(str(col)))
                else:
                    raise NotImplementedError()
            elif self.rowType == Flags.ROW_TYPE_BINARY:
                raise NotImplementedError()
            else:
                raise NotImplementedError()

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Row()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)

        # TODO: Extract row data here

        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

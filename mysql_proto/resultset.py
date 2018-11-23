#!/usr/bin/env python
# coding=utf-8

from mysql_proto import flags as Flags
from colcount import ColCount
from eof import EOF


class ResultSet(object):
    __slots__ = ('characterSet', 'columns', 'rows')

    def __init__(self):
        self.characterSet = Flags.CS_latin1_swedish_ci
        self.columns = list()
        self.rows = list()

    def toPackets(self):
        packets = bytearray()

        maxRowSize = 0

        # TODO: Fix this!
        #for col in self.columns:
        #    size = len(col.toPacket())
        #    if size > maxRowSize:
        #        maxRowSize = size

        colCount = ColCount()
        colCount.sequenceId = self.sequenceId
        self.sequenceId += 1
        colCount.colCount = len(self.columns)
        packets.extend(colCount.toPacket())

        for col in self.columns:
            col.sequenceId = self.sequenceId
            self.sequenceId += 1
            col.columnLength = maxRowSize
            packets.extend(col.toPacket())

        eof = EOF()
        eof.sequenceId = self.sequenceId
        self.sequenceId += 1
        packets.extend(eof.toPacket())

        for row in self.rows:
            row.sequenceId = self.sequenceId
            self.sequenceId += 1
            packets.extend(row.toPacket())

        eof = EOF()
        eof.sequenceId = self.sequenceId
        self.sequenceId += 1
        packets.extend(eof.toPacket())

        return packets

    def addColumn(self, column):
        self.columns.append(column)

    def addRow(self, row):
        self.row.append(row)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

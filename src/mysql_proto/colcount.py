#!/usr/bin/env python
# coding=utf-8

from mysql_proto.packet import Packet
from mysql_proto.proto import Proto

class ColCount(Packet):
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()

#!/usr/bin/env python
# coding=utf-8


class Proto(object):
    __slots__ = ('packet', 'offset')

    def __init__(self, packet, offset=0):
        self.packet = packet
        self.offset = offset

    def has_remaining_data(self):
        return len(self.packet) - self.offset > 0

    @staticmethod
    def build_fixed_int(size, value):
        """
        Build a MySQL Fixed Int

        >>> Proto.build_fixed_int(1, 0)
        bytearray(b'\\x00')

        >>> Proto.build_fixed_int(1, 255)
        bytearray(b'\\xff')

        >>> Proto.build_fixed_int(2, 0)
        bytearray(b'\\x00\\x00')

        >>> Proto.build_fixed_int(2, 0xFFFF)
        bytearray(b'\\xff\\xff')

        >>> Proto.build_fixed_int(3, 0)
        bytearray(b'\\x00\\x00\\x00')

        >>> Proto.build_fixed_int(4, 0)
        bytearray(b'\\x00\\x00\\x00\\x00')

        >>> Proto.build_fixed_int(8, 0)
        bytearray(b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00')

        >>> Proto.build_fixed_int(8, 255)
        bytearray(b'\\xff\\x00\\x00\\x00\\x00\\x00\\x00\\x00')
        """
        packet = bytearray(size)
        if size >= 1:
            packet[0] = ((value >> 0) & 0xFF)
        if size >= 2:
            packet[1] = ((value >> 8) & 0xFF)
        if size >= 3:
            packet[2] = ((value >> 16) & 0xFF)
        if size >= 4:
            packet[3] = ((value >> 24) & 0xFF)
        if size >= 8:
            packet[4] = ((value >> 32) & 0xFF)
            packet[5] = ((value >> 40) & 0xFF)
            packet[6] = ((value >> 48) & 0xFF)
            packet[7] = ((value >> 56) & 0xFF)
        return packet

    @staticmethod
    def build_lenenc_int(value):
        """
        Build a MySQL Length Encoded Int

        >>> Proto.build_lenenc_int(0)
        bytearray(b'\\x00')

        >>> Proto.build_lenenc_int(251)
        bytearray(b'\\xfc\\xfb\\x00')

        >>> Proto.build_lenenc_int(252)
        bytearray(b'\\xfc\\xfc\\x00')

        >>> Proto.build_lenenc_int((2**16))
        bytearray(b'\\xfd\\x00\\x00\\x01')

        >>> Proto.build_lenenc_int((2**24))
        bytearray(b'\\xfe\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00')

        >>> Proto.build_lenenc_int((2**25))
        bytearray(b'\\xfe\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00')


        """
        if (value < 251):
            packet = bytearray(1)
            packet[0] = ((value >> 0) & 0xFF)
        elif (value < (2**16 - 1)):
            packet = bytearray(3)
            packet[0] = 0xFC
            packet[1] = ((value >> 0) & 0xFF)
            packet[2] = ((value >> 8) & 0xFF)
        elif (value < (2**24 - 1)):
            packet = bytearray(4)
            packet[0] = 0xFD
            packet[1] = ((value >> 0) & 0xFF)
            packet[2] = ((value >> 8) & 0xFF)
            packet[3] = ((value >> 16) & 0xFF)
        else:
            packet = bytearray(9)
            packet[0] = 0xFE
            packet[1] = ((value >> 0) & 0xFF)
            packet[2] = ((value >> 8) & 0xFF)
            packet[3] = ((value >> 16) & 0xFF)
            packet[4] = ((value >> 24) & 0xFF)
            packet[5] = ((value >> 32) & 0xFF)
            packet[6] = ((value >> 40) & 0xFF)
            packet[7] = ((value >> 48) & 0xFF)
            packet[8] = ((value >> 56) & 0xFF)
        return packet

    @staticmethod
    def build_lenenc_str(value):
        """
        Build a MySQL Length Encoded String

        >>> Proto.build_lenenc_str('abc')
        bytearray(b'\\x03abc')

        Empty strings are supported:
        >>> Proto.build_lenenc_str('')
        bytearray(b'\\x00')

        Really long strings:
        >>> Proto.build_lenenc_str('abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
')
        bytearray(b'\\xfc\\xf4\\x05abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123abc123\
')
        """
        if value == '':
            return bytearray(1)

        size = Proto.build_lenenc_int(len(value))
        fixed_str = Proto.build_fixed_str(len(value), value)
        return size+fixed_str

    @staticmethod
    def build_null_str(value):
        """
        Build a MySQL Null String

        >>> Proto.build_null_str('ab')
        bytearray(b'ab\\x00')

        Empty string is just a null:
        >>> Proto.build_null_str('')
        bytearray(b'\\x00')
        """
        return Proto.build_fixed_str(len(value) + 1, value)

    @staticmethod
    def build_fixed_str(size, value):
        """
        Build a MySQL Fixed String

        >>> Proto.build_fixed_str(2, 'ab')
        bytearray(b'ab')

        Zero pad if size > sizeOf(value):
        >>> Proto.build_fixed_str(3, 'ab')
        bytearray(b'ab\\x00')
        """
        packet = bytearray(size)
        for i, c in enumerate(value):
            packet[i] = c
        return packet

    @staticmethod
    def build_eop_str(value):
        """
        Build a MySQL End of Packet String

        >>> Proto.build_eop_str('ab')
        bytearray(b'ab')
        """
        return Proto.build_fixed_str(len(value), value)

    @staticmethod
    def build_filler(size, fill=0x00):
        """
        Build a set of filler

        >>> Proto.build_filler(1)
        bytearray(b'\\x00')

        >>> Proto.build_filler(2)
        bytearray(b'\\x00\\x00')

        >>> Proto.build_filler(1, 0x1c)
        bytearray(b'\\x1c')

        >>> Proto.build_filler(2, 0xff)
        bytearray(b'\\xff\\xff')
        """
        packet = bytearray(size)
        for i in xrange(size):
            packet[i] = fill
        return packet

    @staticmethod
    def build_byte(value):
        """
        Build a extendable byte

        >>> Proto.build_byte(0)
        bytearray(b'\\x00')

        >>> Proto.build_byte(1)
        bytearray(b'\\x01')

        >>> Proto.build_byte(0xFF)
        bytearray(b'\\xff')
        """
        packet = bytearray(1)
        packet[0] = value
        return packet

    @staticmethod
    def get_fixed_int_sniplet(packet):
        """
        Extract a fixed int from a packet subset

        >>> Proto.get_fixed_int_sniplet(Proto.build_fixed_int(1, 0))
        0

        >>> Proto.get_fixed_int_sniplet(Proto.build_fixed_int(1 ,1))
        1

        >>> Proto.get_fixed_int_sniplet(Proto.build_fixed_int(1, 255))
        255
        """
        value = 0
        for i in xrange(len(packet)-1, 0, -1):
            value |= packet[i] & 0xFF
            value <<= 8
        value |= packet[0] & 0xFF
        return value

    def get_fixed_int(self, size):
        """
        Extract a fixed int the current packet

        >>> packet = Proto(Proto.build_fixed_int(1, 0))
        >>> packet.get_fixed_int(1)
        0
        """
        value = Proto.get_fixed_int_sniplet(
            self.packet[self.offset:self.offset+size])
        self.offset += size
        return value

    def get_filler(self, size):
        """
        Skip over packet filler

        >>> pckt = bytearray(5)
        >>> packet = Proto(pckt)
        >>> packet.offset
        0
        >>> packet.get_filler(2)
        >>> packet.offset
        2
        """
        self.offset += size

    def get_lenenc_int(self):
        """
        Extract a Length Encoded Int from the current packet position

        >>> pckt = Proto.build_lenenc_int(255)
        >>> packet = Proto(pckt)
        >>> packet.get_lenenc_int()
        255
        """
        size = 0

        if self.packet[self.offset] < 251:
            size = 1
        elif self.packet[self.offset] == 252:
            self.offset += 1
            size = 2
        elif self.packet[self.offset] == 253:
            self.offset += 1
            size = 3
        elif self.packet[self.offset] == 254:
            self.offset += 1
            size = 8

        return self.get_fixed_int(size)

    def get_fixed_str(self, size):
        """
        Extract a fixed length string from the current packet position

        >>> target = "The brown dog did stuff"
        >>> pckt = Proto.build_fixed_str(len(target), target)
        >>> packet = Proto(pckt)
        >>> packet.get_fixed_str(len(pckt))
        'The brown dog did stuff'
        """
        value = ''

        for i in xrange(self.offset, self.offset + size):
            value += chr(self.packet[i])
            self.offset += 1

        return value

    def get_null_str(self):
        """
        Extract a null string from the current packet position

        >>> target = "The brown dog did stuff"
        >>> pckt = Proto.build_null_str(target)
        >>> packet = Proto(pckt)
        >>> packet.get_null_str()
        'The brown dog did stuff'
        """
        value = ''

        for i in xrange(self.offset, len(self.packet)):
            if self.packet[i] == 0x00:
                self.offset += 1
                break
            value += chr(self.packet[i])
            self.offset += 1

        return value

    def get_eop_str(self):
        """
        Extract a eop string from the current packet position

        >>> target = "The brown dog did stuff"
        >>> pckt = Proto.build_eop_str(target)
        >>> packet = Proto(pckt)
        >>> packet.get_eop_str()
        'The brown dog did stuff'
        """
        value = ''

        for i in xrange(self.offset, len(self.packet)):
            if self.packet[i] == 0x00 and i == len(self.packet) - 1:
                self.offset += 1
                break
            value += chr(self.packet[i])
            self.offset += 1

        return value

    def get_lenenc_str(self):
        """
        Extract a length encoded string from the current packet position

        >>> target = "The brown dog did stuff"
        >>> pckt = Proto.build_lenenc_str(target)
        >>> packet = Proto(pckt)
        >>> packet.get_lenenc_str()
        'The brown dog did stuff'
        """
        value = ''
        size = self.get_lenenc_int()

        for i in xrange(self.offset, self.offset + size):
            value += chr(self.packet[i])
            self.offset += 1

        return value

if __name__ == "__main__":
    import doctest
    doctest.testmod()

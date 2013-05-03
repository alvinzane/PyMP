# coding=utf-8

class Proto(object):
    packet = None
    offset = 0
    
    def __init__(self, packet, offset=0):
        self.packet = packet
        self.offset = offset
    
    @staticmethod
    def build_fixed_int(size, value):
        packet = bytearray(size)
        if size >= 1:
            packet[0] = ((value >>  0) & 0xFF);
        if size >= 2:
            packet[1] = ((value >>  8) & 0xFF);
        if size >= 3:
            packet[2] = ((value >> 16) & 0xFF);
        if size >= 4:
            packet[3] = ((value >> 24) & 0xFF);
        if size >= 8:
            packet[4] = ((value >> 32) & 0xFF);
            packet[5] = ((value >> 40) & 0xFF);
            packet[6] = ((value >> 48) & 0xFF);
            packet[7] = ((value >> 56) & 0xFF);
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
            packet[0] = ((value >>  0) & 0xFF)
        elif (value < (2**16 - 1)):
            packet = bytearray(3)
            packet[0] = 0xFC
            packet[1] = ((value >>  0) & 0xFF)
            packet[2] = ((value >>  8) & 0xFF)
        elif (value < (2**24 - 1)):
            packet = bytearray(4)
            packet[0] = 0xFD
            packet[1] = ((value >>  0) & 0xFF)
            packet[2] = ((value >>  8) & 0xFF)
            packet[3] = ((value >> 16) & 0xFF)
        else:
            packet = bytearray(9)
            packet[0] = 0xFE
            packet[1] = ((value >>  0) & 0xFF)
            packet[2] = ((value >>  8) & 0xFF)
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
        if value == "":
            return bytearray(1)
        
        size = Proto.build_lenenc_int(len(value))
        fixed_str = Proto.build_fixed_str(len(value), value)
        return size+fixed_str;
    
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
        return Proto.build_fixed_str(len(value) + 1, value);
    
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
            packet[i] = c;
        return packet;

if __name__ == "__main__":
    import doctest
    doctest.testmod()

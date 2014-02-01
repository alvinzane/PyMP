# coding=utf-8

from proto import Proto
import flags as Flags
import logging


class Packet(object):
    """
    Basic class for all mysql proto classes to inherit from
    """
    __slots__ = ('sequenceId',)

    def __init__(self):
        self.sequenceId = None

    def getPayload(self):
        """
        Return the payload as a bytearray
        """
        raise NotImplementedError('getPayload')

    def toPacket(self):
        """
        Convert a Packet object to a byte array stream
        """
        payload = self.getPayload()

        # Size is payload + packet size + sequence id
        size = len(payload)

        packet = bytearray(size + 4)

        packet[0:2] = Proto.build_fixed_int(3, size)
        packet[3] = Proto.build_fixed_int(1, self.sequenceId)[0]
        packet[4:] = payload

        return packet


def getSize(packet):
    """
    Returns a specified packet size
    """
    return Proto(packet).get_fixed_int(3)


def getType(packet):
    """
    Returns a specified packet type
    """
    return packet[4]


def getSequenceId(packet):
    """
    Returns the Sequence ID for the given packet
    """
    return Proto(packet, 3).get_fixed_int(1)


def dump(packet):
    """
    Dumps a packet to the logger
    """
    logger = logging.getLogger('pymp.engine.packet.dump')
    offset = 0

    if not logger.isEnabledFor(logging.DEBUG):
        return

    dump = 'Packet Dump\n'

    while offset < len(packet):
        dump += hex(offset)[2:].zfill(8).upper()
        dump += '  '

        for x in xrange(16):
            if offset + x >= len(packet):
                dump += '   '
            else:
                dump += hex(packet[offset + x])[2:].upper().zfill(2)
                dump += ' '
                if x == 7:
                    dump += ' '

        dump += '  '

        for x in xrange(16):
            if offset + x >= len(packet):
                break
            c = chr(packet[offset + x])
            if (len(c) > 1
                    or packet[offset + x] < 32
                    or packet[offset + x] == 255):
                dump += '.'
            else:
                dump += c

            if x == 7:
                dump += ' '

        dump += '\n'
        offset += 16

    logger.debug(dump)


def read_packet(socket_in):
    """
    Reads a packet from a socket
    """
    # Read the size of the packet
    psize = bytearray(3)
    socket_in.recv_into(psize, 3)

    size = getSize(psize) + 1

    # Read the rest of the packet
    packet_payload = bytearray(size)
    socket_in.recv_into(packet_payload, size)

    # Combine the chunks
    psize.extend(packet_payload)
    if __debug__:
        dump(psize)

    return psize


def read_full_result_set(socket_in, socket_out, buff, bufferResultSet=True,
                         packedPacketSize=65535,
                         resultsetType=Flags.RS_FULL):
    """
    Reads a full result set
    """
    from colcount import ColCount
    from eof import EOF

    colCount = ColCount.loadFromPacket(buff).colCount

    # Evil optimization
    if not bufferResultSet:
        socket_out.sendall(buff)
        del buff[:]

    # Read columns
    for i in xrange(0, colCount):
        packet = read_packet(socket_in)

        # Evil optimization
        if not bufferResultSet:
            socket_out.sendall(packet)
        else:
            buff.extend(packet)

    # Check for OK or ERR
    # Stop on ERR
    packet = read_packet(socket_in)
    packetType = getType(packet)

    # Evil optimization
    if not bufferResultSet:
        socket_out.sendall(packet)
    else:
        buff.extend(packet)

    # Error? Stop now
    if packetType == Flags.ERR:
        return

    if packetType == Flags.EOF and resultsetType == Flags.RS_HALF:
        return

    # Read rows
    while True:
        packet = read_packet(socket_in)
        packetType = getType(packet)
        if packetType == Flags.EOF:
            moreResults = EOF.loadFromPacket(packet).hasStatusFlag(
                Flags.SERVER_MORE_RESULTS_EXISTS)

        # Evil optimization
        if not bufferResultSet:
            socket_out.sendall(packet)
        else:
            buff.extend(packet)
            if packedPacketSize > 0 and len(buff) > packedPacketSize:
                socket_out.sendall(buff)
                del buff[:]

        if packetType == Flags.EOF or packetType == Flags.ERR:
            break

    # Evil optimization
    if not bufferResultSet:
        socket_out.sendall(buff)
        del buff[:]

    # Show Create Table or similar?
    if packetType == Flags.ERR:
        return

    # Multiple result sets?
    if moreResults:
        buff.extend(
            read_full_result_set(
                socket_in,
                socket_out,
                read_packet(socket_in),
                bufferResultSet=bufferResultSet,
                packedPacketSize=packedPacketSize,
                resultsetType=resultsetType)
        )
    return

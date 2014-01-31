# coding=utf-8

from ..packet import Packet
from ..proto import Proto
from ..flags import Flags


class Quit(Packet):

    def getPayload(self):
        payload = bytearray()

        payload.extend(Proto.build_byte(Flags.COM_QUIT))

        return payload

    @staticmethod
    def loadFromPacket(packet):
        obj = Quit()
        proto = Proto(packet, 3)

        obj.sequenceId = proto.get_fixed_int(1)
        proto.get_filler(1)

        return obj

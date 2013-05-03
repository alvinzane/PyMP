# coding=utf-8

import abc

class Packet(object):
    """
    Basic class for all mysql proto classes to inherit from
    """
    sequenceId = 0;
    
    @abc.abstractmethod
    def getPayload():
        pass
    
    def toPacket():
        pass
    
    def __len__(self):
        pass
    
    
    

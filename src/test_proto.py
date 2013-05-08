#!/usr/bin/env python
# coding=utf-8

import unittest
import optparse
import sys

class TestProto(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def hex_ba(self, string):
        ba = bytearray()
        fields = string.split(' ')
        for field in fields:
            ba_tmp = bytearray(1)
            ba_tmp[0] = int(field, 16)
            ba.extend(ba_tmp)
        return ba
    
    def test_auth_Challenge(self):
        from mysql_proto.auth.challenge import Challenge
        
        packet = bytearray()
        packet.extend(self.hex_ba('36 00 00 00 0a 35 2e 35'))
        packet.extend(self.hex_ba('2e 32 2d 6d 32 00 0b 00'))
        packet.extend(self.hex_ba('00 00 64 76 48 40 49 2d'))
        packet.extend(self.hex_ba('43 4a 00 ff f7 08 02 00'))
        packet.extend(self.hex_ba('00 00 00 00 00 00 00 00'))
        packet.extend(self.hex_ba('00 00 00 00 00 2a 34 64'))
        packet.extend(self.hex_ba('7c 63 5a 77 6b 34 5e 5d'))
        packet.extend(self.hex_ba('3a 00'))
        
        obj = Challenge.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Challenge')
        
    def test_auth_Response(self):
        from mysql_proto.auth.response import Response
        
        packet = bytearray()
        
        # TODO: Get valid packet here
        return
        
        obj = Response.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Response')
        
    def test_COM_QUIT(self):
        from mysql_proto.com.quit import Quit
        
        packet = bytearray()
        packet.extend(self.hex_ba('01 00 00 00 01'))
        
        obj = Quit.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Quit')
    
    def test_COM_INIT_DB(self):
        from mysql_proto.com.initdb import Initdb
        
        packet = bytearray()
        packet.extend(self.hex_ba('05 00 00 00 02 74 65 73'))
        packet.extend(self.hex_ba('74'))
        
        obj = Initdb.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Initdb')
        
    def test_COM_QUERY(self):
        from mysql_proto.com.query import Query
        
        packet = bytearray()
        packet.extend(self.hex_ba('21 00 00 00 03 73 65 6c'))
        packet.extend(self.hex_ba('65 63 74 20 40 40 76 65'))
        packet.extend(self.hex_ba('72 73 69 6f 6e 5f 63 6f'))
        packet.extend(self.hex_ba('6d 6d 65 6e 74 20 6c 69'))
        packet.extend(self.hex_ba('6d 69 74 20 31'))
        
        obj = Query.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Query')
        
    def test_COM_CREATE_DB(self):
        from mysql_proto.com.createdb import Createdb
        
        packet = bytearray()
        packet.extend(self.hex_ba('05 00 00 00 05 74 65 73'))
        packet.extend(self.hex_ba('74'))
        
        obj = Createdb.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Createdb')
        
    def test_COM_DROP_DB(self):
        from mysql_proto.com.dropdb import Dropdb
        
        packet = bytearray()
        packet.extend(self.hex_ba('05 00 00 00 06 74 65 73'))
        packet.extend(self.hex_ba('74'))
        
        obj = Dropdb.loadFromPacket(packet)
        self.assertEqual(obj.toPacket(), packet)
        self.assertEqual(obj.__class__.__name__, 'Dropdb')
        
if __name__ == "__main__":
    # Initialize Options
    parser = optparse.OptionParser()
    
    parser.add_option("-v",
                      "--verbose",
                      dest="verbose",
                      default=1,
                      action="count",
                      help="verbose")

    # Parse Command Line Args
    (options, args) = parser.parse_args()
    
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProto)
    results = unittest.TextTestRunner(verbosity=options.verbose).run(suite)
    
    results = str(results)
    results = results.replace('>', '').split()[1:]
    resobj = {}
    for result in results:
        result = result.split('=')
        resobj[result[0]] = int(result[1])
    
    if resobj['failures'] > 0:
        sys.exit(1)
    if resobj['errors'] > 0:
        sys.exit(2)
    
    sys.exit(0)

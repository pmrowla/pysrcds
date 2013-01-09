# Copyright (C) 2013 Peter Rowlands
#
# Constants and packet formats taken from
# https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
# as of Jan 4 2013
"""Source server RCON communications module"""


from __future__ import division, absolute_import
import struct


# Packet types
SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0


class RconPacket():

    """Source engine RCON packet"""

    pkt_id = 0
    pkt_type = -1
    body = ''
    _PACK_FMT = '<3i'
    _struct = struct.Struct(_PACK_FMT)

    def __init__(self, pkt_id=0, pkt_type=-1, body=''):
        self.pkt_id = pkt_id
        self.pkt_type = pkt_type
        self.body = body

    def __str__(self):
        """Return the body string"""
        return self.body

    def size(self):
        """Return the size of this packet"""
        # Subtract 2 because the size of pkt_size should be discounted, but
        # we also need to account for 2 null-term chars at the end of the
        # packet.
        return self._struct.size() + len(self.body) - 2

    def pack(self):
        """Return the packed version of the packet"""
        header = self._struct.pack(self.size(), self.pkt_id, self.pkt_type)
        return '%s%s\x00\x00' % (header, self.body)

    @classmethod
    def unpack(cls, data):
        """Return a new RconPacket object created from packed data"""
        struct.unpack(cls._PACK_FMT, data[0:struct.calcsize(cls._PACK_FMT)])

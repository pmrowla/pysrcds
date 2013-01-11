# Copyright (C) 2013 Peter Rowlands
"""Source server RCON communications module"""


from __future__ import division, absolute_import
import struct
import socket
import itertools


# Packet types
SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0


class RconPacket(object):

    """RCON packet"""

    _struct = struct.Struct('<3i')

    def __init__(self, pkt_id=0, pkt_type=-1, body=''):
        self.pkt_id = pkt_id
        self.pkt_type = pkt_type
        self.body = body

    def __str__(self):
        """Return the body string"""
        return self.body

    def size(self):
        """Return the pkt_size field for this packet"""
        return len(self.body) + 10

    def pack(self):
        """Return the packed version of the packet"""
        header = self._struct.pack(self.size(), self.pkt_id, self.pkt_type)
        return '%s%s\x00\x00' % (header, self.body)


class RconConnection(object):

    """RCON client to server connection"""

    def __init__(self, server, port=27015, password=''):
        self.server = server
        self.port = port
        self._sock = socket.create_connection((server, port))
        self._authenticate(password)
        self.pkt_id = itertools.count(1)

    def _authenticate(self, password):
        """Authenticate with the server using the given password"""
        auth_pkt = RconPacket(self.pkt_id.next(), SERVERDATA_AUTH, password)
        self._send_pkt(auth_pkt)
        # The server will respond with a SERVERDATA_RESPONSE_VALUE followed by
        # a SERVERDATA_AUTH_RESPONSE
        self.read_response(auth_pkt)
        auth_resp = self.read_response()
        if auth_resp.pkt_type != SERVERDATA_AUTH_RESPONSE:
            raise RconError('Received invalid auth response packet')
        if auth_resp.pkt_id == -1:
            raise RconAuthError('Bad password')

    def exec_command(self, command):
        """Execute the given RCON command

        Return the response body
        """
        cmd_pkt = RconPacket(self.pkt_id.next(), SERVERDATA_EXECCOMMAND,
                             command)
        self._send_pkt(cmd_pkt)
        resp = self.read_response(cmd_pkt, True)
        return resp.body

    def _send_pkt(self, pkt):
        """Send one RCON packet over the connection"""
        if pkt.size() > 4096:
            raise RconSizeError('pkt_size > 4096 bytes')
        data = pkt.pack()
        bytes_sent = 0
        while bytes_sent < len(data):
            bytes_sent += self._sock.send(data[bytes_sent])

    def _recv_pkt(self):
        """Read one RCON packet"""
        header = self._sock.recv(struct.calcsize('<3i'))
        (pkt_size, pkt_id, pkt_type) = struct.unpack('<3i', header)
        body = self._sock.recv(pkt_size - 8)
        # Strip the 2 trailing nulls from the body
        body.rstrip('\x00')
        return RconPacket(pkt_id, pkt_type, body)

    def read_response(self, request=None, multi=False):
        """Return the next response packet"""
        if request and not isinstance(request, RconPacket):
            raise TypeError('Expected RconPacket type for request')
        if multi:
            if not request:
                raise ValueError('Must specify a request packet in order to'
                                 ' read a multi-packet response')
            response = self._read_multi_response(request)
        else:
            response = self._recv_pkt()
        if (response.pkt_type != SERVERDATA_RESPONSE_VALUE and
                response.pkt_type != SERVERDATA_AUTH_RESPONSE):
            raise RconError('Recieved unexpected RCON packet type')
        if request and response.pkt_id != request.pkt_id:
            raise RconError('Response ID does not match request ID')
        return response

    def _read_multi_response(self, req_pkt):
        """Return concatenated multi-packet response"""
        chk_pkt = RconPacket(self.pkt_id.next(), SERVERDATA_RESPONSE_VALUE)
        self._send_pkt(chk_pkt)
        # According to the Valve wiki, a server will mirror a
        # SERVERDATA_RESPONSE_VALUE packet and then send an additional response
        # packet with an empty body. So we should concatenate any packets until
        # we receive a response that matches the ID in chk_pkt
        body_parts = []
        while True:
            response = self._recv_pkt()
            if response.pkt_type != SERVERDATA_RESPONSE_VALUE:
                raise RconError('Received unexpected RCON packet type')
            if response.pkt_id == chk_pkt.pkt_id:
                break
            elif response.pkt_id != req_pkt.pkt_id:
                raise RconError('Response ID does not match request ID')
            body_parts.append(response.body)
        # Read and ignore the extra empty body response
        self._recv_pkt()
        return RconPacket(req_pkt.pkt_id, SERVERDATA_RESPONSE_VALUE,
                          ''.join(body_parts))


class RconError(Exception):
    """Generic RCON error"""
    pass


class RconAuthError(RconError):
    """Raised if an RCON Authentication error occurs"""


class RconSizeError(RconError):
    """Raised when an RCON packet is an illegal size"""
    pass

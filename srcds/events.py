# Copyright (C) 2013 Peter Rowlands
"""
Source server events module

Contains event classes for all standard Source server events.

This module also supports SuperLogs events for the following games:
    CS:S/CS:GO

Complies with the HL Log Standard rev. 1.03

"""

from __future__ import absolute_import
from datetime import datetime

from objects import BasePlayer, SteamId


class BaseEvent(object):

    """Base source event class"""

    def __init__(self, timestamp):
        if not isinstance(timestamp, datetime):
            raise TypeError('Expected datetime instance for timestamp')
        self.timestamp = timestamp


class BaseSuperLogsEvent(BaseEvent):

    """Base SuperLogs event class"""

    def __init__(self, timestamp):
        super(BaseSuperLogsEvent, self).__init__(timestamp)


class CvarEvent(BaseEvent):

    """Cvar change event"""

    def __init__(self, timestamp, cvar='', value='', start=False, end=False):
        super(CvarEvent, self).__init__(timestamp)
        self.cvar = cvar
        self.value = value
        self.start = start
        self.end = end


class LogFileEvent(BaseEvent):

    """Log file change event"""

    def __init__(self, timestamp, filename='', game='', version='',
                 started=False, closed=False):
        super(LogFileEvent, self).__init__(timestamp)
        self.filename = filename
        self.game = game
        self.version = version
        self.started = started
        self.closed = closed


class ChangeMapEvent(BaseEvent):

    """Map change event"""

    def __init__(self, timestamp, mapname, loading=False, started=False,
                 crc=''):
        super(ChangeMapEvent, self).__init__(timestamp)
        self.mapname = mapname
        self.loading = loading
        self.started = started
        self.crc = crc


class RconEvent(BaseEvent):

    """Rcon event"""

    def __init__(self, timestamp, password, address):
        super(RconEvent, self).__init__(timestamp)
        self.password = password
        if not isinstance(tuple, address) or len(address) != 2:
            raise TypeError('Expected 2-tuple (host, port) for address')
        self.address = address


class ConnectionEvent(BaseEvent):

    """Player connection event"""

    def __init__(self, timestamp, player_name, uid, steam_id, address):
        if not isinstance(tuple, address) or len(address) != 2:
            raise TypeError('Expected 2-tuple (host, port) for address')
        super(ConnectionEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, uid, SteamId(steam_id))
        self.address = address


class ValidationEvent(BaseEvent):

    """Player validation event"""

    def __init__(self, timestamp, player_name, uid, steam_id):
        super(ValidationEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, uid, SteamId(steam_id))


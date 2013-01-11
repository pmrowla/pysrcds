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

    def __str__(self):
        """Return a valid HL Log Standard log entry string"""
        return 'L %s:' % (self.timestamp_to_str(self.timestamp))

    @classmethod
    def timestamp_to_str(cls, timestamp):
        """Return a valid HL Log Standard timestamp string"""
        if not isinstance(timestamp, datetime):
            raise TypeError('Expected datetime instance for timestamp')
        return timestamp.strftime('%m/%d/%Y - %H:%M:%S')


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

    def __str__(self):
        if self.start:
            msg = 'Server cvars start'
        elif self.end:
            msg = 'Server cvars end'
        else:
            msg = 'Server cvar "%s" = "%s"' % (self.cvar, self.value)
        return ' '.join([super(CvarEvent, self).__str__(), msg])


class LogFileEvent(BaseEvent):

    """Log file change event"""

    def __init__(self, timestamp, filename='', game='', version='',
                 started=False, closed=False):
        if not started != closed:
            raise ValueError('Invalid event')
        super(LogFileEvent, self).__init__(timestamp)
        self.filename = filename
        self.game = game
        self.version = version
        self.started = started
        self.closed = closed

    def __str__(self):
        if self.started:
            msg = 'Log file started (file "%s") (game "%s") (version "%s")' % (
                self.filename, self.game, self.version)
        else:
            msg = 'Log file closed'
        return ' '.join([super(LogFileEvent, self).__str__(), msg])


class ChangeMapEvent(BaseEvent):

    """Map change event"""

    def __init__(self, timestamp, mapname, loading=False, started=False,
                 crc=''):
        if not loading != started:
            raise ValueError('Invalid event')
        super(ChangeMapEvent, self).__init__(timestamp)
        self.mapname = mapname
        self.loading = loading
        self.started = started
        self.crc = crc

    def __str__(self):
        if self.loading:
            msg = 'Loading map "%s"' % (self.mapname)
        else:
            msg = 'Started map "%s" (CRC "%s")' % (self.mapname, self.crc)
        return ' '.join([super(ChangeMapEvent, self).__str__(), msg])


class RconEvent(BaseEvent):

    """Rcon event"""

    def __init__(self, timestamp, password, address, passed=False):
        super(RconEvent, self).__init__(timestamp)
        self.password = password
        if not isinstance(tuple, address) or len(address) != 2:
            raise TypeError('Expected 2-tuple (host, port) for address')
        self.address = address
        self.passed = passed

    def __str__(self):
        if self.passed:
            msg = 'Rcon: "rcon challenge "%s" command" from "%s:%d"' % (
                self.password, self.address[0], self.address[1])
        else:
            msg = 'Bad Rcon: "rcon challenge "%s" command" from "%s:%d"' % (
                self.password, self.address[0], self.address[1])
        return ' '.join([super(RconEvent, self).__str__(), msg])


class PlayerActionEvent(BaseEvent):

    """Base class for events involving a single player"""

    def __init__(self, timestamp, player_name, uid, steam_id, team=''):
        super(PlayerActionEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, uid, SteamId(steam_id), team)

    def __str__(self):
        msg = '"%s<%d><%s><%s>"' % (self.player.name, self.player.uid,
                                    self.player.steam_id, self.player.team)
        return ' '.join([super(PlayerActionEvent, self).__str__(), msg])


class ConnectionEvent(PlayerActionEvent):

    """Player connection event"""

    def __init__(self, timestamp, player_name, uid, steam_id, address):
        if not isinstance(tuple, address) or len(address) != 2:
            raise TypeError('Expected 2-tuple (host, port) for address')
        super(ConnectionEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id)
        self.address = address

    def __str__(self):
        msg = 'connected, address "%s:%d"' % (self.address[0], self.address[1])
        return ' '.join([super(ConnectionEvent, self).__str__(), msg])


class ValidationEvent(PlayerActionEvent):

    """Player validation event"""

    def __str__(self):
        msg = 'STEAM USERID validated'
        return ' '.join([super(ValidationEvent, self).__str__(), msg])


class EnterGameEvent(PlayerActionEvent):

    """Player entered game event"""

    def __str__(self):
        msg = 'entered the game'
        return ' '.join([super(EnterGameEvent, self).__str__(), msg])


class DisconnectionEvent(PlayerActionEvent):

    """Player disconnected event"""

    def __str__(self):
        msg = 'disconnected'
        return ' '.join([super(DisconnectionEvent, self).__str__(), msg])


class KickEvent(PlayerActionEvent):

    """Player kicked by console event"""

    def __init__(self, timestamp, player_name, uid, steam_id, message):
        super(KickEvent, self).__init__(timestamp, player_name, uid,
                                        steam_id)
        self.message = message

    def __str__(self):
        return ' '.join([
            'L %s:' % (self.timestamp_to_str(self.timestamp)),
            'Kick: "%s<%d><%s><%s>"' % (self.player.name, self.player.uid,
                                        self.player.steam_id,
                                        self.player.team),
            'was kicked by "Console" (message "%s")' % (self.message)
        ])


class SuicideEvent(PlayerActionEvent):

    """Player suicide event"""

    def __init__(self, timestamp, player_name, uid, steam_id, team, weapon):
        super(SuicideEvent, self).__init__(timestamp, player_name, uid,
                                           steam_id, team)
        self.weapon = weapon

    def __str__(self):
        msg = 'committed suicide with "%s"' % (self.weapon)
        return ' '.join([super(SuicideEvent, self).__str__(), msg])


class TeamSelectionEvent(PlayerActionEvent):

    """Player team select event"""

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 new_team):
        super(TeamSelectionEvent, self).__init__(timestamp, player_name, uid,
                                                 steam_id, team)
        self.new_team = new_team

    def __str__(self):
        msg = 'joined team "%s"' % (self.new_team)
        return ' '.join([super(TeamSelectionEvent, self).__str__(), msg])


class RoleSelectionEvent(PlayerActionEvent):

    """Player role select event"""

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 role):
        super(RoleSelectionEvent, self).__init__(timestamp, player_name, uid,
                                                 steam_id, team)
        self.role = role

    def __str__(self):
        msg = 'changed role to "%s"' % (self.role)
        return ' '.join([super(RoleSelectionEvent, self).__str__(), msg])


class ChangeNameEvent(PlayerActionEvent):

    """Player name changed event"""

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 new_name):
        super(ChangeNameEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id, team)
        self.new_name = new_name

    def __str__(self):
        msg = 'changed name to "%s"' % (self.new_name)
        return ' '.join([super(ChangeNameEvent, self).__str__(), msg])

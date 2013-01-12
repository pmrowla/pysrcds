# Copyright (C) 2013 Peter Rowlands
"""
Source server objects module

Contains base classes for all standard Source server objects.

"""


from __future__ import division
import re


STEAM_ACCOUNT_UNIVERSE = {
    'individual': 0,
    'public': 1,
    'beta': 2,
    'internal': 3,
    'dev': 4,
    'rc': 5,
}

STEAM_ACCOUNT_TYPE = {
    'invalid': 0,
    'individual': 1,
    'multiseat': 2,
    'gameserver': 3,
    'anongameserver': 4,
    'pending': 5,
    'contentserver': 6,
    'clan': 7,
    'chat': 8,
    'p2p_superseeder': 9,
    'anonuser': 10,
}


class SteamId(object):

    """Steam ID class"""

    def __init__(self, steam_id):
        """Initialize a SteamId object

        Args:
            steam_id: A valid SteamID. Accepts a string in STEAM_X:Y:Z format,
                or as a 64-bit integer.

        """
        self.is_bot = False
        self.is_console = False
        if isinstance(steam_id, int):
            (self.id_number,
             self.instance,
             self.id_type,
             self.universe) = self.split_id64(steam_id)
        elif not isinstance(steam_id, str):
            raise TypeError('Invalid type for steam_id')
        else:
            if steam_id == 'BOT':
                self.is_bot = True
            elif steam_id == 'Console':
                self.is_console == True
            else:
                pattern = ''.join([
                    r'STEAM_(?P<universe>[0-5]):(?P<id_type>\d+):',
                    r'(?P<id_number>\d+)',
                ])
                match = re.match(pattern, steam_id, re.I)
                if not match:
                    raise ValueError('Invalid string steam_id: %s' % steam_id)
                self.universe = int(match.groupdict()['universe'])
                self.instance = 1
                self.id_type = int(match.groupdict()['id_type'])
                self.id_number = int(match.groupdict()['id_number'])

    def __str__(self):
        if self.is_bot:
            return 'BOT'
        elif self.is_console:
            return 'Console'
        else:
            return self.id64_to_str(self.id64())

    def id64(self):
        """Return the SteamID64 for this ID"""
        if self.is_bot or self.is_console:
            return 0
        id64 = self.id_number
        id64 |= self.instance << 32
        id64 |= self.id_type << 52
        id64 |= self.universe << 56
        return id64

    @classmethod
    def id64_to_str(cls, id64, universe=STEAM_ACCOUNT_UNIVERSE['public']):
        """Convert a SteamID64 to a STEAM_X:Y:Z string"""
        y_part = id64 >> 52 & 0xf
        z_part = id64 & 0xffffffff
        x_part = universe
        return 'STEAM_%d:%d:%d' % (x_part, y_part, z_part)

    @classmethod
    def split_id64(cls, id64):
        """Return a tuple of (id, instance, type, universe)"""
        id_number = id64 & 0xffffffff
        instance = id64 & 0x000fffff00000000
        id_type = id64 & 0x00f0000000000000
        universe = id64 & 0xff00000000000000
        return (id_number, instance, id_type, universe)


class BasePlayer(object):

    """Source player object"""

    def __init__(self, name, uid, steam_id, team=''):
        if not isinstance(steam_id, SteamId):
            raise TypeError('Expected type SteamId for steam_id')
        self.name = name
        if isinstance(uid, str):
            uid = int(uid)
        self.uid = uid
        self.steam_id = steam_id
        self.team = team

    def __str__(self):
        msg = [
            self.name,
            '<%d>' % self.uid,
            '<%s>' % self.steam_id,
        ]
        if self.team is not None:
            msg.append('<%s>' % self.team)
        return ''.join(msg)

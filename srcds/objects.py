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
        if isinstance(steam_id, int):
            (self.id_number,
             self.instance,
             self.id_type,
             self.universe) = self.split_id64(steam_id)
        elif not isinstance(steam_id, str):
            raise TypeError('Invalid type for steam_id')
        else:
            match = re.match(r'STEAM_([0-5]):[0-1]:(\d+)', steam_id, re.I)
            if not match:
                raise ValueError('Invalid string steam_id')
            self.universe = int(match.group(0))
            self.instance = 1   # Valve wiki says this is 1 for user accounts
            self.id_type = STEAM_ACCOUNT_TYPE['individual']
            self.id_number = int(match.group(1))

    def __str__(self):
        return self.id64_to_str(self.id64())

    def id64(self):
        """Return the SteamID64 for this ID"""
        id64 = self.id_type
        id64 |= self.instance << 32
        id64 |= self.id_type << 52
        id64 |= self.universe << 56
        return id64

    @classmethod
    def id64_to_str(cls, id64, universe=STEAM_ACCOUNT_UNIVERSE['public']):
        """Convert a SteamID64 to a STEAM_X:Y:Z string"""
        y = id64 % 2
        z = ((id64 & 0xffffffff) - y) // 2
        x = universe
        return 'STEAM_%d:%d:%d' % (x, y, z)

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
        self.uid = uid
        self.steam_id = steam_id
        self.team = team

    def __str__(self):
        return "%s<%d><%s><%s>" % (self.name, self.uid, self.steam_id,
                                   self.team)

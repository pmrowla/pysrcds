# Copyright (C) 2013 Peter Rowlands
"""
Source server objects module

Contains base classes for all standard Source server objects.

"""

from __future__ import division, unicode_literals
from future.utils import python_2_unicode_compatible

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


@python_2_unicode_compatible
class SteamId(object):

    """Steam ID class"""

    def __init__(self, steam_id, id_type=STEAM_ACCOUNT_TYPE['individual']):
        """Initialize a SteamId object

        Args:
            steam_id: A valid SteamID. Accepts a string in STEAM_X:Y:Z format,
                or as a 64-bit integer.

        """
        self.is_bot = False
        self.is_console = False
        if isinstance(steam_id, int):
            (self.id_number,
             self.y_part,
             self.instance,
             self.id_type,
             self.universe) = self.split_id64(steam_id)
        else:
            if str(steam_id) == u'BOT':
                self.is_bot = True
            elif str(steam_id) == u'Console':
                self.is_console = True
            else:
                pattern = ''.join([
                    r'STEAM_(?P<universe>[0-5]):(?P<y_part>\d+):',
                    r'(?P<id_number>\d+)',
                ])
                match = re.match(pattern, steam_id, re.I | re.U)
                if not match:
                    raise ValueError('Invalid string steam_id: %s' % steam_id)
                self.universe = int(match.groupdict()['universe'])
                self.instance = 1
                self.y_part = int(match.groupdict()['y_part'])
                self.id_number = int(match.groupdict()['id_number'])
                self.id_type = id_type

    def __str__(self):
        if self.is_bot:
            return u'BOT'
        elif self.is_console:
            return u'Console'
        else:
            return self.id64_to_str(self.id64())

    def id64(self):
        """Return the SteamID64 for this ID"""
        if self.is_bot or self.is_console:
            return 0
        id64 = self.id_number * 2
        id64 += self.y_part
        id64 |= self.instance << 32
        id64 |= self.id_type << 52
        id64 |= self.universe << 56
        return id64

    @classmethod
    def id64_to_str(cls, id64, universe=STEAM_ACCOUNT_UNIVERSE['public']):
        """Convert a SteamID64 to a STEAM_X:Y:Z string"""
        (id_number, y_part, instance, id_type, universe) = SteamId.split_id64(id64)
        return u'STEAM_%d:%d:%d' % (universe, y_part, id_number)

    @classmethod
    def split_id64(cls, id64):
        """Return a tuple of (id, y_part, instance, type, universe)"""
        y_part = id64 % 2
        id_number = (id64 & 0xffffffff - y_part) // 2
        instance = (id64 & 0x000fffff00000000) >> 32
        id_type = (id64 & 0x00f0000000000000) >> 52
        universe = (id64 & 0xff00000000000000) >> 56
        return (id_number, y_part, instance, id_type, universe)


@python_2_unicode_compatible
class BasePlayer(object):

    """Source player object"""

    def __init__(self, name, uid, steam_id, team=u''):
        if not isinstance(steam_id, SteamId):
            raise TypeError('Expected type SteamId for steam_id')
        self.name = name
        self.uid = int(uid)
        self.steam_id = steam_id
        if team is None:
            team = u''
        self.team = team

    def __str__(self):
        msg = [
            self.name,
            '<%d>' % self.uid,
            '<%s>' % self.steam_id,
        ]
        if self.team is not None:
            msg.append(u'<%s>' % self.team)
        return ''.join(msg)

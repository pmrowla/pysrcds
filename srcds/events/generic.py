# Copyright (C) 2013 Peter Rowlands
"""Generic Source engine events module

Contains event classes for all standard HL/Source server events.

Complies with the HL Log Standard rev. 1.03

"""

from __future__ import absolute_import
from datetime import datetime
import re

from ..objects import BasePlayer, SteamId


class BaseEvent(object):

    """Base source event class"""

    regex = ''.join([
        ur'^L (?P<timestamp>(0[0-9]|1[0-2])/([0-2][0-9]|3[0-1])/\d{4} - ',
        ur'([0-1][0-9]|2[0-3])(:[0-5][0-9]|60){2}):\s*',
    ])

    def __init__(self, timestamp):
        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        elif isinstance(timestamp, str) or isinstance(timestamp, unicode):
            self.timestamp = datetime.strptime(timestamp,
                                               '%m/%d/%Y - %H:%M:%S')
        else:
            raise TypeError('Unexpected type for timestamp')

    def __str__(self):
        """Return a valid HL Log Standard log entry string"""
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'L %s:' % (self.timestamp_to_str(self.timestamp))

    @classmethod
    def timestamp_to_str(cls, timestamp):
        """Return a valid HL Log Standard timestamp string"""
        if not isinstance(timestamp, datetime):
            raise TypeError('Expected datetime instance for timestamp')
        return timestamp.strftime('%m/%d/%Y - %H:%M:%S')

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        return cls(**match.groupdict())


class CvarEvent(BaseEvent):

    """Cvar change event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Server (cvars (start|end)|cvar "(?P<cvar>\w*)" = "(?P<value>\w*)")',
    ])

    def __init__(self, timestamp, cvar='', value='', start=False, end=False):
        super(CvarEvent, self).__init__(timestamp)
        self.cvar = cvar
        self.value = value
        self.start = start
        self.end = end

    def __unicode__(self):
        if self.start:
            msg = u'Server cvars start'
        elif self.end:
            msg = u'Server cvars end'
        else:
            msg = u'Server cvar "%s" = "%s"' % (self.cvar, self.value)
        return u' '.join([super(CvarEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.find('start') >= 0:
            kwargs['start'] = True
        elif match.string.find('end') >= 0:
            kwargs['end'] = True
        return cls(**kwargs)


class LogFileEvent(BaseEvent):

    """Log file change event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Log file (closed|started \(file "(?P<filename>.*)"\) ',
        ur'\(game "(?P<game>.*)"\) \(version "(?P<version>.*)"\))',
    ])

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

    def __unicode__(self):
        if self.started:
            msg = u'Log file started (file "%s") (game "%s") (version "%s")' % (
                self.filename, self.game, self.version)
        else:
            msg = u'Log file closed'
        return u' '.join([super(LogFileEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.endswith('closed'):
            kwargs['closed'] = True
        else:
            kwargs['started'] = True
        return cls(**kwargs)


class ChangeMapEvent(BaseEvent):

    """Map change event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'(Loading|Started) map "(?P<mapname>.*?)"( \(CRC "(?P<crc>-?\d+)"\))?',
    ])

    def __init__(self, timestamp, mapname, loading=False, started=False,
                 crc=''):
        if not loading != started:
            raise ValueError('Invalid event')
        super(ChangeMapEvent, self).__init__(timestamp)
        self.mapname = mapname
        self.loading = loading
        self.started = started
        self.crc = crc

    def __unicode__(self):
        if self.loading:
            msg = u'Loading map "%s"' % (self.mapname)
        else:
            msg = u'Started map "%s" (CRC "%s")' % (self.mapname, self.crc)
        return ' '.join([super(ChangeMapEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.startswith('Loading'):
            kwargs['loading'] = True
        else:
            kwargs['started'] = True
        return cls(**kwargs)


class RconEvent(BaseEvent):

    """Rcon event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'(Bad )?Rcon: "rcon challenge "(?P<password>\w*)" from ',
        ur'"(?P<host>\w*):(?P<port>\d{0-5})"',
    ])

    def __init__(self, timestamp, password, address, passed=False):
        super(RconEvent, self).__init__(timestamp)
        self.password = password
        if not isinstance(tuple, address) or len(address) != 2:
            raise TypeError('Expected 2-tuple (host, port) for address')
        self.address = address
        self.passed = passed

    def __unicode__(self):
        if self.passed:
            msg = u'Rcon: "rcon challenge "%s" command" from "%s:%d"' % (
                self.password, self.address[0], self.address[1])
        else:
            msg = u'Bad Rcon: "rcon challenge "%s" command" from "%s:%d"' % (
                self.password, self.address[0], self.address[1])
        return ' '.join([super(RconEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if not match.string.startswith('Bad'):
            kwargs['passed'] = True
        return cls(**kwargs)


class PlayerEvent(BaseEvent):

    """Base class for events involving a single player"""

    regex = ''.join([
        BaseEvent.regex,
        ur'"(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>',
        ur'<(?P<team>\w*)>"\s*',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team=''):
        super(PlayerEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, uid, SteamId(steam_id), team)

    def __unicode__(self):
        msg = u'"%s"' % self.player
        return u' '.join([super(PlayerEvent, self).__unicode__(), msg])


class ConnectionEvent(PlayerEvent):

    """Player connection event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'connected, address "((?P<address>none)|(?P<host>\d+(\.\d+){3}):(?P<port>\d*))"'
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, address):
        if (address == 'none' or
                (isinstance(address, tuple) and len(address) == 2)):
            self.address = address
        else:
            raise TypeError('Expected 2-tuple (host, port) for address: %s', address)
        super(ConnectionEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id, team)

    def __unicode__(self):
        if isinstance(self.address, tuple):
            msg = u'connected, address "%s:%d"' % (self.address[0],
                                                  self.address[1])
        else:
            msg = u'connected, address "%s"' % (self.address)
        return u' '.join([super(ConnectionEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if kwargs['address'] != 'none':
            kwargs['address'] = (kwargs['host'], int(kwargs['port']))
        del kwargs['host']
        del kwargs['port']
        return cls(**kwargs)


class ValidationEvent(PlayerEvent):

    """Player validation event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'STEAM USERID validated',
    ])

    def __unicode__(self):
        msg = u'STEAM USERID validated'
        return u' '.join([super(ValidationEvent, self).__unicode__(), msg])


class EnterGameEvent(PlayerEvent):

    """Player entered game event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'entered the game',
    ])

    def __unicode__(self):
        msg = u'entered the game'
        return u' '.join([super(EnterGameEvent, self).__unicode__(), msg])


class DisconnectionEvent(PlayerEvent):

    """Player disconnected event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'disconnected',
    ])

    def __unicode__(self):
        msg = u'disconnected'
        return u' '.join([super(DisconnectionEvent, self).__unicode__(), msg])


class KickEvent(PlayerEvent):

    """Player kicked by console event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Kick: "(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>',
        ur'<(?P<team>\w*)>" was kicked by "Console" ',
        ur'\(message "(?P<message>.*)"\)',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, message):
        super(KickEvent, self).__init__(timestamp, player_name, uid,
                                        steam_id, team)
        self.message = message

    def __unicode__(self):
        return ' '.join([
            u'L %s:' % (self.timestamp_to_str(self.timestamp)),
            u'Kick: "%s"' % (self.player),
            u'was kicked by "Console" (message "%s")' % (self.message),
        ])


class SuicideEvent(PlayerEvent):

    """Player suicide event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'committed suicide with "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, weapon):
        super(SuicideEvent, self).__init__(timestamp, player_name, uid,
                                           steam_id, team)
        self.weapon = weapon

    def __unicode__(self):
        msg = u'committed suicide with "%s"' % (self.weapon)
        return u' '.join([super(SuicideEvent, self).__unicode__(), msg])


class TeamSelectionEvent(PlayerEvent):

    """Player team select event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'joined team "(?P<new_team>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 new_team):
        super(TeamSelectionEvent, self).__init__(timestamp, player_name, uid,
                                                 steam_id, team)
        self.new_team = new_team

    def __unicode__(self):
        msg = u'joined team "%s"' % (self.new_team)
        return u' '.join([super(TeamSelectionEvent, self).__unicode__(), msg])


class RoleSelectionEvent(PlayerEvent):

    """Player role select event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'changed role to "(?P<role>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 role):
        super(RoleSelectionEvent, self).__init__(timestamp, player_name, uid,
                                                 steam_id, team)
        self.role = role

    def __unicode__(self):
        msg = u'changed role to "%s"' % (self.role)
        return u' '.join([super(RoleSelectionEvent, self).__unicode__(), msg])


class ChangeNameEvent(PlayerEvent):

    """Player name changed event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'changed name to "(?P<new_name>.*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 new_name):
        super(ChangeNameEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id, team)
        self.new_name = new_name

    def __unicode__(self):
        msg = u'changed name to "%s"' % (self.new_name)
        return u' '.join([super(ChangeNameEvent, self).__unicode__(), msg])


class PlayerTargetEvent(BaseEvent):

    """Base class for events involving two players"""

    player_regex = ''.join([
        ur'"(?P<player_name>.*)<(?P<player_uid>\d*)>',
        ur'<(?P<player_steam_id>[\w:]*)><(?P<player_team>\w*)>"\s*',
    ])
    target_regex = ''.join([
        ur'"(?P<target_name>.*)<(?P<target_uid>\d*)>',
        ur'<(?P<target_steam_id>[\w:]*)><(?P<target_team>\w*)>"\s*',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team):
        super(PlayerTargetEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, player_uid,
                                 SteamId(player_steam_id), player_team)
        self.target = BasePlayer(target_name, target_uid,
                                 SteamId(target_steam_id), target_team)


class KillEvent(PlayerTargetEvent):

    """Player killed event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        ur' killed ',
        PlayerTargetEvent.target_regex,
        ur' with "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team, weapon):
        super(KillEvent, self).__init__(timestamp, player_name, player_uid,
                                        player_steam_id, player_team,
                                        target_name, target_uid,
                                        target_steam_id, target_team)
        self.weapon = weapon

    def __unicode__(self):
        msg = u'"%s" killed "%s" with "%s"' % (self.player, self.target,
                                              self.weapon)
        return u' '.join([super(KillEvent, self).__unicode__(), msg])


class AttackEvent(PlayerTargetEvent):

    """Player attacked event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        ur' attacked ',
        PlayerTargetEvent.target_regex,
        ur' with "(?P<weapon>\w*)" \(damage "(?P<damage>\d*)"\)',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team, weapon, damage):
        super(AttackEvent, self).__init__(timestamp, player_name, player_uid,
                                          player_steam_id, player_team,
                                          target_name, target_uid,
                                          target_steam_id, target_team)
        self.weapon = weapon
        self.damage = int(damage)

    def __unicode__(self):
        msg = u'"%s" attacked "%s" with "%s" (damage "%d")' % (self.player,
                                                               self.target,
                                                               self.weapon,
                                                               self.damage)
        return u' '.join([super(AttackEvent, self).__unicode__(), msg])


class PlayerActionEvent(PlayerEvent):

    """Player triggered action event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'triggered "(?P<action>.*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 action):
        super(PlayerActionEvent, self).__init__(timestamp, player_name, uid,
                                                steam_id, team)
        self.action = action

    def __unicode__(self):
        msg = u'triggered "%s"' % (self.action)
        return u' '.join([super(PlayerActionEvent, self).__unicode__(), msg])


class TeamActionEvent(BaseEvent):

    """Team triggered action event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Team "(?P<team>\w*?)" triggered "(?P<action>.*?)"',
    ])

    def __init__(self, timestamp, team, action):
        super(TeamActionEvent, self).__init__(timestamp)
        self.team = team
        self.action = action

    def __unicode__(self):
        msg = u'Team "%s" triggered "%s"' % (self.team, self.action)
        return u' '.join([super(TeamActionEvent, self).__unicode__(), msg])


class WorldActionEvent(BaseEvent):

    """World triggered action event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'World triggered "(?P<action>.*?)"',
    ])

    def __init__(self, timestamp, action):
        super(WorldActionEvent, self).__init__(timestamp)
        self.action = action

    def __unicode__(self):
        msg = u'World triggered "%s"' % (self.action)
        return u' '.join([super(WorldActionEvent, self).__unicode__(), msg])


class ChatEvent(PlayerEvent):

    """Chat event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'say(_team)? "(?P<message>.*?)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 message, say_team=False):
        super(ChatEvent, self).__init__(timestamp, player_name, uid, steam_id,
                                        team)
        self.say_team = say_team
        self.message = message

    def __unicode__(self):
        if self.say_team:
            msg = u'say_team "%s"' % (self.message)
        else:
            msg = u'say "%s"' % (self.message)
        return u' '.join([super(ChatEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.find('say_team') >= 0:
            kwargs['say_team'] = True
        return cls(**kwargs)


class TeamAllianceEvent(BaseEvent):

    """Team alliance event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Team "(?P<team_a>\w*?)" formed alliance with "(?P<team_b>\w*?)"',
    ])

    def __init__(self, timestamp, team_a, team_b):
        super(TeamAllianceEvent, self).__init__(timestamp)
        self.team_a = team_a
        self.team_b = team_b

    def __unicode__(self):
        msg = u'Team "%s" formed alliance with "%s"' % (self.team_a,
                                                       self.team_b)
        return u' '.join([super(TeamAllianceEvent, self).__unicode__(), msg])


class RoundEndTeamEvent(BaseEvent):

    """Round end team score report event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Team "(?P<team>\w*?)" scored "(?P<score>\d+)" with ',
        ur'"(?P<num_players>\d+)" players',
    ])

    def __init__(self, timestamp, team, score, num_players):
        super(RoundEndTeamEvent, self).__init__(timestamp)
        self.team = team
        self.score = int(score)
        self.num_players = int(num_players)

    def __unicode__(self):
        msg = u'Team "%s" scored "%d" with "%d" players' % (self.team,
                                                           self.score,
                                                           self.num_players)
        return u' '.join([super(RoundEndTeamEvent, self).__unicode__(), msg])


class PrivateChatEvent(PlayerTargetEvent):

    """Private Chat event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        ur' tell ',
        PlayerTargetEvent.target_regex,
        ur' message "(?P<message>.*)"',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team, message):
        super(PrivateChatEvent, self).__init__(timestamp, player_name,
                                               player_uid, player_steam_id,
                                               player_team, target_name,
                                               target_uid, target_steam_id,
                                               target_team)
        self.message = message

    def __unicode__(self):
        msg = u'"%s" tell "%s" message "%s"' % (self.player, self.target,
                                               self.message)
        return u' '.join([super(PrivateChatEvent, self).__unicode__(), msg])


class RoundEndPlayerEvent(PlayerEvent):

    """Round end player score report event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'Player "(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>',
        ur'<(?P<team>\w*)>"\s*',
        ur'scored "(?P<score>\d+)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, score):
        super(RoundEndPlayerEvent, self).__init__(timestamp, player_name, uid,
                                                  steam_id, team)
        self.score = int(score)

    def __unicode__(self):
        return u' '.join([
            u'L %s:' % (self.timestamp_to_str(self.timestamp)),
            u'Player "%s"' % (self.player),
            u'scored "%d"' % (self.score),
        ])


class WeaponSelectEvent(PlayerEvent):

    """Player selected weapon event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'selected weapon "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 weapon):
        super(WeaponSelectEvent, self).__init__(timestamp, player_name, uid,
                                                steam_id, team)
        self.weapon = weapon

    def __unicode__(self):
        msg = 'selected weapon "%s"' % (self.weapon)
        return ' '.join([super(WeaponSelectEvent, self).__unicode__(), msg])


class WeaponPickupEvent(PlayerEvent):

    """Player picked up weapon event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'acquired weapon "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 weapon):
        super(WeaponPickupEvent, self).__init__(timestamp, player_name, uid,
                                                steam_id, team)
        self.weapon = weapon

    def __unicode__(self):
        msg = u'acquired weapon "%s"' % (self.weapon)
        return u' '.join([super(WeaponPickupEvent, self).__unicode__(), msg])


STANDARD_EVENTS = [
    CvarEvent,
    LogFileEvent,
    ChangeMapEvent,
    RconEvent,
    ConnectionEvent,
    ValidationEvent,
    EnterGameEvent,
    DisconnectionEvent,
    KickEvent,
    SuicideEvent,
    TeamSelectionEvent,
    RoleSelectionEvent,
    ChangeNameEvent,
    KillEvent,
    AttackEvent,
    PlayerActionEvent,
    TeamActionEvent,
    WorldActionEvent,
    ChatEvent,
    TeamAllianceEvent,
    RoundEndTeamEvent,
    PrivateChatEvent,
    RoundEndPlayerEvent,
    WeaponSelectEvent,
    WeaponPickupEvent,
]

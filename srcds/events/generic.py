# Copyright (C) 2013 Peter Rowlands
"""Generic Source engine events module

Contains event classes for all standard HL/Source server events.

Complies with the HL Log Standard rev. 1.03

"""
from __future__ import absolute_import, unicode_literals
from future.utils import python_2_unicode_compatible

from datetime import datetime

from ..objects import BasePlayer, SteamId


@python_2_unicode_compatible
class BaseEvent(object):

    """Base source event class"""

    regex = ''.join([
        r'^L (?P<timestamp>(0[0-9]|1[0-2])/([0-2][0-9]|3[0-1])/\d{4} - ',
        r'([0-1][0-9]|2[0-3])(:[0-5][0-9]|60){2}):\s*',
    ])

    def __init__(self, timestamp):
        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.strptime(timestamp,
                                               '%m/%d/%Y - %H:%M:%S')

    def text(self):
        """Return a valid HL Log Standard log entry string"""
        return 'L {}:'.format(self.timestamp_to_str(self.timestamp))

    __str__ = text

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


@python_2_unicode_compatible
class CvarEvent(BaseEvent):

    """Cvar change event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Server (cvars (start|end)|cvar "(?P<cvar>\w*)" = "(?P<value>\w*)")',
    ])

    def __init__(self, timestamp, cvar='', value='', start=False, end=False):
        super(CvarEvent, self).__init__(timestamp)
        self.cvar = cvar
        self.value = value
        self.start = start
        self.end = end

    def text(self):
        if self.start:
            msg = 'Server cvars start'
        elif self.end:
            msg = 'Server cvars end'
        else:
            msg = 'Server cvar "%s" = "%s"' % (self.cvar, self.value)
        return ' '.join([super(CvarEvent, self).text(), msg])

    __str__ = text

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.find('start') >= 0:
            kwargs['start'] = True
        elif match.string.find('end') >= 0:
            kwargs['end'] = True
        return cls(**kwargs)


@python_2_unicode_compatible
class LogFileEvent(BaseEvent):

    """Log file change event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Log file (closed|started \(file "(?P<filename>.*)"\) ',
        r'\(game "(?P<game>.*)"\) \(version "(?P<version>.*)"\))',
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

    def text(self):
        if self.started:
            msg = 'Log file started (file "%s") (game "%s") (version "%s")' % (
                self.filename, self.game, self.version)
        else:
            msg = 'Log file closed'
        return ' '.join([super(LogFileEvent, self).text(), msg])

    __str__ = text

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.endswith('closed'):
            kwargs['closed'] = True
        else:
            kwargs['started'] = True
        return cls(**kwargs)


@python_2_unicode_compatible
class ChangeMapEvent(BaseEvent):

    """Map change event"""

    regex = ''.join([
        BaseEvent.regex,
        r'(Loading|Started) map "(?P<mapname>.*?)"( \(CRC "(?P<crc>-?\d+)"\))?',
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

    def text(self):
        if self.loading:
            msg = 'Loading map "%s"' % (self.mapname)
        else:
            msg = 'Started map "%s" (CRC "%s")' % (self.mapname, self.crc)
        return ' '.join([super(ChangeMapEvent, self).text(), msg])

    __str__ = text

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.startswith('Loading'):
            kwargs['loading'] = True
        else:
            kwargs['started'] = True
        return cls(**kwargs)


@python_2_unicode_compatible
class RconEvent(BaseEvent):

    """Rcon event"""

    regex = ''.join([
        BaseEvent.regex,
        r'(Bad )?Rcon: "rcon challenge "(?P<password>\w*)" from ',
        r'"(?P<host>\w*):(?P<port>\d{0-5})"',
    ])

    def __init__(self, timestamp, password, address, passed=False):
        super(RconEvent, self).__init__(timestamp)
        self.password = password
        if not isinstance(tuple, address) or len(address) != 2:
            raise TypeError('Expected 2-tuple (host, port) for address')
        self.address = address
        self.passed = passed

    def text(self):
        if self.passed:
            msg = 'Rcon: "rcon challenge "%s" command" from "%s:%d"' % (
                self.password, self.address[0], self.address[1])
        else:
            msg = 'Bad Rcon: "rcon challenge "%s" command" from "%s:%d"' % (
                self.password, self.address[0], self.address[1])
        return ' '.join([super(RconEvent, self).text(), msg])

    __str__ = text

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if not match.string.startswith('Bad'):
            kwargs['passed'] = True
        return cls(**kwargs)


@python_2_unicode_compatible
class PlayerEvent(BaseEvent):

    """Base class for events involving a single player"""

    regex = ''.join([
        BaseEvent.regex,
        r'"(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>',
        r'<(?P<team>\w*)>"\s*',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team=''):
        super(PlayerEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, uid, SteamId(steam_id), team)

    def text(self):
        msg = '"%s"' % self.player
        return ' '.join([super(PlayerEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class ConnectionEvent(PlayerEvent):

    """Player connection event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'connected, address "((?P<address>none)|(?P<host>\d+(\.\d+){3}):(?P<port>\d*))"'
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, address):
        if (address == 'none' or
                (isinstance(address, tuple) and len(address) == 2)):
            self.address = address
        else:
            raise TypeError('Expected 2-tuple (host, port) for address: %s', address)
        super(ConnectionEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id, team)

    def text(self):
        if isinstance(self.address, tuple):
            msg = 'connected, address "%s:%d"' % (self.address[0],
                                                  self.address[1])
        else:
            msg = 'connected, address "%s"' % (self.address)
        return ' '.join([super(ConnectionEvent, self).text(), msg])

    __str__ = text

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if kwargs['address'] != 'none':
            kwargs['address'] = (kwargs['host'], int(kwargs['port']))
        del kwargs['host']
        del kwargs['port']
        return cls(**kwargs)


@python_2_unicode_compatible
class ValidationEvent(PlayerEvent):

    """Player validation event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'STEAM USERID validated',
    ])

    def text(self):
        msg = 'STEAM USERID validated'
        return ' '.join([super(ValidationEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class EnterGameEvent(PlayerEvent):

    """Player entered game event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'entered the game',
    ])

    def text(self):
        msg = 'entered the game'
        return ' '.join([super(EnterGameEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class DisconnectionEvent(PlayerEvent):

    """Player disconnected event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'disconnected',
    ])

    def text(self):
        msg = 'disconnected'
        return ' '.join([super(DisconnectionEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class KickEvent(PlayerEvent):

    """Player kicked by console event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Kick: "(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>',
        r'<(?P<team>\w*)>" was kicked by "Console" ',
        r'\(message "(?P<message>.*)"\)',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, message):
        super(KickEvent, self).__init__(timestamp, player_name, uid,
                                        steam_id, team)
        self.message = message

    def text(self):
        return ' '.join([
            'L %s:' % (self.timestamp_to_str(self.timestamp)),
            'Kick: "%s"' % (self.player),
            'was kicked by "Console" (message "%s")' % (self.message),
        ])

    __str__ = text


@python_2_unicode_compatible
class SuicideEvent(PlayerEvent):

    """Player suicide event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'committed suicide with "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, weapon):
        super(SuicideEvent, self).__init__(timestamp, player_name, uid,
                                           steam_id, team)
        self.weapon = weapon

    def text(self):
        msg = 'committed suicide with "%s"' % (self.weapon)
        return ' '.join([super(SuicideEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class TeamSelectionEvent(PlayerEvent):

    """Player team select event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'joined team "(?P<new_team>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 new_team):
        super(TeamSelectionEvent, self).__init__(timestamp, player_name, uid,
                                                 steam_id, team)
        self.new_team = new_team

    def text(self):
        msg = 'joined team "%s"' % (self.new_team)
        return ' '.join([super(TeamSelectionEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class RoleSelectionEvent(PlayerEvent):

    """Player role select event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'changed role to "(?P<role>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 role):
        super(RoleSelectionEvent, self).__init__(timestamp, player_name, uid,
                                                 steam_id, team)
        self.role = role

    def text(self):
        msg = 'changed role to "%s"' % (self.role)
        return ' '.join([super(RoleSelectionEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class ChangeNameEvent(PlayerEvent):

    """Player name changed event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'changed name to "(?P<new_name>.*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 new_name):
        super(ChangeNameEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id, team)
        self.new_name = new_name

    def text(self):
        msg = 'changed name to "%s"' % (self.new_name)
        return ' '.join([super(ChangeNameEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class PlayerTargetEvent(BaseEvent):

    """Base class for events involving two players"""

    player_regex = ''.join([
        r'"(?P<player_name>.*)<(?P<player_uid>\d*)>',
        r'<(?P<player_steam_id>[\w:]*)><(?P<player_team>\w*)>"\s*',
    ])
    target_regex = ''.join([
        r'"(?P<target_name>.*)<(?P<target_uid>\d*)>',
        r'<(?P<target_steam_id>[\w:]*)><(?P<target_team>\w*)>"\s*',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team):
        super(PlayerTargetEvent, self).__init__(timestamp)
        self.player = BasePlayer(player_name, player_uid,
                                 SteamId(player_steam_id), player_team)
        self.target = BasePlayer(target_name, target_uid,
                                 SteamId(target_steam_id), target_team)


@python_2_unicode_compatible
class KillEvent(PlayerTargetEvent):

    """Player killed event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        r' killed ',
        PlayerTargetEvent.target_regex,
        r' with "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team, weapon):
        super(KillEvent, self).__init__(timestamp, player_name, player_uid,
                                        player_steam_id, player_team,
                                        target_name, target_uid,
                                        target_steam_id, target_team)
        self.weapon = weapon

    def text(self):
        msg = '"%s" killed "%s" with "%s"' % (self.player, self.target,
                                              self.weapon)
        return ' '.join([super(KillEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class AttackEvent(PlayerTargetEvent):

    """Player attacked event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        r' attacked ',
        PlayerTargetEvent.target_regex,
        r' with "(?P<weapon>\w*)" \(damage "(?P<damage>\d*)"\)',
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

    def text(self):
        msg = '"%s" attacked "%s" with "%s" (damage "%d")' % (self.player,
                                                              self.target,
                                                              self.weapon,
                                                              self.damage)
        return ' '.join([super(AttackEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class PlayerActionEvent(PlayerEvent):

    """Player triggered action event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'triggered "(?P<action>.*?)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 action):
        super(PlayerActionEvent, self).__init__(timestamp, player_name, uid,
                                                steam_id, team)
        self.action = action

    def text(self):
        msg = 'triggered "%s"' % (self.action)
        return ' '.join([super(PlayerActionEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class TeamActionEvent(BaseEvent):

    """Team triggered action event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Team "(?P<team>\w*?)" triggered "(?P<action>.*?)"',
    ])

    def __init__(self, timestamp, team, action):
        super(TeamActionEvent, self).__init__(timestamp)
        self.team = team
        self.action = action

    def text(self):
        msg = 'Team "%s" triggered "%s"' % (self.team, self.action)
        return ' '.join([super(TeamActionEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class WorldActionEvent(BaseEvent):

    """World triggered action event"""

    regex = ''.join([
        BaseEvent.regex,
        r'World triggered "(?P<action>.*?)"',
    ])

    def __init__(self, timestamp, action):
        super(WorldActionEvent, self).__init__(timestamp)
        self.action = action

    def text(self):
        msg = 'World triggered "%s"' % (self.action)
        return ' '.join([super(WorldActionEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class ChatEvent(PlayerEvent):

    """Chat event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'say(_team)? "(?P<message>.*?)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 message, say_team=False):
        super(ChatEvent, self).__init__(timestamp, player_name, uid, steam_id,
                                        team)
        self.say_team = say_team
        self.message = message

    def text(self):
        if self.say_team:
            msg = 'say_team "%s"' % (self.message)
        else:
            msg = 'say "%s"' % (self.message)
        return ' '.join([super(ChatEvent, self).text(), msg])

    __str__ = text

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        if match.string.find('say_team') >= 0:
            kwargs['say_team'] = True
        return cls(**kwargs)


@python_2_unicode_compatible
class TeamAllianceEvent(BaseEvent):

    """Team alliance event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Team "(?P<team_a>\w*?)" formed alliance with "(?P<team_b>\w*?)"',
    ])

    def __init__(self, timestamp, team_a, team_b):
        super(TeamAllianceEvent, self).__init__(timestamp)
        self.team_a = team_a
        self.team_b = team_b

    def text(self):
        msg = 'Team "%s" formed alliance with "%s"' % (self.team_a,
                                                       self.team_b)
        return ' '.join([super(TeamAllianceEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class RoundEndTeamEvent(BaseEvent):

    """Round end team score report event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Team "(?P<team>\w*?)" scored "(?P<score>\d+)" with ',
        r'"(?P<num_players>\d+)" players',
    ])

    def __init__(self, timestamp, team, score, num_players):
        super(RoundEndTeamEvent, self).__init__(timestamp)
        self.team = team
        self.score = int(score)
        self.num_players = int(num_players)

    def text(self):
        msg = 'Team "%s" scored "%d" with "%d" players' % (self.team,
                                                           self.score,
                                                           self.num_players)
        return ' '.join([super(RoundEndTeamEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class PrivateChatEvent(PlayerTargetEvent):

    """Private Chat event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        r' tell ',
        PlayerTargetEvent.target_regex,
        r' message "(?P<message>.*)"',
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

    def text(self):
        msg = '"%s" tell "%s" message "%s"' % (self.player, self.target,
                                               self.message)
        return ' '.join([super(PrivateChatEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class RoundEndPlayerEvent(PlayerEvent):

    """Round end player score report event"""

    regex = ''.join([
        BaseEvent.regex,
        r'Player "(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>',
        r'<(?P<team>\w*)>"\s*',
        r'scored "(?P<score>\d+)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, score):
        super(RoundEndPlayerEvent, self).__init__(timestamp, player_name, uid,
                                                  steam_id, team)
        self.score = int(score)

    def text(self):
        return ' '.join([
            'L %s:' % (self.timestamp_to_str(self.timestamp)),
            'Player "%s"' % (self.player),
            'scored "%d"' % (self.score),
        ])

    __str__ = text


@python_2_unicode_compatible
class WeaponSelectEvent(PlayerEvent):

    """Player selected weapon event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'selected weapon "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 weapon):
        super(WeaponSelectEvent, self).__init__(timestamp, player_name, uid,
                                                steam_id, team)
        self.weapon = weapon

    def text(self):
        msg = 'selected weapon "%s"' % (self.weapon)
        return ' '.join([super(WeaponSelectEvent, self).text(), msg])

    __str__ = text


@python_2_unicode_compatible
class WeaponPickupEvent(PlayerEvent):

    """Player picked up weapon event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'acquired weapon "(?P<weapon>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team,
                 weapon):
        super(WeaponPickupEvent, self).__init__(timestamp, player_name, uid,
                                                steam_id, team)
        self.weapon = weapon

    def text(self):
        msg = 'acquired weapon "%s"' % (self.weapon)
        return ' '.join([super(WeaponPickupEvent, self).text(), msg])

    __str__ = text


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

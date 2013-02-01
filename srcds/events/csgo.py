# Copyright (C) 2013 Peter Rowlands
"""csgo events module

Contains event classes for CS:S and CS:GO events

"""

from __future__ import absolute_import

from .generic import (BaseEvent, PlayerEvent, PlayerTargetEvent, KillEvent,
                      AttackEvent)


class SwitchTeamEvent(PlayerEvent):

    """Player switched team event"""

    regex = ''.join([
        BaseEvent.regex,
        ur'"(?P<player_name>.*)<(?P<uid>\d*)><(?P<steam_id>[\w:]*)>" ',
        ur'switched from team <(?P<orig_team>\w*)> to <(?P<new_team>\w*)>',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, orig_team,
                 new_team):
        super(SwitchTeamEvent, self).__init__(timestamp, player_name, uid,
                                              steam_id, team=None)
        self.orig_team = orig_team
        self.new_team = new_team

    def __unicode__(self):
        player = self.player
        player.team = None
        msg = u' '.join([
            u'"%s"' % player,
            u'switched from team <%s> to <%s>' % (self.orig_team,
                                                  self.new_team),
        ])
        return u' '.join([super(PlayerEvent, self).__unicode__(), msg])


class BuyEvent(PlayerEvent):

    """Player buy event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'purchased "(?P<item>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, item):
        super(BuyEvent, self).__init__(timestamp, player_name, uid, steam_id,
                                       team)
        self.item = item

    def __unicode__(self):
        msg = u'purchased "%s"' % (self.item)
        return u' '.join([super(BuyEvent, self).__unicode__(), msg])


class ThrowEvent(PlayerEvent):

    """Player threw grenade event"""

    regex = ''.join([
        PlayerEvent.regex,
        ur'threw (?P<nade>\w*) \[(?P<location>-?\d+ -?\d+ -?\d+)\]',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, nade,
                 location):
        if not isinstance(location, tuple) or not len(location) == 3:
            raise TypeError('Expected 3-tuple for location')
        super(ThrowEvent, self).__init__(timestamp, player_name, uid, steam_id,
                                         team)
        self.location = location
        self.nade = nade

    def __unicode__(self):
        msg = u'threw %s [%d %d %d]' % (self.nade, self.location[0],
                                       self.location[1], self.location[2])
        return u' '.join([super(ThrowEvent, self).__unicode__(), msg])

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        location = kwargs['location'].split()
        kwargs['location'] = (int(location[0]), int(location[1]),
                              int(location[2]))
        return cls(**kwargs)


class CsgoAssistEvent(PlayerTargetEvent):

    """Player assist event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        ur' assisted killing ',
        PlayerTargetEvent.target_regex
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, target_name, target_uid, target_steam_id,
                 target_team):
        super(CsgoAssistEvent, self).__init__(timestamp, player_name,
                                        player_uid, player_steam_id,
                                        player_team, target_name, target_uid,
                                        target_steam_id, target_team)

    def __unicode__(self):
        msg = u'"%s" assisted killing "%s" ' % (self.player, self.target)
        return u' '.join([super(CsgoAssistEvent, self).__unicode__(), msg])


class CsgoKillEvent(KillEvent):

    """CS:GO specific kill event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        ur'\[(?P<player_location>-?\d+ -?\d+ -?\d+)\]',
        ur' killed ',
        PlayerTargetEvent.target_regex,
        ur'\[(?P<target_location>-?\d+ -?\d+ -?\d+)\]',
        ur' with "(?P<weapon>\w*)"',
        ur'( \(headshot\))?',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, player_location, target_name, target_uid,
                 target_steam_id, target_team, target_location, weapon,
                 headshot=False):
        super(CsgoKillEvent, self).__init__(timestamp, player_name, player_uid,
                                            player_steam_id, player_team,
                                            target_name, target_uid,
                                            target_steam_id, target_team,
                                            weapon)
        if (not isinstance(player_location, tuple)
                or not len(player_location) == 3):
            raise TypeError('Expected 3-tuple for player_location')
        if (not isinstance(target_location, tuple)
                or not len(target_location) == 3):
            raise TypeError('Expected 3-tuple for target_location')
        self.player_location = player_location
        self.target_location = target_location
        self.headshot = headshot

    def __unicode__(self):
        msg = [
            u'L %s:' % (self.timestamp_to_str(self.timestamp)),
            u'"%s" [%d %d %d]' % (self.player, self.player_location[0],
                                 self.player_location[1],
                                 self.player_location[2]),
            u'killed',
            u'"%s" [%d %d %d]' % (self.target, self.target_location[0],
                                 self.target_location[1],
                                 self.target_location[2]),
            u'with "%s"' % (self.weapon),
        ]
        if self.headshot:
            msg.append(u'(headshot)')
        return u' '.join(msg)

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        player_location = kwargs['player_location'].split()
        kwargs['player_location'] = (int(player_location[0]),
                                     int(player_location[1]),
                                     int(player_location[2]))
        target_location = kwargs['target_location'].split()
        kwargs['target_location'] = (int(target_location[0]),
                                     int(target_location[1]),
                                     int(target_location[2]))
        if match.string.endswith('(headshot)'):
            kwargs['headshot'] = True
        return cls(**kwargs)


class CsgoAttackEvent(AttackEvent):

    """CS:GO specific attack event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        ur'\[(?P<player_location>-?\d+ -?\d+ -?\d+)\]',
        ur' attacked ',
        PlayerTargetEvent.target_regex,
        ur'\[(?P<target_location>-?\d+ -?\d+ -?\d+)\]',
        ur' with "(?P<weapon>\w*)"',
        ur' \(damage "(?P<damage>\d+)"\)',
        ur' \(damage_armor "(?P<damage_armor>\d+)"\)',
        ur' \(health "(?P<health>\d+)"\)',
        ur' \(armor "(?P<armor>\d+)"\)',
        ur' \(hitgroup "(?P<hitgroup>[\w ]+)"\)',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, player_location, target_name, target_uid,
                 target_steam_id, target_team, target_location, weapon,
                 damage, damage_armor, health, armor, hitgroup):
        super(CsgoAttackEvent, self).__init__(timestamp, player_name,
                                              player_uid, player_steam_id,
                                              player_team, target_name,
                                              target_uid, target_steam_id,
                                              target_team, weapon, damage)
        if (not isinstance(player_location, tuple)
                or not len(player_location) == 3):
            raise TypeError('Expected 3-tuple for player_location')
        if (not isinstance(target_location, tuple)
                or not len(target_location) == 3):
            raise TypeError('Expected 3-tuple for target_location')
        self.player_location = player_location
        self.target_location = target_location
        self.damage_armor = int(damage_armor)
        self.health = int(health)
        self.armor = int(armor)
        self.hitgroup = hitgroup

    def __unicode__(self):
        msg = [
            u'L %s:' % (self.timestamp_to_str(self.timestamp)),
            u'"%s" [%d %d %d]' % (self.player, self.player_location[0],
                                 self.player_location[1],
                                 self.player_location[2]),
            u'attacked',
            u'"%s" [%d %d %d]' % (self.target, self.target_location[0],
                                 self.target_location[1],
                                 self.target_location[2]),
            u'with "%s"' % (self.weapon),
            u'(damage "%d")' % (self.damage),
            u'(damage_armor "%d")' % (self.damage_armor),
            u'(health "%d")' % (self.health),
            u'(armor "%d")' % (self.armor),
            u'(hitgroup "%s")' % (self.hitgroup),
        ]
        return u' '.join(msg)

    @classmethod
    def from_re_match(cls, match):
        """Return an event constructed from a self.regex match"""
        kwargs = match.groupdict()
        player_location = kwargs['player_location'].split()
        kwargs['player_location'] = (int(player_location[0]),
                                     int(player_location[1]),
                                     int(player_location[2]))
        target_location = kwargs['target_location'].split()
        kwargs['target_location'] = (int(target_location[0]),
                                     int(target_location[1]),
                                     int(target_location[2]))
        return cls(**kwargs)


CSGO_EVENTS = [
    SwitchTeamEvent,
    BuyEvent,
    ThrowEvent,
    CsgoAssistEvent,
    CsgoKillEvent,
    CsgoAttackEvent,
]

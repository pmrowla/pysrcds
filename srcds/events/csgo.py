# Copyright (C) 2013 Peter Rowlands
"""csgo events module

Contains event classes for CS:S and CS:GO events

"""

from __future__ import absolute_import

from .generic import (BaseEvent, PlayerEvent, PlayerTargetEvent, KillEvent,
                      AttackEvent)


class BuyEvent(PlayerEvent):

    """Player buy event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'purchased "(?P<item>\w*)"',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, item):
        super(BuyEvent, self).__init__(timestamp, player_name, uid, steam_id,
                                       team)
        self.item = item

    def __str__(self):
        msg = 'purchased "%s"' % (self.item)
        return ' '.join([super(BuyEvent, self).__str__(), msg])


class ThrowEvent(PlayerEvent):

    """Player threw grenade event"""

    regex = ''.join([
        PlayerEvent.regex,
        r'threw (?P<grenade>\w*) \[(?<location>-?\d+ -?\d+ -?\d+)\]',
    ])

    def __init__(self, timestamp, player_name, uid, steam_id, team, nade,
                 location):
        if not isinstance(location, tuple) or not len(location) == 3:
            raise TypeError('Expected 3-tuple for location')
        super(ThrowEvent, self).__init__(timestamp, player_name, uid, steam_id,
                                         team)
        self.location = location
        self.nade = nade

    def __str__(self):
        msg = 'threw %s [%d %d %d]' % (self.nade, self.location[0],
                                       self.location[1], self.location[2])
        return ' '.join([super(ThrowEvent, self).__str__(), msg])


class CsGoKillEvent(KillEvent):

    """CS:GO specific kill event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        r'\[(?<player_location>-?\d+ -?\d+ -?\d+)\]',
        r' killed ',
        PlayerTargetEvent.target_regex,
        r'\[(?<target_location>-?\d+ -?\d+ -?\d+)\]',
        r' with "(?P<weapon>\w*)"',
        r'( \(headshot\))?',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, player_location, target_name, target_uid,
                 target_steam_id, target_team, target_location, weapon,
                 headshot):
        super(CsGoKillEvent, self).__init__(timestamp, player_name, player_uid,
                                            player_steam_id, player_team,
                                            target_name, target_uid,
                                            target_steam_id, target_team)
        if (not isinstance(player_location, tuple)
                or not len(player_location) == 3):
            raise TypeError('Expected 3-tuple for player_location')
        if (not isinstance(target_location, tuple)
                or not len(target_location) == 3):
            raise TypeError('Expected 3-tuple for target_location')
        self.player_location = player_location
        self.target_location = target_location
        self.weapon = weapon
        self.headshot = headshot

    def __str__(self):
        msg = [
            'L %s:' % (self.timestamp_to_str(self.timestamp)),
            '"%s" [%d %d %d]' % (self.player, self.player_location[0],
                                 self.player_location[1],
                                 self.player_location[2]),
            'killed',
            '"%s" [%d %d %d]' % (self.target, self.target_location[0],
                                 self.target_location[1],
                                 self.target_location[2]),
            'with "%s"' % (self.weapon),
        ]
        if self.headshot:
            msg.append('(headshot)')
        return ' '.join(msg)


class CsGoAttackEvent(AttackEvent):

    """CS:GO specific attack event"""

    regex = ''.join([
        BaseEvent.regex,
        PlayerTargetEvent.player_regex,
        r'\[(?<player_location>-?\d+ -?\d+ -?\d+)\]',
        r' attacked ',
        PlayerTargetEvent.target_regex,
        r'\[(?<target_location>-?\d+ -?\d+ -?\d+)\]',
        r' with "(?P<weapon>\w*)"',
        r' \(damage "(?P<damage>\d+)"\)',
        r' \(damage_armor "(?P<damage_armor>\d+)"\)',
        r' \(health "(?P<health>\d+)"\)',
        r' \(armor "(?P<armor>\d+)"\)',
        r' \(hitgroup "(?P<hitgroup>\w+)"\)',
    ])

    def __init__(self, timestamp, player_name, player_uid, player_steam_id,
                 player_team, player_location, target_name, target_uid,
                 target_steam_id, target_team, target_location, weapon,
                 damage, damage_armor, health, armor, hitgroup):
        super(CsGoAttackEvent, self).__init__(timestamp, player_name,
                                              player_uid, player_steam_id,
                                              player_team, target_name,
                                              target_uid, target_steam_id,
                                              target_team)
        if (not isinstance(player_location, tuple)
                or not len(player_location) == 3):
            raise TypeError('Expected 3-tuple for player_location')
        if (not isinstance(target_location, tuple)
                or not len(target_location) == 3):
            raise TypeError('Expected 3-tuple for target_location')
        self.player_location = player_location
        self.target_location = target_location
        self.weapon = weapon
        self.damage = damage
        self.damage_armor = damage_armor
        self.health = health
        self.armor = armor
        self.hitgroup = hitgroup

    def __str__(self):
        msg = [
            'L %s:' % (self.timestamp_to_str(self.timestamp)),
            '"%s" [%d %d %d]' % (self.player, self.player_location[0],
                                 self.player_location[1],
                                 self.player_location[2]),
            'attacked',
            '"%s" [%d %d %d]' % (self.target, self.target_location[0],
                                 self.target_location[1],
                                 self.target_location[2]),
            'with "%s"' % (self.weapon),
            '(damage "%d")' % (self.damage),
            '(damage_armor "%d")' % (self.damage_armor),
            '(health "%d")' % (self.health),
            '(armor "%d")' % (self.armor),
            '(hitgroup "%s")' % (self.hitgroup),
        ]
        return ' '.join(msg)

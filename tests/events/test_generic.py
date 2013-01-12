# Copyright (C) 2013 Peter Rowlands
"""Tests for srcds.events.generic"""

import re

from srcds.events import generic


def check_event(cls, log_line):
    match = re.match(cls.regex, log_line)
    assert match
    event = cls.from_re_match(match)
    assert event
    assert str(event) == log_line
    return event

def test_base_event():
    """Test BaseEvent"""
    log_line = 'L 01/11/2013 - 16:57:49:'
    check_event(generic.BaseEvent, log_line)

def test_cvar_event():
    """Test CvarEvent"""
    log_line = 'L 01/11/2013 - 16:57:49: Server cvars start'
    event = check_event(generic.CvarEvent, log_line)
    assert event.start and not event.end
    log_line = 'L 01/11/2013 - 16:57:49: Server cvars end'
    event = check_event(generic.CvarEvent, log_line)
    assert not event.start and event.end
    log_line = 'L 01/11/2013 - 16:57:49: Server cvar "foo" = "bar"'
    event = check_event(generic.CvarEvent, log_line)
    assert event.cvar == 'foo' and event.value == 'bar'

def test_log_file_event():
    """Test LogFileEvent"""
    log_line = ''.join([
        'L 01/10/2013 - 22:46:06: Log file started (file ',
        '"logfiles/L066_228_036_149_27015_201301102246_001.log") ',
        '(game "/opt/steam/csgo-ds/csgo") (version "5177")',
    ])
    event = check_event(generic.LogFileEvent, log_line)
    assert event.started and not event.closed
    log_line = 'L 01/10/2013 - 23:15:21: Log file closed'
    event = check_event(generic.LogFileEvent, log_line)
    assert not event.started and event.closed

def test_change_map_event():
    """Test ChangeMapEvent"""
    # TODO find an example for this
    pass

def test_rcon_event():
    """Test RconEvent"""
    # TODO find an example for this
    pass

def test_connection_event():
    """Test ConnectionEvent"""
    # test bot connection
    log_line = ''.join([
        'L 01/11/2013 - 16:57:58: "Dave<3><BOT><>" connected, ',
        'address "none"',
    ])
    check_event(generic.ConnectionEvent, log_line)
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'connected, address "12.34.56.78:27005"',
    ])
    check_event(generic.ConnectionEvent, log_line)

def test_validation_event():
    """Test ValidationEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'STEAM USERID validated',
    ])
    check_event(generic.ValidationEvent, log_line)

def test_diconnection_event():
    """Test DisconnectionEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'disconnected',
    ])
    check_event(generic.DisconnectionEvent, log_line)

def test_kick_event():
    """Test KickEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: Kick: "foobar<21><STEAM_1:1:12345><>" ',
        'was kicked by "Console" (message "")',
    ])
    check_event(generic.KickEvent, log_line)

def test_suicide_event():
    """Test SuicideEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'committed suicide with "hegrenade"',
    ])
    check_event(generic.SuicideEvent, log_line)

def test_team_selection_event():
    """Test TeamSelectionEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'joined team "Spectators"',
    ])
    check_event(generic.TeamSelectionEvent, log_line)

def test_role_selection_event():
    """Test RoleSelectionEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><CT>" ',
        'changed role to "medic"',
    ])
    check_event(generic.RoleSelectionEvent, log_line)

def test_change_name_event():
    """Test ChangeNameEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'changed name to "baz"',
    ])
    check_event(generic.ChangeNameEvent, log_line)

def test_player_target_event():
    """Test PlayerTargetEvent"""
    player = '"foobar<21><STEAM_1:1:12345><Spectators>"'
    assert re.match(generic.PlayerTargetEvent.player_regex, player)
    assert re.match(generic.PlayerTargetEvent.target_regex, player)

def test_kill_event():
    """Test KillEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 01:01:01: "foo<32><STEAM_1:0:12345><TERRORIST>" ',
        'killed "bar<38><STEAM_1:1:54321><TERRORIST>" with "glock"',
    ])
    check_event(generic.KillEvent, log_line)

def test_attack_event():
    """Test AttackEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 01:01:01: "foo<32><STEAM_1:0:12345><TERRORIST>" ',
        'attacked "bar<38><STEAM_1:1:54321><TERRORIST>" with "glock" ',
        '(damage "50")',
    ])
    check_event(generic.AttackEvent, log_line)

def test_player_action_event():
    """Test PlayerActionEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'triggered "baz"',
    ])
    check_event(generic.PlayerActionEvent, log_line)

def test_team_action_event():
    """Test TeamActionEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: Team "TERRORIST" ',
        'triggered "foo"',
    ])
    check_event(generic.TeamActionEvent, log_line)

def test_world_action_event():
    """Test WorldActionEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: World triggered "Round_End"',
    ])
    check_event(generic.WorldActionEvent, log_line)

def test_chat_event():
    """Test ChatEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'say "baz"',
    ])
    check_event(generic.ChatEvent, log_line)
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><>" ',
        'say_team "baz"',
    ])
    check_event(generic.ChatEvent, log_line)

def test_team_alliance_event():
    """Test TeamAllianceEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: Team "TERRORIST" ',
        'formed alliance with "CT"',
    ])
    check_event(generic.TeamAllianceEvent, log_line)

def test_round_end_team_event():
    """Test RoundEndTeamEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: Team "TERRORIST" ',
        'scored "2" with "5" players',
    ])
    check_event(generic.RoundEndTeamEvent, log_line)

def test_private_chat_event():
    """Test PrivateChatEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 01:01:01: "foo<32><STEAM_1:0:12345><TERRORIST>" ',
        'tell "bar<38><STEAM_1:1:54321><TERRORIST>" ',
        'message "baz"',
    ])
    check_event(generic.PrivateChatEvent, log_line)

def test_round_end_player_event():
    """Test RoundEndPlayerEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: Player "foobar<21><STEAM_1:1:12345><CT>" ',
        'scored "4"',
    ])
    check_event(generic.RoundEndPlayerEvent, log_line)

def weapon_select_event():
    """Test WeaponSelectEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><TERRORIST>" ',
        'selected weapon "glock"',
    ])
    check_event(generic.WeaponSelectEvent, log_line)

def weapon_pickup_event():
    """Test WeaponPickupEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><TERRORIST>" ',
        'acquired weapon "glock"',
    ])
    check_event(generic.WeaponPickupEvent, log_line)

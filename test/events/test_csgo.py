# Copyright (C) 2013 Peter Rowlands
"""Tests for srcds.events.csgo"""


from srcds.events import csgo

from .test_generic import check_event


def test_switch_team_event():
    """Test SwitchTeamEvent"""
    log_line = ''.join([
        'L 01/21/2013 - 23:07:24: "Charmander<19><STEAM_1:1:11218680>" ',
        'switched from team <Unassigned> to <CT>',
    ])
    check_event(csgo.SwitchTeamEvent, log_line)


def test_buy_event():
    """Test BuyEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><CT>" ',
        'purchased "defuser"',
    ])
    check_event(csgo.BuyEvent, log_line)


def test_throw_event():
    """Test ThrowEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 00:57:01: "foobar<21><STEAM_1:1:12345><CT>" ',
        'threw hegrenade [-1879 2651 33]',
    ])
    check_event(csgo.ThrowEvent, log_line)


def test_csgo_kill_event():
    """Test CsgoKillEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 01:01:01: "foo<32><STEAM_1:0:12345><TERRORIST>" ',
        '[-761 -836 196] killed "bar<38><STEAM_1:1:54321><CT>" ',
        '[-793 -848 130] with "glock"',
    ])
    event = check_event(csgo.CsgoKillEvent, log_line)
    assert not event.headshot
    log_line = ''.join([
        'L 01/12/2013 - 01:01:01: "foo<32><STEAM_1:0:12345><TERRORIST>" ',
        '[-761 -836 196] killed "bar<38><STEAM_1:1:54321><CT>" ',
        '[-793 -848 130] with "glock" (headshot)',
    ])
    event = check_event(csgo.CsgoKillEvent, log_line)
    assert event.headshot

def test_csgo_attack_event():
    """Test CsgoAttackEvent"""
    log_line = ''.join([
        'L 01/12/2013 - 01:01:14: "foo<30><STEAM_1:0:12345><CT>" [254 -370 7]',
        ' attacked "bar<33><STEAM_1:1:54321><TERRORIST>" [-428 -843 114] ',
        'with "m4a1" (damage "21") (damage_armor "4") (health "45") ',
        '(armor "87") (hitgroup "right arm")',
    ])
    check_event(csgo.CsgoAttackEvent, log_line)

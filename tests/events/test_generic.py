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
    log_line = 'L 01/10/2013 - 22:46:06: Log file started (file "logfiles/L066_228_036_149_27015_201301102246_001.log") (game "/opt/steam/csgo-ds/csgo") (version "5177")'
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
    log_line = 'L 01/11/2013 - 16:57:58: "Dave<3><BOT><>" connected, address "none"'
    check_event(generic.ConnectionEvent, log_line)
    # TODO get player conn example

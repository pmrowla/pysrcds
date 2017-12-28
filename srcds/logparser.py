# Copyright (C) 2013 Peter Rowlands
"""
Source server log parsing module

Complies with the HL Log Standard rev. 1.03

"""

from __future__ import division, absolute_import
import os
import re
from collections import deque

from .events import generic


class UnknownEventError(Exception):
    pass


class SourceLogParser(object):

    """HL Log Standard parser class"""

    def __init__(self, default_events=True, skip_unknowns=True):
        self.events = deque()
        self.events_types = []
        self.skip_unknowns = skip_unknowns
        if default_events:
            self.add_event_types(generic.STANDARD_EVENTS)

    def add_event_types(self, event_types=[]):
        """Add event types"""
        for cls in event_types:
            regex = re.compile(cls.regex, re.U)
            self.events_types.append((regex, cls))

    def parse_line(self, line):
        """Parse a single log line"""
        line = line.strip()
        for (regex, cls) in self.events_types:
            match = regex.match(line)
            if match:
                event = cls.from_re_match(match)
                self.events.append(event)
                return
        if not self.skip_unknowns:
            raise UnknownEventError('Could not parse event: %s' % line)

    def read(self, filename):
        """Read in a log file"""
        fd = open(filename)
        for line in fd.readlines():
            self.parse_line(line)
        fd.close()

    def write(self, fileobject):
        """Write the events back to a file object"""
        lines = []
        for event in self.events:
            lines.append(str(self.event))
        fileobject.write(os.linesep.join(lines))

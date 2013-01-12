# Copyright (C) 2013 Peter Rowlands
"""
Source server log parsing module

Complies with the HL Log Standard rev. 1.03

"""


from __future__ import division, absolute_import
from Queue import Queue
import re

from .events import generic


class UnknownEventError(Exception):
    pass


class SourceLogParser(object):

    """HL Log Standard parser class"""

    def __init__(self):
        self.event_q = Queue()
        self.events = []
        self.add_event_types(generic.STANDARD_EVENTS)

    def add_event_types(self, event_types=[]):
        """Add event types"""
        for cls in event_types:
            regex = re.compile(cls.regex)
            self.events.append((regex, cls))

    def read(self, filename):
        """Read in a log file"""
        fd = open(filename)
        for line in fd.readlines():
            self.parse_line(line)
        fd.close()

    def parse_line(self, line):
        """Parse a single log line"""
        line = line.strip()
        for (regex, cls) in self.events:
            match = regex.match(line)
            if match:
                event = cls.from_re_match(match)
                self.event_q.put(event)
                return
        raise UnknownEventError('Could not parse event: %s' % line)

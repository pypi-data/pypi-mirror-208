"""EventLog class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .omniid import OmniId
from .omnierror import OmniError
from .peektime import PeekTime


class EventLogEntry(object):
    """An Entry from an Event Log.
    """

    capture_id = None
    """The GUID of the Capture this log entry. Or None or Null GUID"""

    index = 0
    """The index of the log entry. The first index is 1."""

    message = ''
    """The message of the log entry."""

    severity = 0
    """The severity of the log entry:
    0-Informationa, 1-Minor, 2-Major, 3-Severe.
    """

    source_id = None
    """The GUID of the source of the log entry."""

    source_key = 0
    """The GUID of the source of the log entry."""

    timestamp = None
    """The date and time when the log entry was generated."""

    # XML Tags
    _json_capture_id = "contextId"
    _json_index = "messageId"
    _json_message = "shortMessage"
    _json_severity = "severity"
    _json_source_id = "sourceId"
    _json_source_key = "sourceKey"
    _json_timestamp = "timestamp"
    _json_long_message = "longMessage"
    _json_offsets = "offsets"

    _tag_capture_id = "capture_id"
    _tag_index = "index"
    _tag_message = "message"
    _tag_severity = "severity"
    _tag_source_id = "source_id"
    _tag_source_key = "source_key"
    _tag_timestamp = "timestamp"
    _tag_long_message = ""
    _tag_offsets = ""

    _event_log_entry_prop_dict = {
        _json_capture_id: _tag_capture_id,
        _json_index: _tag_index,
        _json_message: _tag_message,
        _json_severity: _tag_severity,
        _json_source_id: _tag_source_id,
        _json_source_key: _tag_source_key,
        _json_timestamp: _tag_timestamp,
        _json_long_message: _tag_long_message,
        _json_offsets: _tag_offsets
    }

    def __init__(self, props=None):
        self.capture_id = EventLogEntry.capture_id
        self.index = EventLogEntry.index
        self.message = EventLogEntry.message
        self.severity = EventLogEntry.severity
        self.source_id = EventLogEntry.source_id
        self.source_key = EventLogEntry.source_key
        self.timestamp = EventLogEntry.timestamp
        self._load(props)

    def __str__(self):
        return f'EventLogEntry: {self.message}'

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                a = EventLogEntry._event_log_entry_prop_dict.get(k)
                if hasattr(self, a):
                    if isinstance(getattr(self, a), six.string_types):
                        setattr(self, a, v if v else '')
                    elif isinstance(getattr(self, a), int):
                        setattr(self, a, int(v) if v else 0)
                    elif getattr(self, a) is None:
                        if (a == EventLogEntry._tag_capture_id
                                or a == EventLogEntry._tag_source_id):
                            setattr(self, a, OmniId(v))
                        elif a == EventLogEntry._tag_timestamp:
                            setattr(self, a, PeekTime(v))

    def _key(self):
        return self.index


class EventLog(object):
    """The EventLog class.
    """

    context_id = None
    """The id of the context (Capture)."""

    count = 0
    """The total number of entries in the log."""

    engine = None
    """The OmniEngine object the Audit Log is from."""

    first = None
    """The timestamp of the first log entry."""

    informational = 0
    """The number of informational (0) events."""

    last = None
    """The timestamp of the last log entry."""

    major = 0
    """The number of major (2) events."""

    minor = 0
    """The number of minor (1) events."""

    query = None
    """The query string for this EventLog."""

    severe = 0
    """The number of severe (3) events."""

    entries = None
    """The list of
    :class:`EventLogEntry <omniscript.eventlog.EventLogEntry>`
    Entries.
    """

    # Tags
    _json_count = 'total'
    _json_first = 'firstTimestamp'
    _json_informational = 'informational'
    _json_last = 'lastTimestamp'
    _json_major = 'major'
    _json_minor = 'minor'
    _json_severe = 'severe'
    _json_counts = 'counts'
    _tag_entries = 'messages'

    _tag_count = 'count'
    _tag_first = 'first'
    _tag_informational = 'informational'
    _tag_last = 'last'
    _tag_major = 'major'
    _tag_minor = 'minor'
    _tag_severe = 'severe'
    _tag_entries = 'entries'

    _event_log_prop_dict = {
        _json_count: _tag_count,
        _json_first: _tag_first,
        _json_informational: _tag_informational,
        _json_last: _tag_last,
        _json_major: _tag_major,
        _json_minor: _tag_minor,
        _json_severe: _tag_severe
    }

    def __init__(self, engine, props, context_id, query):
        self.context_id = context_id
        self.count = EventLog.count
        self.engine = engine
        self.first = EventLog.first
        self.informational = EventLog.informational
        self.last = EventLog.last
        self.major = EventLog.major
        self.minor = EventLog.minor
        self.query = query
        self.severe = EventLog.severe
        self.entries = []
        self._load_counts(props)
        self._load_entrys(props)

    def __str__(self):
        if self.context_id:
            return f'EventLog of {self.context_id}'
        elif self.engine:
            return f'EventLog of {self.engine}'
        else:
            return 'EventLog'

    def _load_counts(self, props):
        if isinstance(props, dict):
            counts = props.get('counts')
            if isinstance(counts, dict):
                for k, v in counts.items():
                    a = EventLog._event_log_prop_dict[k]
                    if a == EventLog._tag_count:
                        self.count = max(self.count, int(v))
                    elif a == EventLog._tag_informational:
                        self.informational = max(self.informational, int(v))
                    elif a == EventLog._tag_major:
                        self.major = max(self.major, int(v))
                    elif a == EventLog._tag_minor:
                        self.minor = max(self.minor, int(v))
                    elif a == EventLog._tag_severe:
                        self.severe = max(self.severe, int(v))
                    elif a == EventLog._tag_first:
                        self.first = PeekTime(v)
                    elif a == EventLog._tag_last:
                        self.last = PeekTime(v)
            # _first = counts.findtext(EventLog._tag_first, None)
            # if _first:
            #     self.first = PeekTime(_first)
            # _last = counts.findtext(EventLog._tag_last, None)
            # if _last:
            #     self.last = PeekTime(_last)

    def _load_entrys(self, props):
        if isinstance(props, dict):
            entrys = props.get('messages')
            if isinstance(entrys, list):
                for e in entrys:
                    self.entries.append(EventLogEntry(e))

    def get(self, first, count):
        """Add entries to the EventLog starting from first upto count
        entries. The object's entry list will be sorted and without
        duplicates.
        """
        if not self.engine:
            raise OmniError('EventLog does not have an OmniEngine.')
        if isinstance(count, int) and count == 0:
            return
        if count > 0:
            _count = count
            _first = first
        else:
            _count = -count
            _first = (self.count - first) if (first < self.count) else 0
        _el = self.engine.get_event_log(
            _first, _count, self.context_id, self.query)
        self.update(_el)

    def get_next(self, count=None):
        """Retrieve the next count entries of the EventLog or the last
        count entries if count is negative. If count is not specified,
        then the remaining entries are retrieved.
        """
        if not self.engine:
            raise OmniError('EventLog does not have an OmniEngine.')
        if isinstance(count, int) and count == 0:
            return
        if count > 0:
            _count = count
            _first = self.entries[-1].index if self.entries else 0
        else:
            _count = -count
            _first = (self.count - _count) if (_count < self.count) else 0
        _el = self.engine.get_event_log(
            _first, _count, self.context_id, self.query)
        self.update(_el)

    def update(self, el):
        """Update this EventLog with the another EventLog.
        """
        if isinstance(el, EventLog):
            if el.engine != self.engine:
                raise OmniError('EventLog must be from the same OmniEngine.')
            if el.context_id != self.context_id:
                raise OmniError('EventLog must be from the same Capture.')
            self.count = el.count
            self.last = el.last
            _s = set(self.entries)
            _s.update(el.entries)
            self.entries = sorted(_s, key=EventLogEntry._key)

"""AuditLog class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .peektime import PeekTime


class AuditLogMessage(object):
    """A Message from an Audit Log.
    """

    client = ''
    """The client of the AuditLogMessage."""

    id = 0
    """The identifier of the AuditLogMessage."""

    message = ''
    """The message of the AuditLogMessage."""

    result = 0
    """The result of the AuditLogMessage."""

    user = ''
    """The user of the AuditLogMessage."""

    timestamp = None
    """The timestamp of the AuditLogMessage."""

    def __init__(self, props=None):
        self.client = AuditLogMessage.client
        self.id = AuditLogMessage.id
        self.message = AuditLogMessage.message
        self.result = AuditLogMessage.result
        self.user = AuditLogMessage.user
        self.timestamp = AuditLogMessage.timestamp
        self._load(props)

    def __str__(self):
        return f'AuditLogMessage: {self.message}'

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == 'client':
                    self.client = v
                elif k == 'messageId':
                    self.id = int(v)
                elif k == 'message':
                    self.message = v
                elif k == 'result':
                    self.result = int(v)
                elif k == 'user':
                    self.user = v
                elif k == 'timestamp':
                    self.timestamp = PeekTime(v)


class AuditLog(object):
    """The AuditLog class.
    """

    _engine = None
    """The OmniEngine of this Audit Log."""

    total_count = 0
    """The total number of messages in the OmniEngine's Audit Log."""

    start_timestamp = None
    """The timestamp of the OmniEngines' Audit Log."""

    end_timestamp = None
    """The timestamp of the OmniEngine's Audit Log"""

    first_timestamp = None
    """The oldest timestamp in message_list."""

    last_time_stamp = None
    """The latest timestamp in message_list."""

    message_list = None
    """The list of
    :class:`AuditLogMessage <omniscript.auditlog.AuditLogMessage>`
    Entries.
    """

    def __init__(self, engine, props):
        self._engine = engine
        self.total_count = 0
        self.start_timestamp = None
        self.end_timestamp = None
        self.first_timestamp = None
        self.last_time_stamp = None
        self.message_list = []
        self._load(props)

    def __str__(self):
        return (f'AuditLog of {self._engine._last_status.name}' if self._engine._last_status
                else 'an OmniEngine')

    def _load(self, props):
        if isinstance(props, dict):
            counts = props.get('counts')
            if isinstance(counts, dict):
                for k, v in counts.items():
                    if k == 'total':
                        self.total_count = int(v)
                    elif k == 'firstTimestamp':
                        self.first_timestamp = PeekTime(v)
                    elif k == 'lastTimestamp':
                        self.last_timestamp = PeekTime(v)
            all_counts = props.get('allCounts')
            if isinstance(all_counts, dict):
                for k, v in all_counts.items():
                    if k == 'total':
                        self.total_count = int(v)
                    elif k == 'firstTimestamp':
                        self.start_timestamp = PeekTime(v)
                    elif k == 'lastTimestamp':
                        self.end_timestamp = PeekTime(v)
            messages = props.get('messages')
            if isinstance(messages, list):
                for m in messages:
                    self.message_list.append(AuditLogMessage(m))

    @property
    def count(self):
        return len(self.message_list)

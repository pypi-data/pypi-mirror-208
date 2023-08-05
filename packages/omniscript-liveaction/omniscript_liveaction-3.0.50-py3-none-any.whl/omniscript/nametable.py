"""NameTable class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .peektime import PeekTime


class NameTableEntry(object):
    """A NameTable Entry object.
    """

    entry = None
    entry_type = 0
    name = ''
    group = ''
    modified = None
    used = None
    color = 0

    def __init__(self, props=None):
        self.entry = NameTableEntry.entry
        self.entry_type = NameTableEntry.entry_type
        self.name = NameTableEntry.name
        self.group = NameTableEntry.group
        self.modified = NameTableEntry.modified
        self.used = PeekTime(NameTableEntry.used)
        self.color = PeekTime(NameTableEntry.color)
        self._load(props)

    def __str__(self):
        return f'NameTableEntry: {self.name}'

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == 'entry':
                    self.entry = v
                elif k == 'entry_type':
                    self.entry_type = int(v)
                elif k == 'name':
                    self.name = v
                elif k == 'group':
                    self.group = v
                elif k == 'modified':
                    self.modified = v
                elif k == 'used':
                    self.used = v
                elif k == 'color':
                    self.color = int(v.strip('#'), 16)


class NameTable(object):
    """The NameTable class.
    """

    _engine = None
    """The OmniEngine of this Audit Log."""

    modified = None
    """The last time the NameTable was modified."""

    name_list = None
    """The list of
    :class:`NameTableEntry <omniscript.nametable.NameTableEntry>`
    Entries.
    """

    def __init__(self, engine, props):
        self._engine = engine
        self.modified = None
        self.name_list = None
        self._load(props)

    def __str__(self):
        return f'Name Table of {self._engine.name}'

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == 'modificationTime':
                    self.modified = PeekTime(v)
                elif k == 'names':
                    self.name_list = []
                    names = props.get('names')
                    if isinstance(names, list):
                        for n in names:
                            self.name_list.append(NameTableEntry(n))

    @property
    def count(self):
        return len(self.name_list)

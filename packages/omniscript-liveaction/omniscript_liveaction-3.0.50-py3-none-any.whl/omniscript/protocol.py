"""Protocol class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from typing import List


class Protocol(object):
    """A Protocol object.
    """

    color = 0
    """Color of the protocol."""

    description = ''
    """Description of the protocol."""

    hierarchy_name = ''
    """Hierarchy Name of the protocol."""

    id = 0
    """Id of the protocol."""

    long_name = ''
    """Long name of the protocol."""

    name = ''
    """Name of the protocol."""

    find_attributes = ('name', 'id', 'color', 'hierarchy')
    """Attributes to search list of Protocols on."""

    def __init__(self, props: dict):
        self.color = Protocol.color
        self.description = Protocol.description
        self.hierarchy_name = Protocol.hierarchy_name
        self.id = Protocol.id
        self.long_name = Protocol.long_name
        self.name = Protocol.name
        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == 'color':
                    self.color = int(v.strip('#'), 16)
                elif k == 'description':
                    self.description = v
                elif k == 'hierName':
                    self.hierarchy_name = v
                elif k == 'id':
                    self.id = int(v)
                elif k == 'longName':
                    self.long_name = v
                elif k == 'shortName':
                    self.name = v


def _create_protocol_list(props: dict) -> List[Protocol]:
    lst = []
    if isinstance(props, dict):
        protocols = props.get('protocols')
        if isinstance(protocols, list):
            for p in protocols:
                lst.append(Protocol(p))
        lst.sort(key=lambda x: x.name)
    return lst


def find_protocol(protocols: List[Protocol], value: Protocol,
                  attrib=Protocol.find_attributes[0]) -> Protocol:
    """Find the first Protocol in the list that matches in attribute."""
    if (not protocols) or (attrib not in Protocol.find_attributes):
        return None

    _attrib = 'hierarchy_name' if attrib == 'hierarchy' else attrib

    if isinstance(value, Protocol):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in protocols if getattr(i, _attrib) == _value), None)


def find_all_protocol(protocols: List[Protocol], value: Protocol,
                      attrib=Protocol.find_attributes[0]) -> List[Protocol]:
    """Finds all the Protocols in the list that match the attribute."""
    if (not protocols) or (attrib not in Protocol.find_attributes):
        return None

    _attrib = 'hierarchy_name' if attrib == 'hierarchy' else attrib

    if isinstance(value, Protocol):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return [i for i in protocols if getattr(i, _attrib) == _value]

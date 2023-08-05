"""OmniPort classes.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import xml.etree.ElementTree as ET

from .invariant import PORT_TYPE_IP


class PortRange(object):
    """A range of ports."""

    min = 0
    """Lower bound."""

    max = None
    """Upper bound."""

    def __init__(self, value=None):
        self.min = PortRange.min
        self.max = PortRange.max
        if value is not None:
            self._load(value)

    def __str__(self):
        return f'{self.min}' if self.max is None else f'{self.min}-{self.max}'

    def _load(self, value):
        if isinstance(value, int):
            self.min, self.max = value, None
        elif isinstance(value, six.string_types):
            items = value.split('-')
            if len(items) == 1:
                self.min, self.max = int(items[0]), None
            elif len(items) == 2:
                self.min, self.max = int(items[0]), int(items[1])


class OmniPort(object):
    """The OmniPort class."""

    _mask = 0xC0000000
    """The mask value for _storing the port."""

    port_type = PORT_TYPE_IP
    """The type of port. One of the PORT TYPE constants.
    Default is PORT_TYPE_IP.
    """

    port = None
    """The port and/or port-range list."""

    def __init__(self, port=None):
        self._mask = OmniPort._mask
        self.port_type = PORT_TYPE_IP
        self.port = []
        if isinstance(port, int):
            self.port.append(port)
        elif isinstance(port, six.string_types):
            items = port.split()
            for item in items:
                self.port.append(PortRange(item))
        elif isinstance(port, ET.Element):
            self._load(port)

    def __repr__(self) -> str:
        return f'Port: {" ".join(str(p) for p in self.port)}'

    def __str__(self) -> str:
        return " ".join(str(p) for p in self.port)

    # def _load(self, node):
    #     self.port_type = int(node.get('type', '0'))
    #     self._mask = int(node.get('mask', '0'))
    #     data = node.get('data')
    #     if data is not None:
    #         items = data.split()
    #         for item in items:
    #             self.port.append(PortRange(item))

    # def _store(self, node, name):
    #     ET.SubElement(node, name, {'class':'3',
    #                                 'type':str(self.port_type),
    #                                 'data':str(self),
    #                                 'mask':str(self._mask)})

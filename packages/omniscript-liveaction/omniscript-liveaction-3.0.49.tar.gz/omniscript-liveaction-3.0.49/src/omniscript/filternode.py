"""FilterNode class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import xml.etree.ElementTree as ET

import omniscript

from .analysismodule import AnalysisModule
from .omniaddress import OmniAddress, BaseAddress
from .omniport import OmniPort
from .omniid import OmniId
from .peektime import PeekTime

from .invariant import (
    PATTERN_TYPE_ASCII, VALUE_FLAG_NETWORK_BYTE_ORDER, VALUE_OPERATOR_EQUAL, WIRELESS_BAND_ALL,
    WAN_DIRECTION_UNDEFINED)

_json_classid = 'clsid'
_json_andnode = 'andNode'
_json_ornode = 'orNode'
_json_accept_1_to_2 = 'accept1To2'
_json_accept_2_to_1 = 'accept2To1'
_json_data = 'data'
_json_slice = 'sliceToHeader'
_json_type = 'type'

_tag_class_name = '_class_name'

_filter_id_to_class = None


def _build_class_id():
    global _filter_id_to_class
    class_name_ids = omniscript.get_class_name_ids()
    _filter_id_to_class = (dict((class_name_ids[name_], class_)
                           for (name_, class_) in _filter_name_class))
    # Add the duplicate AddressFilterNode.
    id_class_names = omniscript.get_id_class_names()
    for k, v in id_class_names.items():
        if v == 'AddressFilterNode':
            if k not in _filter_id_to_class:
                _filter_id_to_class[k] = _filter_name_class[1][1]
                return


def get_id_to_class():
    global _filter_id_to_class
    if _filter_id_to_class is None:
        _build_class_id()
    return _filter_id_to_class


def parse_omni_filter(element):
    if isinstance(element, dict):
        return parse_omni_filter_dict(element)
    if isinstance(element, ET.Element):
        return parse_omni_filter_xml(element)
    return None


def parse_omni_filter_dict(element):
    if not isinstance(element, dict) and (_json_classid not in element):
        return None
    id_to_class = get_id_to_class()
    node = id_to_class[OmniId(element[_json_classid])]  # 2 lines for debugging.
    root = node(element)  # step right into the __init__ function.
    if not root:
        return None
    if (_json_andnode in element) and (element[_json_andnode] is not None):
        root.and_node = parse_omni_filter_dict(element[_json_andnode])
    if (_json_ornode in element) and (element[_json_ornode] is not None):
        root.or_node = parse_omni_filter_dict(element[_json_ornode])
    return root


def parse_omni_filter_xml(element):
    id_to_class = get_id_to_class()
    clsid = OmniId(element.get('clsid'))
    filter_node = element.find('filternode')
    root = id_to_class[clsid](filter_node)
    and_node = filter_node.find('andnode')
    if and_node is not None:
        root.and_node = parse_omni_filter_xml(and_node)
    or_node = filter_node.find('ornode')
    if or_node is not None:
        root.or_node = parse_omni_filter_xml(or_node)
    return root


def parse_console_filter(element):
    global _console_filter_id_class
    clsid = OmniId(element.get('clsid'))
    filter_node = element.find('filternode')
    root = _console_filter_id_class[clsid](filter_node)
    and_node = element.find(_json_andnode)
    if and_node is not None:
        root.and_node = parse_console_filter(and_node)
    or_node = element.find(_json_ornode)
    if or_node is not None:
        root.or_node = parse_console_filter(or_node)
    return root


def store_omni_filter(element, operator, criteria):
    class_name_ids = omniscript.get_class_name_ids()
    class_id = class_name_ids[criteria._class_name]
    filter_node = {}
    criteria._store(filter_node)
    if criteria.and_node is not None:
        store_omni_filter(filter_node, _json_andnode, criteria.and_node)
    if criteria.or_node is not None:
        store_omni_filter(filter_node, _json_ornode, criteria.or_node)
    filter_node[_json_classid] = class_id.format()
    element[operator] = filter_node


LOGICAL_OP_AND = 0
LOGICAL_OP_OR = 1
LOGICAL_OP_NOT = 2

DATA_TYPE_UNDEFINED = 0
DATA_TYPE_NULL = 1
DATA_TYPE_ADDRESS = 2
DATA_TYPE_ANALYSIS_MODULE = 3
DATA_TYPE_CHANNEL = 4
DATA_TYPE_ERROR = 5
DATA_TYPE_LENGTH = 6
DATA_TYPE_LOGICAL_OPERATOR = 7
DATA_TYPE_PATTERN = 8
DATA_TYPE_PORT = 9
DATA_TYPE_PROTOCOL = 10
DATA_TYPE_TCP_DUMP = 11
DATA_TYPE_VALUE = 12
DATA_TYPE_VLAN_MPLS = 13
DATA_TYPE_WAN_DIRECTION = 14
DATA_TYPE_WIRELESS = 15

ERROR_FLAG_CRC = 0x002
ERROR_FLAG_FRAME = 0x004
ERROR_FLAG_OVERSIZE = 0x010
ERROR_FLAG_RUNT = 0x020

directions = ['---', '<--', '-->', '<->']


def _direction_string(first, second):
    return directions[[0, 1][first] + [0, 2][second]]


def _invert_string(inverted):
    return [' ', ' ! '][inverted]


def _make_mask(byte_count, bit_length=32):
    mask = 0
    for i in range(byte_count):
        mask = (mask << 1) | 1
    return mask << (bit_length - byte_count)


def _bytes_to_hex_string(bytes):
    """Return a string of hex characters from a list of
    integers (bytes).

    Args:
        bytes ([int]): list of integers:  [18, 52, 86, 120]

    Returns:
        String: '12345678'
    """
    return ''.join(hex(n)[2:] for n in bytes)


def _hex_string_to_bytes(value):
    """Return a list of single byte intergers from each pair of
    hex characters.

    Args:
        value (string): string of hex characters: '12345678'

    Returns:
        List of integers: [18, 52, 86, 120]
    """
    return [int(value[i:i+2], 16) for i in range(0, len(value), 2)]


def _hex_string_to_shorts(value):
    """Return a list of short intergers from each four hex characters.
    Used to parse IPv6 hex strings into list of 16-bit values.

    Args:
        value (string): string of hex characters: '12345678'

    Returns:
        List of integers: [4660, 22136]
    """
    return [int(value[i:i+4], 16) for i in range(0, len(value), 4)]


def _hex_string_to_string(value):
    """Return a string from each pair of hex characters.

    Args:
        value (string): string of hex characters: '48656C6C6F'

    Returns:
        String: 'Hello'
    """
    return ''.join(chr(int(value[i:i+2], 16)) for i in range(0, len(value), 2)).strip('\0')


def parse_port_list(value):
    if isinstance(value, six.string_types):
        port_list = value.split(' ')
        pl = [OmniPort(p) for p in port_list if p]
        return pl
    else:
        return [OmniPort(value)]


def _string_to_hex_string(value, pad=0):
    """Return a string of hex characters from a string.

    Args:
        value (string): string of hex characters: 'Hello'
        pad: min length of the resulting string.: 8

    Returns:
        String: '48656C6C6F000000'
    """
    result = ''.join('%X' % ord(i) for i in value)
    if len(value) < pad:
        result += ''.join('00' for i in range(8 - len(value)))
    return result


class DataIdType(object):
    """Data Id Type object.
    """

    id = None
    """The GUID of the type as a
    :class:`OmniId <omniscript.omniid.OmniId>` object.
    """

    data_type = DATA_TYPE_UNDEFINED
    """The Named Type. One of the DATA TYPE constants."""

    def __init(self):
        self.id = DataIdType.id
        self.data_type = DataIdType.data_type


class NamedDataType(object):
    """The Named Data Type class.
    """

    name = ''
    """The name of the type."""

    data_type = DATA_TYPE_UNDEFINED
    """The type of data/node. One of the DATA TYPE constants."""

    def __init__(self):
        self.name = NamedDataType.name
        self.data_type = NamedDataType.data_type


class WirelessChannel(object):
    """A wireless channel.
    """

    channel = 0
    """The channel number."""

    frequency = 0
    """The channel's frequency."""

    band = WIRELESS_BAND_ALL
    """The channel's band."""

    _tag_number = 'number'
    _tag_frequency = 'frequency'
    _tag_band = 'band'

    def __init__(self):
        self.channel = WirelessChannel.channel
        self.frequency = WirelessChannel.frequency
        self.band = WirelessChannel.band

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == WirelessChannel._tag_number:
                    self.channel_number = int(v)
                elif k == WirelessChannel._tag_frequency:
                    self.channel_frequency = int(v)
                elif k == WirelessChannel._tag_band:
                    self.channel_band = int(v)


class FilterNode(object):
    """The FilterNode class is the criteria of
    :class:`Filter <omniscript.filter.Filter>` object.
    The other filter node types are subclasses of this class.
    """

    pad_depth = 4
    """The number of bytes of padding per indentation level."""

    nodes = None
    """List of node derived from the
    :class:`FilterNode <omniscript.filternode.FilterNode>`
    class.
    """

    and_node = None
    """The AND node."""

    or_node = None
    """The OR node."""

    comment = None
    """User supplied comment for this node."""

    protospec_path = ''
    """The path of the protospec."""

    option_inverted = False
    """Is the logic of this node inverted?
    Default is False.
    """

    option_slice_to_header = False
    """Slice the packet to header?
    Default is False.
    """

    # Tags
    _json_comment = 'comment'
    _json_inverted = 'inverted'
    _json_slice_to_header = 'sliceToHeader'
    _json_protospec_path = 'protospecPath'

    _tag_comment = 'comment'
    _tag_inverted = 'option_inverted'
    _tag_slice_to_header = 'option_slice_to_header'
    _tag_protospec_path = 'protospec_path'

    _filter_node_prop_dict = {
        _json_comment: _tag_comment,
        _json_inverted: _tag_inverted,
        _json_slice_to_header: _tag_slice_to_header,
        _json_protospec_path: _tag_protospec_path
    }

    def __init__(self):
        # pad_depth is a class property.
        self.nodes = FilterNode.nodes
        self.and_node = FilterNode.and_node
        self.or_node = FilterNode.or_node
        self.comment = FilterNode.comment
        self.protospec_path = FilterNode.protospec_path
        self.option_inverted = FilterNode.option_inverted
        self.option_slice_to_header = FilterNode.option_slice_to_header

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = FilterNode._filter_node_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                if a == FilterNode._tag_comment:
                    self.comment = v
                elif a == FilterNode._tag_protospec_path:
                    self.protospec_path = v
                elif a == FilterNode._tag_inverted:
                    self.option_inverted = v
                elif a == FilterNode._tag_slice_to_header:
                    self.option_slice_to_header = v

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[FilterNode._json_inverted] = self.option_inverted
        if self.comment:
            props[FilterNode._json_comment] = self.comment

    def to_string(self, pad, operation=""):
        text = ''
        if self.and_node:
            text += "\n" + self.and_node.to_string((pad+1), "and: ")
        if self.or_node:
            text += "\n" + self.or_node.to_string(pad, "or: ")
        return text


class ApplicationNode(FilterNode):
    """The ApplicationNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    names = []
    """A list of appliation names"""

    _class_name = 'ApplicationFilterNode'
    _display_name = 'Application'

    _json_names = 'applicationId'

    _tag_names = 'names'

    def __init__(self, props=None):
        super(ApplicationNode, self).__init__()
        self.names = []
        self._load(props)

    def __str__(self):
        return f'{ApplicationNode._class_name}: {self.names}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(ApplicationNode, self)._load(props)
        if ApplicationNode._json_names in props:
            self.names = props[ApplicationNode._json_names]

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ApplicationNode._json_names] = ' '.join(self.names)
        super(ApplicationNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            ApplicationNode._display_name,
            _invert_string(self.option_inverted),
            self.names)
        return criteria + FilterNode.to_string(self, pad)


class AddressNode(FilterNode):
    """The AddressNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    address_1 = None
    """The address of the Node as a
    :class:`OmniAddress <omniscript.omniaddress.OmniAddress>` object."""

    address_2 = None
    """The other address 2 of the Node as a
    :class:`OmniAddress <omniscript.omniaddress.OmniAddress>` object."""

    address_list_1 = None
    """The first address as a list of
    :class:`OmniAddress <omniscript.omniaddress.OmniAddress>` object."""

    address_list_2 = None
    """The second address as a list of
    :class:`OmniAddress <omniscript.omniaddress.OmniAddress>` object."""

    option_accept_1_to_2 = False
    """Accept traffic from the first to the second address."""

    option_accept_2_to_1 = False
    """Accept traffic from the second to the first address."""

    _class_id = OmniId('D2ED5346-496C-4EA0-948E-21CDDA1ED723')
    _class_name = 'AddressFilterNode'
    _display_name = 'Address'

    _json_address_1 = 'address1'
    _json_address_2 = 'address2'
    _json_address_type = 'type'

    _tag_address_1 = 'address_1'
    _tag_address_2 = 'address_2'
    _tag_address_type = 'address_type'
    _tag_accept_1_to_2 = 'option_accept_1_to_2'
    _tag_accept_2_to_1 = 'option_accept_2_to_1'

    _address_node_prop_dict = {
        _json_address_1: _tag_address_1,
        _json_address_2: _tag_address_2,
        _json_address_type: _tag_address_type,
        _json_accept_1_to_2: _tag_accept_1_to_2,
        _json_accept_2_to_1: _tag_accept_2_to_1
    }

    def __init__(self, props=None):
        super(AddressNode, self).__init__()
        self.address_1 = AddressNode.address_1
        self.address_2 = AddressNode.address_2
        self.address_list_1 = AddressNode.address_list_1
        self.address_list_2 = AddressNode.address_list_2
        self.option_accept_1_to_2 = AddressNode.option_accept_1_to_2
        self.option_accept_2_to_1 = AddressNode.option_accept_2_to_1
        self._load(props)

    def __str__(self):
        return (f'{AddressNode._class_name}: '
                f'{self.address_list_1} '
                f'{_direction_string(self.option_accept_1_to_2, self.option_accept_2_to_1)} '
                f'{self.address_list_2}')

    @property
    def accept_1_to_2(self):
        return self.option_accept_1_to_2

    @accept_1_to_2.setter
    def accept_1_to_2(self, value):
        self.option_accept_1_to_2 = bool(value)

    @property
    def accept_2_to_1(self):
        return self.option_accept_2_to_1

    @accept_2_to_1.setter
    def accept_2_to_1(self, value):
        self.option_accept_2_to_1 = bool(value)

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(AddressNode, self)._load(props)
        _address_1 = None
        _address_2 = None
        _address_type = None
        for k, v in props.items():
            a = AddressNode._address_node_prop_dict.get(k)
            # if a is None, then simply no match.
            if a == AddressNode._tag_address_1:
                _address_1 = v
            elif a == AddressNode._tag_address_2:
                _address_2 = v
            elif a == AddressNode._tag_address_type:
                _address_type = int(v)
            elif a == AddressNode._tag_accept_1_to_2:
                self.option_accept_1_to_2 = v
            elif a == AddressNode._tag_accept_2_to_1:
                self.option_accept_2_to_1 = v
        self.address_list_1 = OmniAddress('addr1', _address_1, _address_type).address_list
        self.address_list_2 = OmniAddress('addr2', _address_2, _address_type).address_list

    def _store(self, props):
        if not isinstance(props, dict):
            return
        if isinstance(self.address_1, BaseAddress) and self.address_list_1 is None:
            self.address_list_1 = [self.address_1]
        if isinstance(self.address_2, BaseAddress) and self.address_list_2 is None:
            self.address_list_2 = [self.address_2]
        addr_1 = [str(a) for a in self.address_list_1] if self.address_list_1 else []
        addr_2 = [str(a) for a in self.address_list_2] if self.address_list_2 else []
        _type = (self.address_list_1[0].address_type if self.address_list_1
                 else self.address_list_2[0].address_type if self.address_list_1 else 0)
        props[_json_type] = _type
        props[AddressNode._json_address_1] = ' '.join(addr_1) if addr_1 else ''
        props[AddressNode._json_address_2] = ' '.join(addr_2) if addr_2 else ''
        props[_json_accept_1_to_2] = self.option_accept_1_to_2
        props[_json_accept_2_to_1] = self.option_accept_2_to_1
        super(AddressNode, self)._store(props)

    def to_string(self, pad, operation=""):
        addr_1 = [str(a) for a in self.address_list_1] if self.address_list_1 else []
        addr_2 = [str(a) for a in self.address_list_2] if self.address_list_2 else []
        return (
            f'{"".ljust(pad * FilterNode.pad_depth)}{operation} {AddressNode._display_name}:'
            f'{_invert_string(self.option_inverted)}'
            f'{" ".join(addr_1) if addr_1 else "any"} '
            f'{_direction_string(self.option_accept_1_to_2, self.option_accept_2_to_1)} '
            f'{" ".join(addr_2) if addr_2 else "any"} '
            f'{FilterNode.to_string(self, pad)}'
        )


class BpfNode(FilterNode):
    """The BpfNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    filter = ''
    """The filter's criteria in BPF syntax"""

    _class_name = 'BpfFilterNode'
    _display_name = 'BPF'

    _json_filter = 'bpfData'

    def __init__(self, props=None):
        super(BpfNode, self).__init__()
        self.filter = BpfNode.filter
        self._load(props)

    def __str__(self):
        return f'{BpfNode._class_name}: {self.filter}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(BpfNode, self)._load(props)
        if BpfNode._json_filter in props:
            self.filter = props[BpfNode._json_filter]

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[BpfNode._json_filter] = self.filter
        super(BpfNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            BpfNode._display_name,
            _invert_string(self.option_inverted),
            self.filter)
        return criteria + FilterNode.to_string(self, pad)


class ChannelNode(FilterNode):
    """The ChannelNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    channel = 0
    """The channel."""

    _class_name = 'ChannelFilterNode'
    _display_name = 'Channel'

    _json_channel = 'channel'

    def __init__(self, props=None):
        super(ChannelNode, self).__init__()
        self.channel = ChannelNode.channel
        self._load(props)

    def __str__(self):
        return f'{ChannelNode._class_name}: {self.channel}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(ChannelNode, self)._load(props)
        if ChannelNode._json_channel in props:
            self.channel = int(props[ChannelNode._json_channel])

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ChannelNode._json_channel] = self.channel
        super(ChannelNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%d' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            ChannelNode._display_name,
            _invert_string(self.option_inverted),
            self.channel)
        return criteria + FilterNode.to_string(self, pad)


class CountryNode(FilterNode):
    """The CountryNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    country_1 = None
    """The first country as a String."""

    country_2 = None
    """The second Country as a string."""

    option_accept_1_to_2 = False
    """Accept traffic from the first to the second country."""

    option_accept_2_to_1 = False
    """Accept traffic from the second to the first coutry."""

    _class_name = 'CountryFilterNode'
    _display_name = 'Country'

    country_1 = None
    country_2 = None

    _json_country_1 = 'country1'
    _json_country_2 = 'country2'

    _tag_country_1 = 'country_1'
    _tag_country_2 = 'country_2'
    _tag_accept_1_to_2 = 'option_accept_1_to_2'
    _tag_accept_2_to_1 = 'option_accept_2_to_1'

    _country_node_prop_dict = {
        _json_country_1: _tag_country_1,
        _json_country_2: _tag_country_2,
        _json_accept_1_to_2: _tag_accept_1_to_2,
        _json_accept_2_to_1: _tag_accept_2_to_1
    }

    def __init__(self, props=None):
        super(CountryNode, self).__init__()
        self.country_1 = ''
        self.country_2 = ''
        self.option_accept_1_to_2 = CountryNode.option_accept_1_to_2
        self.option_accept_2_to_1 = CountryNode.option_accept_2_to_1
        self._load(props)

    def __str__(self):
        return (f'{CountryNode._class_name}: '
                f'{self.country_1} '
                f'{_direction_string(self.option_accept_1_to_2, self.option_accept_2_to_1)} '
                f'{self.country_2}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(CountryNode, self)._load(props)
        for k, v in props.items():
            a = CountryNode._country_node_prop_dict.get(k)
            if a == CountryNode._tag_country_1:
                self.country_1 = v
            elif a == CountryNode._tag_country_2:
                self.country_2 = v
            elif a == CountryNode._tag_accept_1_to_2:
                self.option_accept_1_to_2 = v
            elif a == CountryNode._tag_accept_2_to_1:
                self.option_accept_2_to_1 = v

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[CountryNode._json_country_1] = self.country_1
        props[CountryNode._json_country_2] = self.country_2
        props[_json_accept_1_to_2] = self.option_accept_1_to_2
        props[_json_accept_2_to_1] = self.option_accept_2_to_1
        super(CountryNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s %s %s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            CountryNode._display_name,
            _invert_string(self.option_inverted), self.country_1,
            _direction_string(self.option_accept_1_to_2, self.option_accept_2_to_1),
            self.country_2)
        return criteria + FilterNode.to_string(self, pad)


class ErrorNode(FilterNode):
    """The ErrorNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    option_crc_errors = False
    """Cyclical Redundency Check failures?"""

    option_frame_errors = False
    """Framing Error failures?"""

    option_oversize_errors = False
    """Oversized Packets?"""

    option_runt_errors = False
    """Undersized Packets?"""

    _class_name = 'ErrorFilterNode'
    _display_name = 'Error'

    _json_flags = 'errorFlags'

    def __init__(self, props=None):
        super(ErrorNode, self).__init__()
        self.option_crc_errors = ErrorNode.option_crc_errors
        self.option_frame_errors = ErrorNode.option_frame_errors
        self.option_oversize_errors = ErrorNode.option_oversize_errors
        self.option_runt_errors = ErrorNode.option_runt_errors
        self._load(props)

    def __str__(self):
        return (f'{ErrorNode._class_name}: '
                f'c:{self.option_crc_errors}, '
                f'f:{self.option_frame_errors}, '
                f'o:{self.option_oversize_errors}, '
                f'r:{self.option_runt_errors}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(ErrorNode, self)._load(props)
        if ErrorNode._json_flags in props:
            flags = int(props[ErrorNode._json_flags])
            self.option_crc_errors = (flags & ERROR_FLAG_CRC) != 0
            self.option_frame_errors = (flags & ERROR_FLAG_FRAME) != 0
            self.option_oversize_errors = (flags & ERROR_FLAG_OVERSIZE) != 0
            self.option_runt_errors = (flags & ERROR_FLAG_RUNT) != 0

    def _store(self, props):
        errorflags = 0
        errorflags |= [0, ERROR_FLAG_CRC][self.option_crc_errors]
        errorflags |= [0, ERROR_FLAG_FRAME][self.option_frame_errors]
        errorflags |= [0, ERROR_FLAG_OVERSIZE][self.option_oversize_errors]
        errorflags |= [0, ERROR_FLAG_RUNT][self.option_runt_errors]
        props[ErrorNode._json_flags] = errorflags

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %scrc:%s frame:%s oversize:%s runt:%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            ErrorNode._display_name,
            _invert_string(self.option_inverted),
            ['F', 'T'][self.option_crc_errors],
            ['F', 'T'][self.option_frame_errors],
            ['F', 'T'][self.option_oversize_errors],
            ['F', 'T'][self.option_runt_errors])
        return criteria + FilterNode.to_string(self, pad)


class LengthNode(FilterNode):
    """The LengthNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    minimum = 64
    """The minimum length.
    Default is 64 btyes.
    """

    maximum = 1518
    """The maximum lenth.
    Default is 1518 bytes.
    """

    _class_name = 'LengthFilterNode'
    _display_name = 'Length'

    _json_minimum = 'minimumLength'
    _json_maximum = 'maximumLength'

    _tag_minimum = 'minimum'
    _tag_maximum = 'maximum'

    _length_node_prop_dict = {
        _json_minimum: _tag_minimum,
        _json_maximum: _tag_maximum
    }

    def __init__(self, props=None):
        super(LengthNode, self).__init__()
        self.minimum = LengthNode.minimum
        self.maximum = LengthNode.maximum
        if props is not None:
            self._load(props)

    def __str__(self):
        return f'{LengthNode._class_name}: {self.minimum} to {self.maximum}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(LengthNode, self)._load(props)
        for k, v in props.items():
            a = LengthNode._length_node_prop_dict.get(k)
            if a == LengthNode._tag_minimum:
                self.minimum = int(v)
            elif a == LengthNode._tag_maximum:
                self.maximum = int(v)

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[LengthNode._json_minimum] = self.minimum
        props[LengthNode._json_maximum] = self.maximum
        super(LengthNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %smin:%d max:%d' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            LengthNode._display_name,
            _invert_string(self.option_inverted),
            self.minimum,
            self.maximum)
        return criteria + FilterNode.to_string(self, pad)


class LogicalNode(FilterNode):
    """The LogicalNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    operator = 0
    """The logical operator:
        0 - And
        1 - Or
        2 - Not
    """

    left = None
    """The left side opperand.
    """

    right = None
    """The right side opperand.
    """

    _class_name = 'LogicalFilterNode'
    _display_name = 'Logical'
    _op_names = ['and', 'or', 'not']

    _json_operator = 'op'
    _json_left = 'left'
    _json_right = 'right'

    def __init__(self, props=None):
        super(LogicalNode, self).__init__()
        self.operator = LogicalNode.operator
        self.left = LogicalNode.left
        self.right = LogicalNode.right
        self._load(props)

    def __str__(self):
        return f'{LogicalNode._class_name}: {LogicalNode._op_names[self.operator]}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(LogicalNode, self)._load(props)
        if LogicalNode._json_operator in props:
            self.operator = int(props[LogicalNode._json_operator])
        if LogicalNode._json_left in props:
            self.left = parse_omni_filter_dict(props[LogicalNode._json_left])
        if LogicalNode._json_rigth in props:
            self.right = parse_omni_filter_dict(props[LogicalNode._json_right])

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[LogicalNode._json_operator] = self.operator
        if self.left:
            _left = {}
            self.left.store(_left)
            props[LogicalNode._json_left] = _left
        if self.rigth:
            _right = {}
            self.left.store(_right)
            props[LogicalNode._json_right] = _right
        super(LogicalNode, self)._store(props)

    def to_string(self, pad, operation=""):
        _padding = ''.ljust(pad * FilterNode.pad_depth)
        _padding_plus = ''.ljust((pad+1) * FilterNode.pad_depth)

        criteria = '%s%s%s: %s %s\n%sleft:%s\n%sright:%s' % (
            _padding,
            operation,
            LogicalNode._display_name,
            _invert_string(self.option_inverted),
            LogicalNode._op_names[self.operator],
            _padding_plus,
            self.left.to_string(pad+1),
            _padding_plus,
            self.right.to_string(pad+1))
        return criteria + FilterNode.to_string(self, pad)


class PatternNode(FilterNode):
    """The PatternNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    pattern_type = PATTERN_TYPE_ASCII
    """The Pattern type. One of the PATTERN TYPE constants."""

    pattern = ''
    """The pattern to match as ASCII hex.
    1=31, 2=32, 3=33, ...
    a=61, b=62, c=63, ...
    Use set_pattern() to convert strings to ASCII hex.
    """

    start_offset = 0
    """Beginging offset within the packet."""

    end_offset = 1517
    """Ending offset within the packet."""

    protocol_specification = None
    """The protocol specification."""

    flags = None
    """The patter flags."""

    code_page = 0
    """Code page of the pattern."""

    option_case_sensitive = False
    """Is the match case sensitive?"""

    _class_name = 'PatternFilterNode'
    _display_name = 'Pattern'

    _json_pattern_type = 'patternType'
    _json_pattern = 'patternData'
    _json_start_offset = 'startOffset'
    _json_end_offset = 'endOffset'
    _json_code_page = 'codePage'
    _json_case_sensitive = 'caseSensitive'
    _json_protocol_specification = 'pspec'
    _json_flags = 'patternFlags'

    _tag_pattern_type = 'pattern_type'
    _tag_pattern = 'pattern'
    _tag_case_sensitive = 'option_case_sensitive'
    _tag_code_page = 'code_page'
    _tag_start_offset = 'start_offset'
    _tag_end_offset = 'end_offset'
    _tag_protocol_specification = 'protocol_specification'
    _tag_flags = 'flags'

    _pattern_node_prop_dict = {
        _json_pattern_type: _tag_pattern_type,
        _json_pattern: _tag_pattern,
        _json_case_sensitive: _tag_case_sensitive,
        _json_code_page: _tag_code_page,
        _json_start_offset: _tag_start_offset,
        _json_end_offset: _tag_end_offset
    }

    def __init__(self, props=None):
        super(PatternNode, self).__init__()
        self.pattern_type = PatternNode.pattern_type
        self.pattern = PatternNode.pattern
        self.start_offset = PatternNode.start_offset
        self.end_offset = PatternNode.end_offset
        self.option_case_sensitive = PatternNode.option_case_sensitive
        self._load(props)

    def __str__(self):
        return f'{PatternNode._class_name}: {self.pattern}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(PatternNode, self)._load(props)
        for k, v in props.items():
            a = PatternNode._pattern_node_prop_dict.get(k)
            if a == PatternNode._tag_pattern_type:
                self.pattern_type = int(v)
            elif a == PatternNode._tag_pattern:
                self.pattern = v
            elif a == PatternNode._tag_case_sensitive:
                self.option_case_sensitive = v
            elif a == PatternNode._tag_code_page:
                self.code_page = int(v)
            elif a == PatternNode._tag_start_offset:
                self.start_offset = int(v)
            elif a == PatternNode._tag_end_offset:
                self.end_offset = int(v)
            elif a == PatternNode._tag_protocol_specification:
                self.protocol_specification = int(v)
            elif a == PatternNode._tag_flags:
                self.flags = int(v)

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[PatternNode._json_pattern_type] = self.pattern_type
        props[PatternNode._json_pattern] = self.pattern
        props[PatternNode._json_case_sensitive] = self.option_case_sensitive
        props[PatternNode._json_code_page] = 0
        props[PatternNode._json_start_offset] = self.start_offset
        props[PatternNode._json_end_offset] = self.end_offset
        props[PatternNode._json_protocol_specification] = (self.protocol_specification
                                                           if self.protocol_specification
                                                           else 1000)
        props[PatternNode._json_flags] = self.flags if self.flags else 0
        super(PatternNode, self)._store(props)

    def set_pattern(self, value):
        """Sets the pattern attribte to the ASCII hex of value."""
        if isinstance(value, six.string_types):
            self.pattern = ''.join(("%02X" % ord(x)) for x in value)
            self.pattern_type = PATTERN_TYPE_ASCII
        else:
            self.pattern = str(value)
            self.pattern_type = PATTERN_TYPE_ASCII

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s begin:%d end:%d' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            PatternNode._display_name,
            _invert_string(self.option_inverted),
            self.pattern,
            self.start_offset,
            self.end_offset)
        return criteria + FilterNode.to_string(self, pad)


class PluginNode(FilterNode):
    """The PluginNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    ids = []
    """A list of plugin ids as a list of
    :class:`OmniId <omniscript.omniid.OmniId>` objects.
    Use the add_analysis_module function to add items to the list.
    """

    _class_name = 'PluginFilterNode'
    _display_name = 'Plugin'

    _json_ids = 'pluginId'

    def __init__(self, props=None):
        super(PluginNode, self).__init__()
        self.ids = []
        self._load(props)

    def __str__(self):
        return (f'{PluginNode._class_name}: '
                f'{" ".join(i.format() for i in self.ids)}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(PluginNode, self)._load(props)
        if PluginNode._json_ids in props:
            ids = props[PluginNode._json_ids]
            self.ids.append(OmniId(ids))

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[PluginNode._json_ids] = ' '.join(id.format() for id in self.ids)
        super(PluginNode, self)._store(props)

    def add_analysis_module(self, clsid):
        if isinstance(clsid, OmniId):
            self.ids.append(clsid)
        elif isinstance(clsid, six.string_types):
            self.ids.append(OmniId(clsid))
        elif isinstance(clsid, AnalysisModule):
            self.ids.append(clsid.id)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            PluginNode._display_name,
            _invert_string(self.option_inverted),
            f'{" ".join(i.format() for i in self.ids)}')
        return criteria + FilterNode.to_string(self, pad)


class PortNode(FilterNode):
    """The PortNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    port_list_1 = None
    """The first list of
    :class:`OmniPort <omniscript.omniport.OmniPort>` object."""

    port_list_2 = None
    """The second list of
    :class:`OmniPort <omniscript.omniport.OmniPort>` object."""

    option_accept_1_to_2 = False
    """Accept traffic from the first to the second address."""

    option_accept_2_to_1 = False
    """Accept traffic from the second to the first address."""

    _class_name = 'PortFilterNode'
    _display_name = 'Port'

    _json_port_1 = 'port1'
    _json_port_2 = 'port2'

    _tag_port_1 = 'port_1'
    _tag_port_2 = 'port_2'
    _tag_accept_1_to_2 = 'option_accept_1_to_2'
    _tag_accept_2_to_1 = 'option_accept_2_to_1'

    _port_node_prop_dict = {
        _json_port_1: _tag_port_1,
        _json_port_2: _tag_port_2,
        _json_accept_1_to_2: _tag_accept_1_to_2,
        _json_accept_2_to_1: _tag_accept_2_to_1
    }

    def __init__(self, props=None):
        super(PortNode, self).__init__()
        self.port_list_1 = PortNode.port_list_1
        self.port_list_2 = PortNode.port_list_2
        self.option_accept_1_to_2 = PortNode.option_accept_1_to_2
        self.option_accept_2_to_1 = PortNode.option_accept_2_to_1
        self._load(props)

    def __str__(self):
        return (f'{PortNode._class_name}: '
                f'{self.port_1} '
                f'{_direction_string(self.option_accept_1_to_2, self.option_accept_2_to_1)} '
                f'{self.port_2}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(PortNode, self)._load(props)
        for k, v in props.items():
            a = PortNode._port_node_prop_dict.get(k)
            if a == PortNode._tag_port_1:
                self.port_list_1 = parse_port_list(v)
            elif a == PortNode._tag_port_2:
                self.port_list_2 = parse_port_list(v)
            elif a == PortNode._tag_accept_1_to_2:
                self.option_accept_1_to_2 = v
            elif a == PortNode._tag_accept_2_to_1:
                self.option_accept_2_to_1 = v

    def _store(self, props):
        if not isinstance(props, dict):
            return
        port_1 = [str(a) for a in self.port_list_1] if self.port_list_1 else []
        port_2 = [str(a) for a in self.port_list_2] if self.port_list_2 else []
        _type = (self.port_list_1[0].port_type if self.port_list_1
                 else self.port_list_2[0].port_type if self.port_list_2 else 0)
        props[_json_type] = _type
        props[PortNode._json_port_1] = ' '.join(port_1) if port_1 else ''
        props[PortNode._json_port_2] = ' '.join(port_2) if port_2 else ''
        props[_json_accept_1_to_2] = self.option_accept_1_to_2
        props[_json_accept_2_to_1] = self.option_accept_2_to_1
        super(PortNode, self)._store(props)

    def to_string(self, pad, operation=""):
        ports_1 = [str(p) for p in self.port_list_1] if self.port_list_1 else []
        ports_2 = [str(p) for p in self.port_list_2] if self.port_list_2 else []
        return (
            f'{"".ljust(pad * FilterNode.pad_depth)}{operation} {PortNode._display_name}:'
            f'{_invert_string(self.option_inverted)}'
            f'{" ".join(ports_1) if ports_1 else "any"} '
            f'{_direction_string(self.option_accept_1_to_2, self.option_accept_2_to_1)} '
            f'{" ".join(ports_2) if ports_2 else "any"} '
            f'{FilterNode.to_string(self, pad)}'
        )


class ProtocolNode(FilterNode):
    """The ProtocolNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    protocol = 0
    """The protocol to match."""

    _class_name = 'ProtocolFilterNode'
    _display_name = 'Protocol'

    _json_protocol = 'protocol'

    def __init__(self, props=None):
        super(ProtocolNode, self).__init__()
        self.protocol = ProtocolNode.protocol
        self._load(props)

    def __str__(self):
        return f'{ProtocolNode._class_name}: {self.protocol}'

    def _load(self, props):
        if not isinstance(props, dict) or (ProtocolNode._json_protocol not in props):
            return
        super(ProtocolNode, self)._load(props)
        elem = props[ProtocolNode._json_protocol]
        if not isinstance(elem, dict) and (_json_data not in elem):
            return
        data = elem[_json_data]
        if data is not None:
            octets = list(data[x:x+2] for x in range(0, 8, 2))
            octets.reverse()
            self.protocol = int(''.join(octets), 16)

    def _store(self, props):
        if not isinstance(props, dict):
            return
        protocol = f'{self.protocol:08X}'
        octets = list(protocol[x:x+2] for x in range(0, 8, 2))
        octets.reverse()
        elem = {
            'msclass': 1,
            'type': 9,
            'data': ''.join(octets)
        }
        props[ProtocolNode._json_protocol] = elem
        super(ProtocolNode, self)._store(props)

    def set_protocol(self, name):
        name_ids = omniscript.get_protocol_short_name_ids()
        self.protocol = name_ids.get(name, 0)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%d' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            ProtocolNode._display_name,
            _invert_string(self.option_inverted),
            self.protocol)
        return criteria + FilterNode.to_string(self, pad)


class TimeRangeNode(FilterNode):
    """The TimeRangeNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    start = None
    """The start time as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    end = None
    """The end time as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    _class_name = 'TimeRangeFilterNode'
    _display_name = 'TimeRange'

    _json_start = 'start'
    _json_end = 'end'

    def __init__(self, props=None):
        super(TimeRangeNode, self).__init__()
        self.start = TimeRangeNode.start
        self.end = TimeRangeNode.end
        self._load(props)

    def __str__(self):
        return f'{TimeRangeNode._class_name}: {self.start} to {self.end}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(TimeRangeNode, self)._load(props)
        if TimeRangeNode._json_start in props:
            self.start = PeekTime(props[TimeRangeNode._json_start])
        if TimeRangeNode._json_end in props:
            self.start = PeekTime(props[TimeRangeNode._json_end])

    def _store(self, props):
        if not isinstance(props, dict):
            return
        if self.start:
            props[TimeRangeNode._json_start] = self.start
        if self.end:
            props[TimeRangeNode._json_end] = self.end
        super(TimeRangeNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %sstart: %s end: %s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            TimeRangeNode._display_name,
            _invert_string(self.option_inverted),
            str(self.start),
            str(self.end))
        return criteria + FilterNode.to_string(self, pad)


class ValueNode(FilterNode):
    """The ValueNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    value = 0
    """The value to match.
    Default is 0.
    """

    mask = 0xFFFFFFFF
    """The mask to apply to the packet data before the match.
    Default is 0xFFFFFFFF.
    """

    offset = 0
    """The offset within the packet to begin searching.
    Default is 0.
    """

    length = 4
    """The amount of packet data to search.
    Default is 4 bytes.
    """

    operator = VALUE_OPERATOR_EQUAL
    """The match operator. One of the VALUE OPERATOR  constants.
    Default is VALUE_OPERATOR_EQUAL.
    """

    flags = VALUE_FLAG_NETWORK_BYTE_ORDER
    """Flags to contrain the match. A set of VALUE FLAG  constants.
    Default is VALUE_FLAG_NETWORK_BYTE_ORDER.
    """

    _class_name = 'ValueFilterNode'
    _display_name = 'Value'

    _json_value = 'value'
    _json_mask = 'mask'
    _json_offset = 'offset'
    _json_operator = 'valueOperation'
    _json_flags = 'valueFlags'

    _tag_value = 'value'
    _tag_mask = 'mask'
    _tag_offset = 'offset'
    _tag_operator = 'operator'
    _tag_flags = 'flags'

    _value_node_prop_dict = {
        _json_value: _tag_value,
        _json_mask: _tag_mask,
        _json_offset: _tag_offset,
        _json_operator: _tag_operator,
        _json_flags: _tag_flags
    }

    def __init__(self, props=None):
        super(ValueNode, self).__init__()
        self.value = ValueNode.value
        self.mask = ValueNode.mask
        self.offset = ValueNode.offset
        self.length = ValueNode.length
        self.operator = ValueNode.operator
        self.flags = ValueNode.flags
        self._load(props)

    def __str__(self):
        return (f'{ValueNode._class_name}: '
                f'{self.value} '
                f'off:{self.offset} '
                f'len:{self.length}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(ValueNode, self)._load(props)
        for k, v in props.items():
            a = ValueNode._value_node_prop_dict.get(k)
            if a == ValueNode._tag_value:
                if isinstance(v, dict) and (_json_data in v):
                    self.value = int(v[_json_data])
            elif a == ValueNode._tag_mask:
                if isinstance(v, dict) and (_json_data in v):
                    self.mask = int(v[_json_data])
            elif a == ValueNode._tag_offset:
                if isinstance(v, dict) and (_json_data in v):
                    self.offset = int(v[_json_data])
            elif a == ValueNode._tag_operator:
                self.operator = int(v)
            elif a == ValueNode._tag_flags:
                self.flags = int(v)

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ValueNode._json_value] = {
            'type': 4,
            'data': self.value
        }
        props[ValueNode._json_mask] = {
            _json_type: 4,
            _json_data: self.mask
        }
        props[ValueNode._json_offset] = {
            _json_data: 8,
            'pspec': 1000
        }
        props[ValueNode._json_operator] = self.operator
        props[ValueNode._json_flags] = self.flags
        super(ValueNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            ValueNode._display_name,
            _invert_string(self.option_inverted),
            self.value)
        return criteria + FilterNode.to_string(self, pad)


class VlanMplsNode(FilterNode):
    """The VlanMplsNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    ids = None
    """A list of VLAN Ids and Id ranges."""

    labels = None
    """A list of MPLS Labels and Label ranges."""

    _class_name = 'VlanFilterNode'
    _display_name = 'Vlan-Mpls'

    _json_ids = 'ids'
    _json_labels = 'labels'

    def __init__(self, props=None):
        super(VlanMplsNode, self).__init__()
        self.ids = []
        self.labels = []
        self._load(props)

    def __str__(self):
        return f'{VlanMplsNode._class_name}: {self.ids} {self.labels}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(VlanMplsNode, self)._load(props)
        if VlanMplsNode._json_ids in props:
            ids = props[VlanMplsNode._json_ids]
            if isinstance(ids, six.string_types):
                for _id in ids.split(' '):
                    self.add_id(_id)
        if VlanMplsNode._json_labels in props:
            labels = props[VlanMplsNode._json_labels]
            if isinstance(labels, six.string_types):
                for _label in labels.split(' '):
                    self.add_label(_label)

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[VlanMplsNode._json_ids] = ''
        props[VlanMplsNode._json_labels] = ''
        if self.ids:
            props[VlanMplsNode._json_ids] = (' '.join(str(id) if isinstance(id, int)
                                             else '-'.join(str(i) for i in id) for id in self.ids))
        if self.labels:
            props[VlanMplsNode._json_labels] = (' '.join(str(lb) if isinstance(lb, int)
                                                else '-'.join(str(i) for i in lb)
                                                for lb in self.labels))
        super(VlanMplsNode, self)._store(props)

    def add_id(self, id):
        """Add a VLAN Id or Id range."""
        if isinstance(id, int):
            self.ids.append(id)
        elif isinstance(id, six.string_types):
            if id:
                items = id.split('-')
                if len(items) == 1:
                    self.ids.append(int(items[0]))
                elif len(items) > 1:
                    self.ids.append((int(items[0]), int(items[1])))

    def add_ids(self, *ids):
        """Add multiple VLAN Ids and/or Id ranges.
        Either as a string: '10 100-110 256' or a list:
        (10, '100-110', 256).
        If the list contains a range, the range must be quoted.
        """
        if isinstance(ids, list) or isinstance(ids, tuple):
            for id in ids:
                if isinstance(id, int) or isinstance(id, six.string_types):
                    self.add_id(id)
                else:
                    self.add_ids(id)
        elif isinstance(ids, six.string_types):
            for id in ids.split(' '):
                self.add_id(id)

    def add_label(self, label):
        """Add an MPLS Label."""
        if isinstance(label, int):
            self.labels.append(label)
        elif isinstance(label, six.string_types):
            if label:
                items = label.split('-')
                if len(items) == 1:
                    self.labels.append(int(items[0]))
                elif len(items) > 1:
                    self.labels.append((int(items[0]), int(items[1])))

    def add_labels(self, *labels):
        """Add multiple MPLS Labels and/or Label ranges.
        Either as a string: '10 100-110 256' or a list:
        (10, '100-110', 256).
        If the list contains a range, the range must be quoted.
        """
        if isinstance(labels, list) or isinstance(labels, tuple):
            for label in labels:
                if isinstance(label, int) or isinstance(label, six.string_types):
                    self.add_label(label)
                else:
                    self.add_labels(label)
        elif isinstance(labels, six.string_types):
            for label in labels:
                self.add_label(label)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %sIds:%s Labels:%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            VlanMplsNode._display_name,
            _invert_string(self.option_inverted),
            self.ids,
            self.labels)
        return criteria + FilterNode.to_string(self, pad)


class WANDirectionNode(FilterNode):
    """The WANDirectionNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    direction = WAN_DIRECTION_UNDEFINED
    """Direction: to the DCE (1) or to the DTE (2)."""

    _class_name = 'DirectionFilterNode'
    _display_name = 'WAN Direction'

    _json_direction = 'direction'

    def __init__(self, props=None):
        super(WANDirectionNode, self).__init__()
        self.direction = WANDirectionNode.direction
        self._load(props)

    def __str__(self):
        return (f'{WANDirectionNode._class_name}: to '
                f'{["", "DCE", "DTE"][self.direction]}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(WANDirectionNode, self)._load(props)
        if WANDirectionNode._json_direction in props:
            self.direction = int(props[WANDirectionNode._json_direction])

    def _store(self, props):
        if not isinstance(props, dict):
            return
        if self.direction != WAN_DIRECTION_UNDEFINED:
            props[WANDirectionNode._json_direction] = self.direction
        super(WANDirectionNode, self)._store(props)

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            WANDirectionNode._display_name,
            _invert_string(self.option_inverted),
            ['Unknown', 'to DCE', 'to DTE'][self.direction])
        return criteria + FilterNode.to_string(self, pad)


class WirelessNode(FilterNode):
    """The WirelessNode class, subclass of the
    :class:`FilterNode <omniscript.filternode.FilterNode>` class.
    """

    channel_number = None
    """The Channel Number to fileter on."""

    channel_frequency = None
    """The Channel Frequency to fileter on."""

    channel_band = WIRELESS_BAND_ALL
    """The Channel Band to fileter on. One of the WIRELESS BAND constants.
    Default is WIRELESS_BAND_ALL.
    """

    data_rate = None
    """The Data Rate, in megabits per second, to filter as a floating point
    value.
    """

    flags = None
    """The flags. A set of the WIRELESS FLAG constants."""

    signal_minimum = None
    """The Minumum Signal to filter on."""

    signal_maximum = None
    """The Maximum Signal to filter on."""

    noise_minimum = None
    """The Minumum Noise Level to filter on."""

    noise_maximum = None
    """The Maximum Noise Level to filter on."""

    encryption = None
    """Encryption information."""

    decryption = None
    """Decryption information."""

    bssid = None
    """The BSSID to filter on."""

    mask_bssid = 0
    """Mask to constrain the BSSID match."""

    _class_name = 'WirelessFilterNode'
    _display_name = 'Wireless'

    _json_channel = 'channel'
    _json_channel_number = 'channelNumber'
    _json_channel_frequency = 'channelFrequency'
    _json_channel_band = 'channelBand'
    # _json_data_rate = 'dataRate'
    # _json_signal = 'signal'
    # _json_noise = 'noise'
    # _json_encryption = 'encryption'
    # _json_decryption = 'decryption'
    # _json_bssid = 'bssid'
    # _json_flags = 'flags'

    _tag_channel_number = 'channel_number'
    _tag_channel_frequency = 'channel_frequency'
    _tag_channel_band = 'channel_band'

    _wireless_node_prop_dict = {
        _json_channel_number: _tag_channel_number,
        _json_channel_frequency: _tag_channel_frequency,
        _json_channel_band: _tag_channel_band
    }

    def __init__(self, props=None):
        super(WirelessNode, self).__init__()
        self.channel_number = WirelessNode.channel_number
        self.channel_frequency = WirelessNode.channel_frequency
        self.channel_band = WirelessNode.channel_band
        self.data_rate = WirelessNode.data_rate
        self.flags = WirelessNode.flags
        self.signal_minimum = WirelessNode.signal_minimum
        self.signal_maximum = WirelessNode.signal_maximum
        self.noise_minimum = WirelessNode.noise_minimum
        self.noise_maximum = WirelessNode.noise_maximum
        self.encryption = WirelessNode.encryption
        self.decryption = WirelessNode.decryption
        self.bssid = WirelessNode.bssid
        self.mask_bssid = WirelessNode.mask_bssid
        self._load(props)

    def __str__(self):
        return (f'{WirelessNode._class_name}: '
                f'ch:{self.channel_number} '
                f'Hz:{self.channel_frequency} '
                f'band:{self.channel_band}')

    def _load(self, props):
        if not isinstance(props, dict):
            return
        super(WirelessNode, self)._load(props)
        if WirelessNode._json_channel in props:
            channel = props[WirelessNode._json_channel]
            if isinstance(channel, dict):
                for k, v in channel.items():
                    a = WirelessNode._wireless_node_prop_dict.get(k)
                    if a == WirelessNode._tag_channel_number:
                        self.channel_number = int(v)
                    elif a == WirelessNode._tag_channel_frequency:
                        self.channel_frequency = int(v)
                    elif a == WirelessNode._tag_channel_band:
                        self.channel_band = int(v)
        # if 'dataRate' in props:
        #     datarate = props['datarate']
        #     if datarate is not None:
        #         data_rate = int(datarate.get('data', '0'))
        #         self.data_rate = data_rate / 2.0

        # signal = props.find('signal')
        # if signal is not None:
        #     self.signal_minimum = int(signal.get('min', '0'))
        #     self.signal_maximum = int(signal.get('max', '0'))
        # noise = props.find('noise')
        # if noise is not None:
        #     self.noise_minimum = int(noise.get('min', '0'))
        #     self.noise_maximum = int(noise.get('max', '0'))
        # encryption = props.find('encryption')
        # if encryption is not None:
        #     self.encryption = int(encryption.get('data', '0')) != 0
        # decryption = props.find('decryptionerror')
        # if decryption is not None:
        #     self.decryption = int(decryption.get('data', '0')) != 0
        # bssid = props.find('bssid')
        # if bssid is not None:
        #     self.bssid = OmniAddress(bssid)
        # flags = props.find('flagsn')
        # if flags is not None:
        #     self.flags = int(flags.get('data', '0'))

    def _store(self, props):
        if not isinstance(props, dict):
            return
        if self.channel_number is not None:
            props[WirelessNode._json_channel_number] = self.channel_number
            props[WirelessNode._json_channel_frequency] = self.channel_frequency
            props[WirelessNode._json_channel_band] = self.channel_band
        # if self.data_rate is not None:
        #     data_rate = int(self.data_rate * 2)
        #     ET.SubElement(props, 'datarate', {'data':str(data_rate)})
        # if self.signal_minimum is not None:
        #     ET.SubElement(props, 'signal', {'min':str(self.signal_minimum),
        #                                       'max':str(self.signal_maximum)})
        # if self.noise_minimum is not None:
        #     ET.SubElement(props, 'noise', {'min':str(self.noise_minimum),
        #                                      'max':str(self.noise_maximum)})
        # if self.encryption is not None:
        #     ET.SubElement(props, 'encryption',
        #                   {'data':['0', '1'][self.encryption]})
        # if self.decryption is not None:
        #     ET.SubElement(props, 'decryptionerror',
        #                   {'data':['0', '1'][self.decryption]})
        # if self.bssid is not None:
        #     self.bssid._store(props)
        # if self.flags is not None:
        #     ET.SubElement(props, 'flagsn', {'data':str(self.flags)})

    def to_string(self, pad, operation=""):
        criteria = '%s%s%s: %s%s' % (
            ''.ljust(pad * FilterNode.pad_depth),
            operation,
            WirelessNode._display_name,
            _invert_string(self.option_inverted),
            int(self.channel_number) if self.channel_number else '')
        return criteria + FilterNode.to_string(self, pad)


_filter_name_class = [
    ('', None),
    ('AddressFilterNode', AddressNode),
    ('ApplicationFilterNode', ApplicationNode),
    ('BpfFilterNode', BpfNode),
    ('ChannelFilterNode', ChannelNode),
    ('CountryFilterNode', CountryNode),
    ('ErrorFilterNode', ErrorNode),
    ('LengthFilterNode', LengthNode),
    ('LogicalFilterNode', LogicalNode),
    ('PatternFilterNode', PatternNode),
    ('PluginFilterNode', PluginNode),
    ('PortFilterNode', PortNode),
    ('ProtocolFilterNode', ProtocolNode),
    ('TimeRangeFilterNode', TimeRangeNode),
    ('ValueFilterNode', ValueNode),
    ('VlanFilterNode', VlanMplsNode),
    ('DirectionFilterNode', WANDirectionNode),
    ('WirelessFilterNode', WirelessNode)
]

_console_filter_id_class = {
    OmniId('{B4298A64-5A40-4F5F-ABCD-B14BA0F8D9EB}'): None,
    OmniId('{2D2D9B91-08BF-44CF-B240-F0BBADBF21B5}'): AddressNode,
    OmniId('{8C7C9172-82B2-43DC-AAF1-41ED80CE828F}'): ApplicationNode,
    OmniId('{11FC8E5E-B21E-446B-8024-39E41E6865E1}'): BpfNode,
    OmniId('{6E8DAF74-AF0D-4CD3-865D-D559A5798C5B}'): ChannelNode,
    OmniId('{EF8A52E6-233F-4337-AAED-B021CBD8E9E4}'): CountryNode,
    OmniId('{D0BDFB3F-F72F-4AEF-8E17-B16D4D3543FF}'): ErrorNode,
    OmniId('{CF190294-C869-4D67-93F2-9A53FDFAE77D}'): LengthNode,
    OmniId('{D8B5CE02-90CA-48AC-8188-468AC293B9C6}'): None,
    OmniId('{47D49D7C-8219-40D5-9E5D-8ADEAACC644D}'): PatternNode,
    OmniId('{D0329C21-8B27-489F-84D7-C7B783634A6A}'): PluginNode,
    OmniId('{297D404D-3610-4A18-95A2-22768B554BED}'): PortNode,
    OmniId('{F4342DAD-4A56-4ABA-9436-6E3C30DAB1C8}'): ProtocolNode,
    OmniId('{85F2216E-6E65-4AE9-B14B-CC8DF48CAE6A}'): TimeRangeNode,
    OmniId('{838F0E57-0D9F-4095-9C12-F1040C84E428}'): ValueNode,
    OmniId('{1999CC65-01DA-4256-81B4-C303BDE88BDA}'): VlanMplsNode,
    OmniId('{90BAE500-B97B-42B0-9886-0947F34001EF}'): WANDirectionNode,
    OmniId('{899E11AD-1849-40BA-9454-9F03798B3A6C}'): WirelessNode
}

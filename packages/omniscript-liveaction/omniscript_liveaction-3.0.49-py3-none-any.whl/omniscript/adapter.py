"""Adapter class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .invariant import AdapterType
from .omniid import OmniId


_adapt_prop_dict = {
    'AdapterFeatures': 'features',
    'AdapterType': 'adapter_type',
    'address': 'address',
    'channels': 'channels',
    'clsid': 'class_id',
    'defaultLinkSpeed': 'default_link_speed',
    'description': 'description',
    'DeviceName': 'device_name',
    'flags': 'flags',
    'identifier': 'adapter_id',
    'ids': 'ids',
    'InterfaceFeatures': 'interface_features',
    'linkSpeed': 'link_speed',
    'mediaSubType': 'media_sub_type',
    'mediaType': 'media_type',
    'ringBufferSize': 'ring_buffer_size',
    'type': 'adapter_type',
    'WildPacketsAPI': 'wildpackets_api'
}


class Adapter(object):
    """The Adapter class has the attributes of an adapter.
    The
    :func:`get_adapter_list()
    <omniscript.omniengine.OmniEngine.get_adapter_list>`
    function returns a list of Adapter objects.
    """

    adapter_id = ''
    """The adapter's identifier is a string. On Linux it's the port
       name, for instance eth0. On Windows is a four digit code with
       leading zeros are significant and is engine specific.
    """

    adapter_type = AdapterType.UKNOWN
    """The type of adapter. Must be an AdapteryType value."""

    address = '00:00:00:00:00:00'
    """The Ethernet Address of the adapter."""

    class_id = None
    """The adapters Class Id as a GUID."""

    default_link_speed = 0
    """The adapter's default link speed in bits per second."""

    description = ''
    """The decscription/name of the adapter."""

    device_name = ''
    """The device name of the adapter: Broadcom, Intel..."""

    features = 0
    """Features of the adapter. Bit fields."""

    interface_features = 0
    """Interface Features of the adapter. Bit fields."""

    link_speed = 0
    """The link speed of the adapter in bits per second."""

    media_type = 0
    """The Media Type of the adapter."""

    media_sub_type = 0
    """The Media Sub Type of the adapter."""

    ring_buffer_size = 0
    """The size of the ring buffer in bytes."""

    wildpackets_api = False
    """Does the adapter support the WildPackets' Wireless API."""

    adapter_types = (
        'Unknown', 'Network Interface Card', 'File Adapter', 'Plugin Adapter', 'Remote Adapter')

    find_attributes = ('name', 'id', 'device_name', 'type')

    _endpoint = 'Adapters'

    def __init__(self, engine, props):
        self._engine = engine
        self.logger = engine.logger
        self.adapter_id = Adapter.adapter_id
        self.adapter_type = Adapter.adapter_type
        self.address = Adapter.address
        self.class_id = Adapter.class_id
        self.default_link_speed = Adapter.default_link_speed
        self.description = Adapter.description
        self.device_name = Adapter.device_name
        self.features = Adapter.features
        self.interface_features = Adapter.interface_features
        self.link_speed = Adapter.link_speed
        self.media_type = Adapter.media_type
        self.media_sub_type = Adapter.media_sub_type
        self.ring_buffer_size = Adapter.ring_buffer_size
        self.wildpackets_api = Adapter.wildpackets_api
        self._load(props)
        if self.description is None:
            self.description = ''
        if not self.device_name and (self.name == self.adapter_id):
            self.device_name = self.name

    def __repr__(self):
        return f'Adapter: {self.description}'

    def __str__(self):
        return f'Adapter: {self.description}'

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            if len(props) == 2:
                config = props.get('configuration')
                info = props.get('info')
            else:
                config = props
                info = None
            # Set attributes from the configuration (config) dictionary.
            if isinstance(config, dict):
                for k, v in config.items():
                    a = _adapt_prop_dict.get(k)
                    if a is not None and hasattr(self, a):
                        if isinstance(getattr(self, a), six.string_types):
                            setattr(self, a, v if v else '')
                        elif isinstance(getattr(self, a), int):
                            setattr(self, a, int(v) if v else 0)
                        elif isinstance(getattr(self, a), list):
                            setattr(self, a, v)
                        elif isinstance(getattr(self, a), dict):
                            setattr(self, a, v)
                        elif getattr(self, a) is None:
                            setattr(self, a, OmniId(v))
                        else:
                            setattr(self, a, v)
            # Set attributes from the information (info) dictionary.
            if isinstance(info, dict):
                for k, v in info.items():
                    a = _adapt_prop_dict.get(k)
                    if a is not None and hasattr(self, a):
                        if isinstance(getattr(self, a), six.string_types):
                            setattr(self, a, v if v else '')
                        elif isinstance(getattr(self, a), int):
                            setattr(self, a, int(v) if v else 0)
                        elif isinstance(getattr(self, a), list):
                            setattr(self, a, v)
                        elif isinstance(getattr(self, a), dict):
                            setattr(self, a, v)
                        elif getattr(self, a) is None:
                            setattr(self, a, OmniId(v))
                        else:
                            setattr(self, a, v)

    @property
    def name(self):
        """The name/description of the adapter. (Read Only)"""
        return self.description

    def rename(self, new_name):
        self._engine.rename_adapter(self.adapter_type, self.adapter_id, new_name)


def _create_adapter_list(engine, resp):
    lst = []
    adapters = resp['adapters']
    if adapters is not None:
        for props in adapters:
            lst.append(Adapter(engine, props))
    lst.sort(key=lambda x: x.description)
    return lst


def find_all_adapters(adapters, value, attrib=Adapter.find_attributes[0]):
    """Finds all adapters that match the value in the adapters list"""
    if (not adapters) or (attrib not in Adapter.find_attributes):
        return None

    if attrib == 'id':
        _attrib = 'adapter_id'
    elif attrib == 'type':
        _attrib = 'adapter_type'
    else:
        _attrib = attrib

    if isinstance(adapters, list):
        return [i for i in adapters if isinstance(i, Adapter) and getattr(i, _attrib) == value]


def find_adapter(adapters, value, attrib=Adapter.find_attributes[0]):
    """Find the first adapter in the list that matches the criteria."""
    if (not adapters) or (attrib not in Adapter.find_attributes):
        return None

    if len(adapters) == 0:
        return None

    if isinstance(value, Adapter):
        _value = value.adapter_id
        attrib = 'id'
    else:
        _value = value

    if attrib == 'id':
        _attrib = 'adapter_id'
    elif attrib == 'type':
        _attrib = 'adapter_type'
    else:
        _attrib = attrib

    return next((i for i in adapters if getattr(i, _attrib) == _value), None)

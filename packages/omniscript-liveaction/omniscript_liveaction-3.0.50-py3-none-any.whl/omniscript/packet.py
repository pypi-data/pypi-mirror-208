"""Packet class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

import omniscript

from .omniaddress import EthernetAddress, IPv4Address
from .country import Country
from .omniport import OmniPort
from .peektime import PeekTime
# from .readstream import ReadStream

# from .omniscript import get_id_protocol_names


_packet_prop_dict = {
    'absoluteTime': 'timestamp',
    'address1': 'address_1',
    'address2': 'address_2',
    'address3': 'address_3',
    'address4': 'address_4',
    'application': 'application',
    'applicationId': 'application_id',
    'applicationColor': 'application_color',
    'band': 'band',
    'bssid': 'bssid',
    'dataRate': 'data_rate',
    'date': 'date',
    'deltaTime': 'delta_time',
    'destination': 'destination',
    'destinationCity': 'destination_city',
    'destinationCountry': 'destination_country',
    'destinationLatitude': 'destination_latitude',
    'destinationLogical': 'destination_logical',
    'destinationLongitude': 'destination_longitude',
    'destinationPhysical': 'destination_physical',
    'destinationPort': 'destination_port',
    'expert': 'expert',
    'filter': 'filter',
    'flags': 'flags',
    'flags80211': 'flags80211',
    'flowId': 'flow_id',
    'frequency': 'frequency',
    'fullDuplexChannel': 'full_duplex_channel',
    'ipIdentifier': 'ip_identifier',
    'ipLength': 'ip_length',
    'ipTTL': 'ip_ttl',
    'mcs': 'mcs',
    'mpls': 'mpls',
    'noisedBm': 'noise_dbm',
    'noiseStrength': 'noise_strength',
    'packetNumber': 'number',
    'protocol': 'protocol',
    'receiver': 'receiver',
    'relativeTime': 'relative_time',
    'signaldBm': 'signal_dbm',
    'signalStrength': 'signal_strength',
    'size': 'size',
    'sizeBar': 'size_bar',
    'source': 'source',
    'sourceCity': 'source_city',
    'sourceCountry': 'source_country',
    'sourceLatitude': 'source_latitude',
    'sourceLogical': 'source_logical',
    'sourceLongitude': 'source_longitude',
    'sourcePhysical': 'source_physical',
    'sourcePort': 'source_port',
    'spatialStreams': 'spatial_streams',
    'summary': 'summary',
    'summarySource': 'summary_source',
    'transmitter': 'transmitter',
    'vlan': 'vlan',
    'wanDirection': 'wan_direction',
    'wirelessChannel': 'wireless_channel'
}


class Packet(object):
    """The Packet class has packet information.
    The
    :func:`get_packets()
    <omniscript.capture.Capture.get_packets>`
    function returns a list of Packet objects.

    Packet number vs index: the packet number, which starts at 0, is a
    counter of the packets as they are captured. When a packet is
    captured the packet counter becomes the packet number of the packet
    and then the packet counter is incremented.
    The packet index is the index into the list of packets called the
    packet buffer.
    The first index in the packet buffer is 0. The first packet in the
    packet buffer, index 0, always contains the packet with the lowest
    packet number.

    A capture buffer can only hold a finite number of packets. Once
    the buffer  has filled and a new packet is captured then the
    first packet in the packet buffer (index 0) is deleted makeing what
    was the second packet (index 1) into the first packet (index 0).
    And the newly captured packet becomes the last packet in the buffer.

    The first_packet attribute of a
    :class:`Capture <omniscript.capture.Capture>`
    is the packet number of the first packet in the capture buffer.
    """

    address_1 = None
    """The first address."""

    address_2 = None
    """The second address.."""

    address_3 = None
    """The third address.."""

    address_4 = None
    """The fourth address.."""

    application = ''
    """The application."""

    application_id = ''
    """The application identifier."""

    application_color = ''
    """The application color."""

    band = ''
    """The band."""

    bssid = ''
    """The BSSID."""

    data = None
    """The packet data."""

    data_rate = 0
    """The data rate."""

    date = None
    """The packet data."""

    delta_time = None
    """How long it's been since the previous packet."""

    destination = ''
    """Physical desination Ehternet Address."""

    destination_city = ''
    """The destination city of based on Destination Address."""

    destination_country = None
    """The destination country of based on Destination Address."""

    destination_latitude = ''
    """The destination latitude based on Destination Address."""

    destination_logical = ''
    """The logical destination address."""

    destination_longitude = ''
    """The destination longitude based on Destination Address."""

    destination_physical = None
    """The physical destination address."""

    destination_port = None
    """The destination port."""

    expert = ''
    """The ExpertEvent triggered by this packet."""

    filter = ''
    """The Filter used to accept this packet."""

    flags = None
    """The flags."""

    flags80211 = ''
    """The Wireless flags."""

    flow_id = 0
    """The identifier of the flow this packet is in."""

    frequency = ''
    """The frequency the packet was captured at."""

    full_duplex_channel = ''
    """The full duplex channel the packet was captured on."""

    index = 0
    """The packet's index from the starting of the capture buffer."""

    ip_identifier = ''
    """The IP Identifier of the packet."""

    ip_length = 0
    """The length of the IP poertion of the packet."""

    ip_ttl = ''
    """The Time To Live (TTL) of the packet."""

    mcs = ''
    """The MCS of the packet."""

    mpls = ''
    """The MPLS Label of the packet."""

    noise_dbm = ''
    """The noise level in decibals the packet was captured."""

    noise_strength = ''
    """The strength of the noise the packet was captured at."""

    number = 0
    """The packet's number starting from when the capture starts."""

    packet_length = 0
    """The length in bytes of the packet."""

    protocol = ''
    """The packet's protocol."""

    receiver = ''
    """The address of the packet's receiver."""

    relative_time = None
    """The amount of time since the Capture was started."""

    signal_dbm = ''
    """The quality of the wireless signal in decibels."""

    signal_strength = ''
    """The strength of the wireless signal when the packet was captured."""

    size_bar = ''
    """The size bar of the packet."""

    source = ''
    """Physical source MAC Address."""

    source_city = ''
    """The source city of based on Source Address."""

    source_country = None
    """The source country of based on Source Address."""

    source_latitude = ''
    """The source latitude of based on Source Address."""

    source_logical = ''
    """The logical value of the Source Address."""

    source_longitude = ''
    """The source longitude of the Source Address."""

    source_physical = ''
    """The source physical of based on Source Address."""

    source_port = ''
    """The source port of based on Source Address."""

    spatial_streams = ''
    """The spatial streams of the packet."""

    status = 0
    """The packet's status."""

    summary = ''
    """The Summary Information of the packet."""

    summary_source = ''
    """The source of the summary attribute."""

    timestamp = None
    """The packet's timestamp as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    transmitter = ''
    """The address of the wireless transmitter."""

    vlan = ''
    """The VLAN the packet is on."""

    wan_direction = ''
    """The direction of the packet: to server, or from server."""

    wireless_channel = ''
    """The wireless channel the packet was captured on."""

    def __init__(self, number=None, props=None, data=None):
        self.number = number if number and (number > 0) else Packet.number
        self.address_1 = Packet.address_1
        self.address_2 = Packet.address_2
        self.address_3 = Packet.address_3
        self.address_4 = Packet.address_4
        self.application = Packet.application
        self.application_id = Packet.application_id
        self.application_color = Packet.application_color
        self.band = Packet.band
        self.bssid = Packet.bssid
        self.data = Packet.data
        self.data_rate = Packet.data_rate
        self.date = Packet.date
        self.delta_time = Packet.delta_time
        self.destination = Packet.destination
        self.destination_city = Packet.destination_city
        self.destination_country = Packet.destination_country
        self.destination_latitude = Packet.destination_latitude
        self.destination_logical = Packet.destination_logical
        self.destination_longitude = Packet.destination_longitude
        self.destination_physical = Packet.destination_physical
        self.destination_port = Packet.destination_port
        self.expert = Packet.expert
        self.filter = Packet.filter
        self.flags = Packet.flags
        self.flags80211 = Packet.flags80211
        self.flow_id = Packet.flow_id
        self.frequency = Packet.frequency
        self.full_duplex_channel = Packet.full_duplex_channel
        self.index = Packet.index
        self.ip_identifier = Packet.ip_identifier
        self.ip_length = Packet.ip_length
        self.ip_ttl = Packet.ip_ttl
        self.mcs = Packet.mcs
        self.mpls = Packet.mpls
        self.noise_dbm = Packet.noise_dbm
        self.noise_strength = Packet.noise_strength
        self.number = Packet.number
        self.packet_length = Packet.packet_length
        self.protocol = Packet.protocol
        self.receiver = Packet.receiver
        self.relative_time = Packet.relative_time
        self.signal_dbm = Packet.signal_dbm
        self.signal_strength = Packet.signal_strength
        self.size_bar = Packet.size_bar
        self.source = Packet.source
        self.source_city = Packet.source_city
        self.source_country = Packet.source_country
        self.source_latitude = Packet.source_latitude
        self.source_logical = Packet.source_logical
        self.source_longitude = Packet.source_longitude
        self.source_physical = Packet.source_physical
        self.source_port = Packet.source_port
        self.spatial_streams = Packet.spatial_streams
        self.status = Packet.status
        self.summary = Packet.summary
        self.summary_source = Packet.summary_source
        self.timestamp = Packet.timestamp
        self.transmitter = Packet.transmitter
        self.vlan = Packet.vlan
        self.wan_direction = Packet.wan_direction
        self.wireless_channel = Packet.wireless_channel
        self._load(props)
        self._load_data(data)

    def __repr__(self) -> str:
        return f'Packet: {self.index}'

    def __str__(self) -> str:
        return f'Packet: {self.index}'

    @property
    def id(self):
        """The packet's identifier. (Read Only)"""
        return self.number

    @property
    def name(self):
        """The packet's number. (Read Only)"""
        return self.number

    @classmethod
    def get_prop_dict(cls):
        return _packet_prop_dict

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            missed = 0
            for k, v in props.items():
                a = _packet_prop_dict.get(k)
                if a is None or not hasattr(self, a):
                    continue
                if isinstance(getattr(self, a), six.string_types):
                    setattr(self, a, v if v else '')
                elif isinstance(getattr(self, a), int):
                    setattr(self, a, int(v) if v else 0)
                elif getattr(self, a) is None:
                    if a in ('address_1', 'address_2', 'address_3', 'address_4', 'destination',
                             'destination_logical', 'destination_physical', 'source',
                             'source_logical', 'source_physical'):
                        try:
                            setattr(self, a, EthernetAddress(v) if v else None)
                        except Exception:
                            setattr(self, a, v)
                    elif a in ('destination_country', 'source_country'):
                        setattr(self, a, Country(v))
                    elif a in ('destination_logical', 'source_logical'):
                        setattr(self, a, IPv4Address(v) if v else None)
                    elif a in ('destination_port', 'source_port'):
                        setattr(self, a, OmniPort(v) if v else None)
                    elif a in ('date', 'delta_time', 'relative_time', 'timestamp'):
                        setattr(self, a, PeekTime(v) if v else None)
                    elif a == 'flags':
                        setattr(self, a, v if v else [])
                    else:
                        missed += 1
                else:
                    missed += 1000

    def _load_data(self, data):
        if not data:
            return
        self.data = data
        self.packet_length = len(self.data)

    def data_length(self):
        """The number of bytes in the packet."""
        if self.data is not None:
            return len(self.data)
        return 0

    def is_sliced(self):
        """Is the packet sliced."""
        if self.data is None:
            return False
        return len(self.data) < self.packet_length

    def protocol_name(self):
        """The protocol name of the packet."""
        protocol_id_names = omniscript.get_id_protocol_names()
        if self.proto_spec & 0x0FFFF:
            return protocol_id_names[self.proto_spec & 0x0FFFF]
        return 'Unknown'


def _create_packet_list(props, first=0):
    if not isinstance(props, dict):
        return
    lst = []
    packets = props.get('packets')
    if isinstance(packets, list):
        for p in packets:
            lst.append(Packet(props=p))
    return lst

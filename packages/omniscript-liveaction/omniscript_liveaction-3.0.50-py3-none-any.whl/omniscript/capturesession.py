"""CaptureSession class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .omniid import OmniId
from .peektime import PeekTime

from .invariant import SessionDataType, SessionStatisticsType


session_data_types = (
    'utilization-mbps',
    'packets',
    'multicast',
    'packet-sizes',
    'vlan-mpls',
    'protocols-mbps',
    'protocols-pps',
    'call-quality',
    'call-utilization',
    'wireless-packets',
    'wireless-retries',
    'applications-mbps',
    'applications-pps'
)

session_statistics_types = (
    'top-applications',
    'top-ipv4-nodes',
    'top-ipv6-nodes',
    'top-physical-nodes',
    'top-protocols'
)


# class SessionData(object): ...
# class SessionStatistics(object): ...
# class ApplicationsData(object): ...
# class CallQualityData(object): ...
# class CallUtilizationData(object): ...
# class MulticastData(object): ...
# class PacketsData(object): ...
# class PacketSizeData(object): ...
# class ProtocolsData(object): ...
# class UtilizationData(SessionData): ...
# class VlanMplsData(object): ...
# class WirelessData(object): ...
# class StatisticsEntry(object): ...


def _decode_color(value):
    return int(value.strip('#'), 16)


def _format_color(color):
    return f'#{color:6X}' if color else '#000000'


class ApplicationsData(object):
    """An Applications Data object.
    """

    application_id = 0.0
    """The identifier of the application."""

    others = 0.0
    """The others of the applications."""

    total_packets = 0
    """The total number of packets in the data."""

    def __init__(self, props):
        self.application_id = 0.0
        self.others = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.application_id = float(props.get('appid', 0.0))
            self.others = float(props.get('others', 0.0))
            self.total_packets = int(props.get('totalPackets', 0))

    def format(self):
        return f'app id: {self.application_id}, other: {self.others}, pkts: {self.total_packets}'


class CallQualityData(object):
    """A Call Quality Data object.
    """

    bad = 0.0
    """The number of bad quality calls."""

    fair = 0.0
    """The number of fair quality calls."""

    good = 0.0
    """The number of good quality calls."""

    poor = 0.0
    """The number of poor quality calls."""

    unknown = 0.0
    """The number of unkown quality calls."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.bad = 0.0
        self.fair = 0.0
        self.good = 0.0
        self.poor = 0.0
        self.unknown = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.bad = float(props.get('bad', 0.0))
            self.fair = float(props.get('fair', 0.0))
            self.good = float(props.get('good', 0.0))
            self.poor = float(props.get('poor', 0.0))
            self.unknown = float(props.get('unknown', 0.0))
            self.packets = int(props.get('totalPackets', 0))

    def format(self):
        return (f'bad: {self.bad}, fair: {self.fair}, good: {self.good}, poor: {self.poor}, '
                f'unknown: {self.unknown}, pkts: {self.total_packets}')


class CallUtilizationData(object):
    """A Call Utilization Data object.
    """

    call_mbps = 0.0
    """The amount of traffic of the calls in megabits per second."""

    mbps = 0.0
    """The speed of traffic in megabits per second."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.call_mbps = 0.0
        self.mbps = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.call_mbps = float(props.get('callMbps', 0.0))
            self.mbps = float(props.get('mbps', 0.0))
            self.packets = int(props.get('totalPackets', 0))

    def format(self):
        return f'call: {self.call_mbps}, mbps: {self.mbps}, pkts: {self.total_packets}'


class PacketsData(object):
    """A Packets Data object.
    """

    packets = 0.0
    """The number of packets."""

    dropped = 0.0
    """The number of dropped packets."""

    crc = 0.0
    """The number of crc errors."""

    undersize = 0.0
    """The number of under-sized packets."""

    oversize = 0.0
    """The number of over-sized packets."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.packets = 0.0
        self.dropped = 0.0
        self.crc = 0.0
        self.undersize = 0.0
        self.oversize = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.packets = float(props.get('packets', 0.0))
            self.dropped = float(props.get('dropped', 0.0))
            self.crc = float(props.get('crc', 0.0))
            self.undersize = float(props.get('undersize', 0.0))
            self.oversize = float(props.get('oversize', 0.0))
            self.total_packets = int(props.get('totalPackets', 0))

    def format(self):
        return f'pkts: {self.total_packets}'


class PacketSizeData(object):
    """A PacketSizeData object.
    """

    size_range = ''
    """The range of packet sizes."""

    packets = 0.0
    """The packet count."""

    pct = 0.0
    """The pct."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.size_range = ''
        self.packets = 0.0
        self.pct = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.size_range = props.get('entry, 0.0')
            self.packets = float(props.get('packets', 0.0))
            self.pct = float(props.get('pct', 0.0))
            self.total_packets = int(props.get('totalPackets', 0))

    def format(self):
        return (f'range: {self.size_range}, p: {self.packets}, pct: {self.pct}, '
                f'pkts: {self.total_packets}')


class ProtocolsData(object):
    """A ProtocolsData object.
    """

    icmp = 0.0
    """The number packets of the ICMP protocol."""

    ipv4 = 0.0
    """The number of IPv4 packets."""

    ipv6 = 0.0
    """The number of IPv6 packets."""

    tcp = 0.0
    """The number packets of the TCP protocol."""

    udp = 0.0
    """The number packets of the UDP protocol."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.icmp = 0.0
        self.ipv4 = 0.0
        self.ipv6 = 0.0
        self.tcp = 0.0
        self.udp = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.icmp = float(props.get('icmp', 0.0))
            self.ipv4 = float(props.get('ipv4', 0.0))
            self.ipv6 = float(props.get('ipv6', 0.0))
            self.tcp = float(props.get('tcp', 0.0))
            self.udp = float(props.get('udp', 0.0))
            self.packets = int(props.get('totalPackets', 0))

    def format(self):
        return (f'icmp: {self.icmp}, ipv4: {self.ipv4}, ipv6: {self.ipv6}, tcp: {self.tcp}, '
                f'udp: {self.udp}, pkts: {self.total_packets}')


class MulticastData(object):
    """A MulticastData object.
    """

    broadcast = 0.0
    """The number of broadcast packets."""

    multicast = 0.0
    """The number of multicast packets."""

    unicast = 0.0
    """The number of unicast packets."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.broadcast = 0.0
        self.multicast = 0.0
        self.unicast = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.broadcast = float(props.get('broadcast', 0.0))
            self.multicast = float(props.get('multicast', 0.0))
            self.unicast = float(props.get('unicast', 0.0))
            self.total_packets = int(props.get('totalPackets', 0))

    def format(self):
        return (f'broad: {self.broadcast}, multi: {self.multicast}, uni: {self.unicast}, '
                f'pkts: {self.total_packets}')


class UtilizationData(object):
    """A UtilizationData object.
    """

    mbps = 0.0
    """The traffic utilization in megabits per second."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.mbps = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.mbps = float(props.get('mbps', 0.0))
            self.total_packets = int(props.get('totalPackets', 0))

    def format(self):
        return f'mbps: {self.mbps}, pkts: {self.total_packets}'


class VlanMplsData(object):
    """A VlanMplsData object.
    """

    mpls = 0.0
    """The number of MPLS packets."""

    packets = 0.0
    """The number of packets."""

    vlan = 0.0
    """The number of VLAN packets."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.mpls = 0.0
        self.packets = 0.0
        self.vlan = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.mpls = float(props.get('mpls', 0.0))
            self.packets = float(props.get('packets', 0.0))
            self.vlan = float(props.get('vlan', 0.0))
            self.total_packets = int(props.get('total_packets', 0))

    def format(self):
        return (f'mpls: {self.mpls}, p: {self.packets}, vlan: {self.vlan}, '
                f'pkts: {self.total_packets}')


class WirelessData(object):
    """A WirelessData object.
    """

    call_mbps = 0.0
    """The utilization of wireless data in megabits per second."""

    control = 0.0
    """The number of control packets."""

    data = 0.0
    """The number of data packets."""

    management = 0.0
    """The number of management packets."""

    packets = 0.0
    """The number of packets."""

    retry = 0.0
    """The number of retry packets."""

    total_packets = 0
    """The total number of packets."""

    def __init__(self, props):
        self.call_mbps = 0.0
        self.control = 0.0
        self.data = 0.0
        self.management = 0.0
        self.packets = 0.0
        self.retry = 0.0
        self.total_packets = 0
        if isinstance(props, dict):
            self.call_mbps = float(props.get('callMbps', 0.0))
            self.control = float(props.get('control', 0.0))
            self.data = float(props.get('data', 0.0))
            self.management = float(props.get('management', 0.0))
            self.packets = float(props.get('packets', 0.0))
            self.retry = float(props.get('retry', 0.0))
            self.total_packets = int(props.get('totalPackets', 0))

    def format(self):
        return (f'call: {self.call_mbps}, ctrl: {self.control}, d: {self.data}, '
                f'man: {self.management}, p: {self.packets}, re: {self.retry}, '
                f'pkts: {self.total_packets}')


class SessionData(object):
    """Session Data object.
    """

    session_id = 0
    """The session id of the data."""

    data_type = 0
    """The type of the data."""

    start_time = None
    """The timestamp of the start of the data."""

    end_time = None
    """The timestamp of the end of the data."""

    sample_interval = 0
    """The interval in seconds between samples."""

    sample_count = 0
    """"The number of samples in the data."""

    data_list = None
    """The list of samples."""

    def __init__(self, session, props):
        self._session = session
        self.session_id = 0
        self.data_type = None
        self.start_time = None
        self.end_time = None
        self.sample_interval = 0
        self.sample_count = None
        self.data_list = None
        self._load(props)

    def _load(self, props):
        if not isinstance(props, dict):
            return
        self.session_id = int(props.get('sessionId', 0))
        self.data_type = SessionDataType(props.get('viewType', 0))
        self.start_time = PeekTime(props.get('startTime', 0))
        self.end_time = PeekTime(props.get('startTime', 0))
        self.sample_interval = int(props.get('sampleInterval', 0))
        self.data_list = None
        if self.data_type == SessionDataType.UTILIZATION_MBPS:
            self.data_list = [UtilizationData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.PACKETS:
            self.data_list = [PacketsData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.MULTICAST:
            self.data_list = [MulticastData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.PACKET_SIZES:
            self.sample_count = int(props.get('sampleCount'))
            self.data_list = [PacketSizeData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.VLAN_MPLS:
            self.data_list = [VlanMplsData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.PROTOCOLS_MBPS:
            self.data_list = [ProtocolsData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.PROTOCOLS_PPS:
            self.data_list = [ProtocolsData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.CALL_QUALITY:
            self.data_list = [CallQualityData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.CALL_UTILIZATION:
            self.data_list = [CallUtilizationData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.WIRELESS_PACKETS:
            self.data_list = [WirelessData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.WIRELESS_RETRIES:
            self.data_list = [WirelessData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.APPLICATIONS_MBPS:
            self.data_list = [ApplicationsData(d) for d in props.get('data')]
        elif self.data_type == SessionDataType.APPLICATIONS_PPS:
            self.data_list = [ApplicationsData(d) for d in props.get('data')]
        else:
            raise ValueError('Invalid data_type')


class SessionStatistics(object):
    """A SessionStatistics object.
    """

    _session = None
    """The CaptureSession object the statistics belong to."""

    statistics_type = None
    """The type of statistics."""

    start_time = None
    """The timestamp of when the CaptureSession began."""

    end_time = None
    """"The timestamp of when the CaptureSession ended."""

    total_bytes = None
    """The total number of bytes in the CaptureSession."""

    entry_list = None
    """The list of statistics objects of the CaptureSession."""

    def __init__(self, session, statistics_type, props):
        self._session = session
        self.statistics_type = statistics_type
        self.start_time = None
        self.end_time = None
        self.total_bytes = None
        self.entry_list = None
        self._load(props)

    def _load(self, props):
        if not isinstance(props, dict):
            return
        self.start_time = PeekTime(props.get('startTime', 0))
        self.end_time = PeekTime(props.get('endTime', 0))
        self.total_bytes = int(props.get('sampleInterval', 0))
        self.entry_list = [StatisticsEntry(e) for e in props.get('entries')]


class StatisticsEntry(object):
    """A StatisticsEntry object.
    """

    entry = ''
    """A CaptureSession Statistics Entry object."""

    name = ''
    """"The name of the StatisticsEntry."""

    color = 0
    """"The color of the StatisticsEntry."""

    bytes = 0
    """"The number of byte of traffic data in the StatisticsEntry."""

    pct = 0.0
    """The pct of the StatisticsEntry."""

    total_bytes = None
    """The total number of bytes of traffic in the StatisticsEntry."""

    def __init__(self, props):
        self.entry = ''
        self.name = ''
        self.color = 0
        self.bytes = 0
        self.pct = 0.0
        self.total_bytes = None
        if isinstance(props, dict):
            self.entry = props.get('entry', '')
            self.name = props.get('name', '')
            self.color = int(props.get('color', '0').strip('#'), 16)
            self.bytes = int(props.get('bytes', 0))
            self.pct = float(props.get('pct', 0.0))
            self.total_bytes = int(props.get('totalBytes', 0))


class CaptureSession(object):
    """Information about a Capture Session.
    """

    _engine = None
    """The engine this capture belongs to."""

    adapter_address = ''
    """The Ethernet address of the adapter."""

    adapter_name = ''
    """The name of the adapter."""

    capture_flags = 0
    """The status flags of the capture."""

    capture_id = None
    """The Id (GUID/UUID) of the Capture that created the file as a
    :class:`OmniId <omniscript.omniid.OmniId>` object.
    """

    alt_capture_id = None
    """The Id (GUID/UUID) of the Capture that created the file as a
    :class:`OmniId <omniscript.omniid.OmniId>` object.
    """

    capture_state = 0
    """The statw of the capture."""

    capture_type = 0
    """The type of the capture."""

    capture_units = 0
    """The measurment units of the capture."""

    dropped_packet_count = 0
    """The number of dropped packets."""

    link_speed = 0
    """The link speed of the adapter."""

    media_type = 0
    """The Media Type of the adapter."""

    media_sub_type = 0
    """The Media Sub Type of the adapter."""

    name = ''
    """The name of the file."""

    owner = ''
    """The owner of the session."""

    packet_count = 0
    """The number of packets in the file."""

    session_id = 0
    """The session's numeric (integer) identifier."""

    session_start_time = None
    """The timestamp of when the session was started as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    start_time = None
    """The timestamp of the first packet in the file as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    storage_units = 0
    """The number of storage units used by the session."""

    stop_time = None
    """The timestamp of the last packet in the file as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    total_byte_count = 0
    """The total number of bytes in the session."""

    total_dropped_packet_count = 0
    """The total number of packets dropped in the session."""

    total_packet_count = 0
    """The total number of packets in the session."""

    _capture_session_prop_dict = {
        'AdapterAddr': 'adapter_address',
        'AdapterName': 'adapter_name',
        'CaptureFlags': 'capture_flags',
        'CaptureID': 'alt_capture_id',
        'CaptureGUID': 'capture_id',
        'CaptureState': 'capture_state',
        'CaptureType': 'capture_type',
        'CaptureUnits': 'capture_units',
        'DroppedCount': 'dropped_packet_count',
        'LinkSpeed': 'link_speed',
        'MediaType': 'media_type',
        'MediaSubType': 'media_sub_type',
        'Name': 'name',
        'Owner': 'owner',
        'PacketCount': 'packet_count',
        'SessionID': 'session_id',
        'SessionStartTimestamp': 'session_start_time',
        'StartTimestamp': 'start_time',
        'StorageUnits': 'storage_units',
        'StopTimestamp': 'stop_time',
        'TotalByteCount': 'total_byte_count',
        'TotalDroppedCount': 'total_dropped_packet_count',
        'TotalPacketCount': 'total_packet_count'
        }

    def __init__(self, engine, props):
        self._engine = engine
        self.adapter_address = CaptureSession.adapter_address
        self.adapter_name = CaptureSession.adapter_name
        self.capture_flags = CaptureSession.capture_flags
        self.capture_id = CaptureSession.capture_id
        self.capture_state = CaptureSession.capture_state
        self.capture_type = CaptureSession.capture_type
        self.capture_units = CaptureSession.capture_units
        self.dropped_packet_count = CaptureSession.dropped_packet_count
        self.link_speed = CaptureSession.link_speed
        self.media_type = CaptureSession.media_type
        self.media_sub_type = CaptureSession.media_sub_type
        self.name = CaptureSession.name
        self.owner = CaptureSession.owner
        self.packet_count = CaptureSession.packet_count
        self.session_id = CaptureSession.session_id
        self.session_start_time = CaptureSession.session_start_time
        self.start_time = CaptureSession.start_time
        self.storage_units = CaptureSession.storage_units
        self.stop_time = CaptureSession.stop_time
        self.total_byte_count = CaptureSession.total_byte_count
        self.total_dropped_packet_count = CaptureSession.total_dropped_packet_count
        self.total_packet_count = CaptureSession.total_packet_count
        self._load(props)

    def __str__(self):
        return f'CaptureSession: {self.name if self.name else ""}'

    def _load(self, props):
        """Load the CaptureSession information from the row of an
        :class:`OmniDataTable <omniscript.omnidatatabel.OmniDataTable>`.
        """
        if isinstance(props, dict):
            for k, v in props.items():
                a = CaptureSession._capture_session_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if isinstance(getattr(self, a), six.string_types):
                        setattr(self, a, v if v else '')
                    elif isinstance(getattr(self, a), int):
                        setattr(self, a, int(v) if v else 0)
                    elif getattr(self, a) is None:
                        if a == 'capture_id' or a == 'alt_capture_id':
                            setattr(self, a, OmniId(v))
                        elif (a == 'session_start_time'
                              or a == 'start_time'
                              or a == 'stop_time'):
                            setattr(self, a, PeekTime(v))

    def _perf(self, msg):
        """Log a performance message."""
        return (self._engine._perf_logger.perf(msg)
                if self._engine and self._engine._perf_logger else None)

    def get_data(self, data_type):
        """Get the a
        :class:`CaptureSession <omniscript.capturesession.CaptureSession>`.

        Returns:
            A
            :class:`CaptureSession <omniscript.capturesession.CaptureSession>`
            object.
        """
        if not self._engine:
            raise ValueError('CaptureSession improperly initialized, no OmniEngine reference.')

        if isinstance(data_type, SessionDataType):
            dt = session_data_types[data_type]
        elif isinstance(data_type, int):
            dt = session_data_types[SessionDataType(data_type)]
        elif isinstance(data_type, six):
            dt = data_type.lower()
            if dt not in session_data_types:
                raise TypeError('The value of data_type is not supported')
        else:
            raise TypeError('data_type is not a supported type')

        pr = self._perf('get_capture_session_data')
        cmd = f'capture-sessions/{self.session_id}/{dt}/'
        props = self._engine._issue_command(cmd, pr)
        return SessionData(self, props) if props else None

    def get_statistics(self, statistics_type, start, end):
        """Get the a statistics from the Capture Session of the type
        specified.

        Returns:
            A
            :class:`SessionStatistics <omniscript.capturesession.SessionStatistics>`
            object.
        """
        if not self._engine:
            raise ValueError('CaptureSession improperly initialized, no OmniEngine reference.')

        if isinstance(statistics_type, SessionStatisticsType):
            st = session_statistics_types[statistics_type]
        elif isinstance(statistics_type, int):
            st = session_statistics_types[SessionStatisticsType(statistics_type)]
        elif isinstance(statistics_type, six):
            st = statistics_type.lower()
            if st not in session_statistics_types:
                raise TypeError('The value of statistics_type is not supported')
        else:
            raise TypeError('statistics_type is not a supported type')

        req_props = {
            'start': start.iso_time(),
            'end': end.iso_time()
        }
        pr = self._perf('get_capture_session_statistics')
        cmd = f'capture-sessions/{self.session_id}/{st}/'
        props = self._engine._issue_command(cmd, pr, params=req_props)
        return SessionStatistics(self, st, props) if props else None


def _create_capture_session_list(engine, props):
    """Create a List of CaptureSession objects from a Dictionary."""
    lst = None
    if isinstance(props, dict):
        rows = props.get('rows')
        if isinstance(rows, list):
            lst = []
            for r in rows:
                cs = CaptureSession(engine, r)
                lst.append(cs)
        lst.sort(key=lambda x: x.name)
    return lst

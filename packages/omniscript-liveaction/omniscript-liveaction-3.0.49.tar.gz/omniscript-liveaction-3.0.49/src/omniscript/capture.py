"""Capture class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import xml.etree.ElementTree as ET

from .invariant import (
    CAPTURE_STATUS_CAPTURING, DECODE_PLAIN_TEXT, DECODE_HTML, DECODE_TAG_STREAM)

from .adapter import Adapter
# from .callstatistic import CallStatistic
from .capturetemplate import CaptureTemplate
# from .expertquery import ExpertQuery
# from .expertresult import ExpertResult
from .invariant import EngineDataFormat as DF, EngineOperation as EO
from .mediainformation import MediaInformation
# from .nodestatistic import NodeStatistic
from .omnierror import OmniError
from .omniid import OmniId
from .packet import Packet
from .peektime import PeekTime
# from .protocolstatistic import ProtocolStatistic
# from .readstream import ReadStream
# from .statscontext import StatsContext
# from .summarystatistic import SummaryStatistic

# from .expertresult import _create_expert_result_list
from .packet import _create_packet_list


status_map = {
    0: 'Idle',
    1: 'Capturing',
    256: 'Idle Start Active',
    257: 'Wait Start',
    8192: 'Idle Stop Active',
    8193: 'Capturing Stop Active',
    8448: 'Idle Start and Stop Active',
    8449: 'Start Stop Active'
}

jtrue = 'true'
jfalse = 'false'


def jbool(b):
    """Returns 'true' if 'b' is True else 'false'."""
    return jtrue if b else jfalse


def _summary_xml_to_stats_list(xml):
    # TODO: change the inner lists to tuples.
    type_dict = [
        [''],
        ['date'],
        ['time'],
        ['duration'],
        ['packets'],
        ['bytes'],
        ['packets', 'bytes'],
        ['int'],
        ['double']
    ]
    element = ET.fromstring(xml)
    lst = []
    snapshot = element.find('summarystats/snapshot')
    for stat in snapshot:
        stat_type = int(stat.attrib['type'])
        s = {
            'id': stat.attrib['id'],
            'parent': stat.attrib['parent'],
            'type': stat_type,
            'flags': int(stat.attrib['flags'])
        }
        if stat_type >= 1 and stat_type <= len(type_dict):
            for t in type_dict[stat_type]:
                s[t] = stat.attrib[t]
        # lst.append(SummaryStatistic(s))
    return lst


_capture_prop_dict = {
    'adapter': 'adapter_name',
    'adapterId': 'adapter_id',
    'adapterInfo': 'adapter',
    'adapterType': 'adapter_type',
    'alarmsEnabled': 'option_alarms',
    'alarmsInfo': 'alarms_info',
    'alarmsMajor': 'alarms_major',
    'alarmsMinor': 'alarms_minor',
    'alarmsSevere': 'alarms_severe',
    'analysisDroppedPackets': 'analysis_dropped_packets',
    'bufferCapacity': 'buffer_size',
    'capacityAvailable': 'buffer_available',
    'capacityUsed': 'buffer_used',
    'captureId': 'group_id',
    'captureSessionId': 'session_id',
    'comment': 'comment',
    'creationTime': 'creation_time',
    'creator': 'creator',
    'creatorSID': 'creator_sid',
    'ctdEnabled': 'option_ctd',
    'ctdIntelligent': 'option_ctd_intelligent',
    'ctdSize': 'file_size',
    'ctdStartTime': 'ctd_start_time',
    'ctdStopTime': 'ctd_stop_time',
    'dataPacketCount': '_data_packet_count',
    'dataPacketsDropped': 'data_packets_dropped',
    'dataSize': 'data_size',
    'dataSizeReserved': 'data_size_reserved',
    'dataStartTime': 'data_start_time',
    'dataStopTime': 'data_stop_time',
    'distributedCapture': 'option_distributed',
    'duplicatePacketsDiscarded': 'duplicate_packets_discarded',
    'duration': 'duration',
    'elkCapture': 'option_elk',
    'errorCondition': 'error_code',
    'errorConditionText': 'error_code_text',
    'expertEnabled': 'option_expert',
    'filterIdsEnabled': 'filter_list',
    'filterMode': 'filter_mode',
    'filtersEnabled': 'option_filters',
    'firstPacket': 'first_packet',
    'flowsDropped': 'flows_dropped',
    'graphsCount': 'graphs_count',
    'graphsEnabled': 'option_graphs',
    'groupID': 'group_id',
    'hardwareDeduplication': 'option_hardware_deduplication',
    'hardwareFiltering': 'option_hardware_filtering',
    'hardwareProfileID': 'hardware_profile_id',
    'hardwareProfileName': 'hardware_profile',
    'hardwareSlicing': '',
    'hidden': 'option_hidden',
    'id': 'id',
    'indexingEnabled': 'option_indexing',
    'linkSpeed': 'link_speed',
    'loggedOnUserSid': 'logged_on_user_sid',
    'mediaInfo': 'media_information',
    'mediaSubType': 'media_sub_type',
    'mediaType': 'media_type',
    'modificationBy': 'modified_by',
    'modificationTime': 'modification_time',
    'modificationType': 'modification_type',
    'multiStream': 'option_multistream',
    'name': 'name',
    'packetBufferEnabled': 'option_packet_buffer',
    'packetCount': 'packet_count',
    'packetsAnalyzed': 'packets_analyzed',
    'packetsDropped': 'packets_dropped',
    'packetsFiltered': 'packets_filtered',
    'packetsReceived': 'packets_received',
    'pluginsEnabled': 'plugin_list',
    'resetCount': 'reset_count',
    'spotlightCapture': 'option_spotlight',
    'startTime': 'start_time',
    'statsEnabled': 'option_stats',
    'status': 'status',
    'stopTime': 'stop_time',
    'threatEyeNVCapture': 'option_threateye',
    'timelineStatsEnabled': 'option_timeline_stats',
    'triggerCount': 'trigger_count',
    'triggerDuration': 'trigger_duration',
    'voiceEnabled': 'option_voice',
    'webEnabled': 'option_web'
}


class Capture(object):
    """The Capture class has the attributes of a capture.
    The functions :func:`create_capture()
    <omniscript.omniengine.OmniEngine.create_capture>`
    and :func:`find_capture() <omniscript.omniengine.OmniEngine.find_capture>`
    return a Capture object.
    The function :func:`get_capture_list()
    <omniscript.omniengine.OmniEngine.get_capture_list>`
    returns a list of Capture objects.
    """

    _engine = None
    """The engine this capture belongs to."""

    adapter = None
    """The :class:`Adapter <omniscript.adapter.Adapter>` object of the
    capture.
    """

    adapter_id = ''
    """The type of adapter being used by the capture."""

    adapter_name = ''
    """The name of the capture's adapter."""

    adapter_type = 0
    """The type, as an integer, of adapter being used by the capture."""

    alarms_info = 0
    """The number of Information alarms that have been triggered."""

    alarms_major = 0
    """The number of Major alarms that have been triggered."""

    alarms_minor = 0
    """The number of Minor alarms that have been triggered."""

    alarms_severe = 0
    """The number of Severe alarms that have been triggered."""

    analysis_dropped_packets = 0
    """The number of packets that were not analysied. (Need to confirm.)"""

    buffer_available = 0
    """The amount of unused space, in bytes, in the capture's buffer."""

    buffer_size = 0
    """The size of the capture's buffer in bytes."""

    buffer_used = 0
    """The number of bytes in use of the capture's buffer."""

    comment = ''
    """The capture's comment."""

    creation_time = None
    """When the capture was created as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    creator = ''
    """The name of the account that created the capture."""

    creator_sid = ''
    """The Security Id of the account that created the capture."""

    ctd_start_time = None
    """The time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    when Capture to Disk data started being saved.
    """

    ctd_stop_time = None
    """The time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    when Capture to Disk data stopped being saved.
    """

    data_packet_count = 0
    """The number of packets saved to disk."""

    data_packets_dropped = 0
    """The number of packets dropped while saving to disk."""

    data_size = 0
    """The size, in bytes, of the packet files when they are saved to
    disk.
    """

    data_size_reserved = 0
    """The number of bytes reserved for packet files being saved to
    disk files. If this value is exceeded, the old file(s) will be
    deleted.
    """

    data_start_time = None
    """The time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    when Capture to Disk data started being saved.
    """

    data_stop_time = None
    """The time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    when Capture to Disk data stopped being saved.
    """

    duplicate_packets_discarded = 0
    """The number of discarded packets because they are duplicates."""

    duration = 0
    """The length of time the capture has been capturing in
    nanoseconds.
    """

    error_code = 0
    """The code, as Integer, of the last error."""

    error_code_text = ''
    """The description, as text, of the last error."""

    file_size = 0
    """The number of bytes in a Capture to Disk file before starting
    a new file.
    """

    filter_list = []
    """The list of enabled Filters."""

    filter_mode = 0
    """The filter mode."""

    first_packet = 0
    """The packet number of the first packet in the capture's packet
    buffer.
    """

    flows_dropped = 0
    """The number of flows dropped."""

    graphs_count = 0
    """The number of graphs being used by the capture."""

    group_id = 0
    """The index, as an integer, of the capture group."""

    hardware_profile = ''
    """The name of the Hardware Profile."""

    hardware_profile_id = None
    """The Hardware Profile Id as
    :class:`OmniId <omniscript.omniid.OmniId>`
    """

    id = None
    """The Identifier, as
    :class:`OmniId <omniscript.omniid.OmniId>`,
    of the Capture.
    """

    link_speed = 0
    """The link speed, in bits per second, of the capture's adapter."""

    logged_on_user_sid = ''
    """The currenlty logged on user."""

    media_information = None
    """The :class:`MediaInformation <omniscript.mediainformation.MediaInformation>` object
    of the capture.
    """

    media_sub_type = 0
    """The media sub-type of the capture's adapter."""

    media_type = 0
    """The media type of the capture's adapter."""

    modification_time = None
    """The time of the last modification made to the capture as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    modification_type = ''
    """The type of the last modification made to the capture."""

    modified_by = ''
    """The name of the user that last modified the capture."""

    name = ''
    """The name of the capture."""

    packet_count = 0
    """The current number of packets in the capture's packet buffer."""

    packets_analyzed = 0
    """The number of packets analyzed."""

    packets_dropped = 0
    """The number of packets dropped."""

    packets_filtered = 0
    """The number of packets that have been accepted by the capture's
    filters.
    """

    packets_received = 0
    """The number of packets the capture has received."""

    plugin_list = []
    """The Analysis Modules (plugins) being used by the capture."""

    reset_count = 0
    """The number of times the capture has been reset."""

    session_id = None
    """The session id of this capture."""

    start_time = None
    """The Start Time of the capture as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    status = 0
    """The status of the capture: idle, capturing... """

    stop_time = None
    """The Stop Time of the capture as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    trigger_count = 0
    """The number of Triggers that have been triggered."""

    trigger_duration = 0
    """The duration of the trigger events."""

    option_alarms = False
    """Are alarms enabled?"""

    option_ctd = False
    """Is Capture to Disk enabled?"""

    option_ctd_intelligent = False
    """Is Intelligent Capture to Disk enabled?"""

    option_distributed = False
    """Is the capture distributed?"""

    option_elk = False
    """Is Elk enabled?"""

    option_expert = False
    """Is Expert Processing enabled?"""

    option_filters = False
    """Are Filters enabled."""

    option_graphs = False
    """Are graphs enabled?"""

    option_hardware_deduplication = False
    """Is Hardware Deduplication enabled?"""

    option_hardware_filtering = False
    """Is Hardware Filtering enabled?"""

    option_hidden = False
    """Is the capture hidden?"""

    option_indexing = False
    """Is Indexing enabled?
    Indexing is enabled only if CTD and at least one Indexing option
    is enabled.
    """

    option_packet_buffer = True
    """Does the capture have a capture buffer."""

    option_spotlight = False
    """Is this the Spotlight Capture?"""

    option_threateye = False
    """Is this a ThreatEye NV Capture?"""

    option_timeline_stats = False
    """Are Timeline Statistics enabled?"""

    option_voice = False
    """Are Voice Statistics enabled?"""

    option_web = False
    """Are Web Statistics enabled?"""

    find_attributes = ('name', 'id')

    def __init__(self, engine, props=None):
        self._engine = engine
        self.logger = engine.logger
        self._context = None

        self.adapter = Capture.adapter
        self.adapter_id = Capture.adapter_id
        self.adapter_name = Capture.adapter_name
        self.adapter_type = Capture.adapter_type
        self.alarms_info = Capture.alarms_info
        self.alarms_major = Capture.alarms_major
        self.alarms_minor = Capture.alarms_minor
        self.alarms_severe = Capture.alarms_severe
        self.analysis_dropped_packets = Capture.analysis_dropped_packets
        self.buffer_available = Capture.buffer_available
        self.buffer_size = Capture.buffer_size
        self.buffer_used = Capture.buffer_used
        self.comment = Capture.comment
        self.creation_time = Capture.creation_time
        self.creator = Capture.creator
        self.creator_sid = Capture.creator_sid
        self.ctd_start_time = Capture.ctd_start_time
        self.ctd_stop_time = Capture.ctd_stop_time
        self.data_start_time = Capture.data_start_time
        self.data_stop_time = Capture.data_stop_time
        self.duplicate_packets_discarded = Capture.duplicate_packets_discarded
        self.duration = Capture.duration
        self.error_code = Capture.error_code
        self.error_code_text = Capture.error_code_text
        self.file_size = Capture.file_size
        self.filter_list = Capture.filter_list
        self.filter_mode = Capture.filter_mode
        self.first_packet = Capture.first_packet
        self.flows_dropped = Capture.flows_dropped
        self.graphs_count = Capture.graphs_count
        self.group_id = Capture.group_id
        self.hardware_profile = Capture.hardware_profile
        self.hardware_profile_id = Capture.hardware_profile_id
        self.id = Capture.id
        self.link_speed = Capture.link_speed
        self.logged_on_user_sid = Capture.logged_on_user_sid
        self.media_information = Capture.media_information
        self.media_sub_type = Capture.media_sub_type
        self.media_type = Capture.media_type
        self.modification_time = Capture.modification_time
        self.modification_type = Capture.modification_type
        self.modified_by = Capture.modified_by
        self.name = Capture.name
        self.packet_count = Capture.packet_count
        self.packets_analyzed = Capture.packets_analyzed
        self.packets_dropped = Capture.packets_dropped
        self.packets_filtered = Capture.packets_filtered
        self.packets_received = Capture.packets_received
        self.plugin_list = Capture.plugin_list
        self.reset_count = Capture.reset_count
        self.session_id = Capture.session_id
        self.start_time = Capture.start_time
        self.status = Capture.status
        self.stop_time = Capture.stop_time
        self.trigger_count = Capture.trigger_count
        self.trigger_duration = Capture.trigger_duration
        self.option_alarms = Capture.option_alarms
        self.option_ctd = Capture.option_ctd
        self.option_ctd_intelligent = Capture.option_ctd_intelligent
        self.option_distributed = Capture.option_distributed
        self.option_elk = Capture.option_elk
        self.option_expert = Capture.option_expert
        self.option_filters = Capture.option_filters
        self.option_graphs = Capture.option_graphs
        self.option_hardware_deduplication = Capture.option_hardware_deduplication
        self.option_hardware_filtering = Capture.option_hardware_filtering
        self.option_hidden = Capture.option_hidden
        self.option_indexing = Capture.option_indexing
        self.option_packet_buffer = Capture.option_packet_buffer
        self.option_spotlight = Capture.option_spotlight
        self.option_threateye = Capture.option_threateye
        self.option_timeline_stats = Capture.option_timeline_stats
        self.option_voice = Capture.option_voice
        self.option_web = Capture.option_web
        self._load(props)

    def __repr__(self) -> str:
        return f'Capture: {self.name}'

    def __str__(self) -> str:
        return f'Capture: {self.name}'

    # def _get_properties(self):
    #     request = '<request><prop name=\"id\" type=\"8\">' + str(self.id) + '</prop></request>'
    #     response = self._engine._issue_xml_command(invariant.OMNI_GET_CAPTURE_PROPS, request)
    #     return omniscript._parse_command_response(response, 'captureproperties')

    # def _get_statistics(self):
    #     """Get the Statistics, a binary blob of data, and cache them."""
    #     if self.id is None:
    #         self.logger.error("Failed to get the id for Capture: %s",
    #                           self.name)
    #         return None
    #     # DEBUG self._context = self._engine._api_issue_command(
    #     # DEBUG                   invariant.OMNI_GET_STATS_CONTEXT, str(self.id), 0)
    #     request = struct.pack('16sQ', self.id.bytes_le(), 0)
    #     data = self._engine._issue_command(invariant.OMNI_GET_STATS,
    #                                        request, 24)
    #     # DEBUG with open(r"c:\temp\stat_data.bin", 'wb') as fle:
    #     # DEBUG    fle.write(data)
    #     # self._context = StatsContext(data.raw)

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = _capture_prop_dict.get(k)
                if a is None or not hasattr(self, a):
                    continue
                if isinstance(getattr(self, a), six.string_types):
                    setattr(self, a, v if v else '')
                elif isinstance(getattr(self, a), bool):
                    setattr(self, a, (v != 'true') if v else False)
                elif isinstance(getattr(self, a), int):
                    setattr(self, a, int(v) if v else 0)
                elif isinstance(getattr(self, a), list):
                    if (a == 'filter_list') or (a == 'plugin_list'):
                        setattr(self, a, [OmniId(id) for id in v])
                elif getattr(self, a) is None:
                    if a == 'adapter':
                        setattr(self, a, Adapter(self.engine, v))
                    elif a in ('group_id', 'id', 'session_id'):
                        setattr(self, a, OmniId(v))
                    elif a in ('creation_time', 'data_start_time', 'data_stop_time',
                               'modification_time', 'start_time', 'stop_time'):
                        setattr(self, a, PeekTime(v))
                    elif a == 'media_information':
                        setattr(self, a, MediaInformation(v))
        # first_packet is a packet index (index into the capture buffer),
        #   convert it into a packet number(?).
        if self.first_packet > 0:
            self.first_packet += 1

    @property
    def engine(self):
        """The engine that this capture belongs to."""
        return self._engine

    def format_status(self):
        """Convert capture status from integer to descriptive string."""
        status = status_map[self.status]
        if status is None:
            return 'Unknown'
        return status

    # def get_application_stats(self, refresh=False):
    #     """Returns a list of
    #     :class:`ApplicationStatistic <omniscript.applicationstatistic.ApplicationStatistic>`
    #     objects.

    #     Args:
    #         refresh (boolean): refresh the statistics cache. Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context "
    #                            "for capture: %s.", self.name))
    #         return None
    #     return self._context.get_application_statistics()

    # def get_call_stats(self, refresh=False):
    #     """Returns a
    #     :class:`CallStatistic <omniscript.callstatistic.CallStatistic>`
    #     object.
    #     Note that only one CallStatistic object is returned.

    #     Args:
    #         refresh (boolean): refresh the statistics cache. Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context "
    #                            "for capture: %s.", self.name))
    #         return None
    #     return self._context.get_call_statistics()

    # def get_capture_template(self):
    #     """Get the
    #     :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    #     of this capture.

    #     Returns:
    #         A :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    #         object.
    #     """
    #     return self._engine.get_capture_template(self)

    # def get_country_stats(self, refresh=False):
    #     """Returns a list of
    #     :class:`CountryStatistic <omniscript.countrystatistic.CountryStatistic>`
    #     objects.

    #     Args:
    #         refresh (boolean): refresh the statistics cache.
    #                            Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context "
    #                            "for capture: %s.", self.name))
    #         return None
    #     return self._context.get_country_statistics()

    # def get_node_stats(self, refresh=False):
    #     """Returns a list of
    #     :class:`NodeStatistic <omniscript.nodestatistic.NodeStatistic>`
    #     objects.

    #     Args:
    #         refresh (boolean): refresh the statistics cache.
    #                            Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context "
    #                            "for capture: %s.", self.name))
    #         return None
    #     return self._context.get_node_statistics()

    def get_options(self):
        """Returns the Capture's Options in a Capture Template object."""
        pr = self.perf('get_options')
        cmd = f'captures/{self.id.format()}/options/'
        props = self._engine._issue_command(cmd, pr)
        return CaptureTemplate(props=props, engine=self._engine) if props else None

    def get_packet_data(self, number):
        """Returns a bytearry of the packet data.

        Notes:
            The first packet number is 1.

        Example:
            get_packet_data(1) gets the data of the first captured packet.
        """
        self.refresh()
        if number < self.first_packet:
            return None
        pr = self.perf('get_packet_data')
        cmd = f'captures/{self.id.format()}/packets/{number}/'
        resp = self._engine._issue_command(cmd, pr)
        data = bytearray(resp['data'])
        return data

    def get_packet_decode(self, number, format=DECODE_PLAIN_TEXT):
        """Returns a string or array of bytes of the packet decode.

        Notes:
            The first packet number is 1.

        Example:
            get_packet_decode(1) gets the decode of the first captured packet.
        """
        self.refresh()
        if number < self.first_packet:
            return None
        if format == DECODE_PLAIN_TEXT:
            decode = DF.PLAIN
        elif format == DECODE_HTML:
            decode = DF.HTML
        elif format == DECODE_TAG_STREAM:
            decode = DF.TAG_STREAM
        else:
            raise OmniError('Unrecognized format parameter.')

        pr = self.perf('get_packet_decode')
        command = f'captures/{self.id.format()}/packets/{number}/'
        resp = self._engine._issue_command(command, pr, format=decode)
        return resp

    def get_packets(self, first, count=1):
        """Returns a list of :class:`Packet <omniscript.packet.Packet>`
        objects.

        Notes:
            The first packet number is 1.

        Example:
            get_packets(1) gets the first captured packet.
        """
        self.refresh()
        if first < self.first_packet:
            return []
        req_props = [
            ('firstPacketNumber', first),
            ('packetCount', count),
            ('showLogical', jtrue),
            ('showAddressNames', jfalse),
            ('showPortNames', jfalse)
        ]
        column_dict = Packet.get_prop_dict()
        for k in column_dict.keys():
            req_props.append(('columns', k))
        pr = self.perf('get_packets')
        command = f'captures/{self.id.format()}/packet-list/'
        props = self._engine._issue_command(command, pr, params=req_props)
        return _create_packet_list(props)

    # def get_packets_old(self, indices):
    # #     """Returns a list of
    # #     :class:`Packet <omniscript.packet.Packet>`
    # #     objects.

    # #     Notes:
    # #         The first packet number is 1.

    # #     Args:
    # #         numbers (list): a list of integers or tuples.
    # #         numbers (integer): the number of the to retrieve.
    # #         numbers (tupel): the number of the first packet and the
    # #         number of the last packet to retrieve.

    # #     Example:
    # #         get_packets([(1,3),(10,11),20]) gets packets: 1,2,3,10,11,20.
    # #         get_packets(1) gets the first captured packet.
    # #         get_packets((1,3) gets packets: 1,2,3
    # #     """
    #     pairs = []
    #     if isinstance(indices, list):
    #         for i in indices:
    #             if isinstance(i, int):
    #                 pairs.append((i,(i + 1)))
    #             elif isinstance(i, tuple):
    #                 pairs.append((i[0], (i[1] + 1)))
    #     elif isinstance(indices, int):
    #         pairs.append((indices,indices))
    #     elif isinstance(indices, tuple):
    #         pairs.append((indices[0], (indices[1] + 1)))
    #     count = len(pairs) * 2
    #     if count == 0:
    #         return None
    #     self.refresh()
    #     pl = []
    #     for p in pairs:
    #         if isinstance(p, tuple) and (len(p) == 2):
    #             for x in range(p[0], p[1]):
    #                 pl.append(self.get_packet(x))

    #     # indexes = (item for sublist in pairs for item in sublist)
    #     # for i in indexes:
    #     #     if isinstance(i, int):
    #     #         pl.append(self.get_packet(i))
    #     return pl

    # def get_protocol_stats(self, refresh=False):
    #     """Returns a list of
    #     :class:`ProtocolStatistic
    #     <omniscript.protocolstatistic.ProtocolStatistic>`
    #     objects.

    #     Args:
    #         refresh (boolean): refresh the statistics cache. Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context for "
    #                            "capture: %s.", self.name))
    #         return None
    #     return self._context.get_protocol_statistics()

    # def get_stats_context(self, refresh=False):
    #     """Returns a
    #     :class:`StatsContext
    #     <omniscript.statscontext.StatsContext>`
    #     object.

    #     Args:
    #         refresh (boolean): refresh the statistics context. Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context for "
    #                            "capture: %s.", self.name))
    #         return None
    #     return self._context

    # def get_summary_stats(self, refresh=False):
    #     """Returns a list of
    #     :class:`SummaryStatistic
    #     <omniscript.summarystatistic.SummaryStatistic>`
    #     objects.

    #     Args:
    #         refresh (boolean): refresh the statistics cache. Default is False.
    #     """
    #     if self._context is None or refresh:
    #         self._get_statistics()
    #     if self._context is None:
    #         self.logger.error(("Failed to get statistics context for "
    #                            "capture: %s.", self.name))
    #         return None
    #     return self._context.get_summary_statistics()

    def is_capturing(self, refresh=True):
        """Returns True if the capture is capturing.

        Args:
            refresh (boolean): refresh the capture's status. Default is True.
        """
        if refresh:
            self.refresh()
        return ((self.status & CAPTURE_STATUS_CAPTURING) != 0)

    def is_idle(self, refresh=True):
        """Returns True if the capture is not capturing.

        Args:
            refresh (boolean): refresh the capture's status. Default is True.
        """
        return not self.is_capturing(refresh)

    def is_spotlight_capture(self):
        """Returns True if the capture is the Spotlight Capture."""
        return self.option_spotlight

    # def is_start_trigger_active(self, refresh=True):
    #     """Returns True if the capture has an active Start Trigger.

    #     Args:
    #         refresh (boolean): refresh the capture's status. Default is True.
    #     """
    #     if refresh:
    #         self.refresh()
    #     return ((self.status & invariant.CAPTURE_STATUS_START_ACTIVE) != 0)

    # def is_stop_trigger_active(self, refresh=True):
    #     """Returns True if the capture has an active Stop Trigger.

    #     Args:
    #         refresh (boolean): refresh the capture's status. Default is True.
    #     """
    #     if refresh:
    #         self.refresh()
    #     return ((self.status & invariant.CAPTURE_STATUS_STOP_ACTIVE) != 0)

    # def modify(self, template):
    #     """Modify the settings with those in the template.
    #     """
    #     return self._engine.modify_capture(template, self)

    def perf(self, message):
        if self._engine:
            return self._engine.perf(message)
        return None

    # def query_expert(self, query_list):
    #     """Query the Expert with one or more
    #     :class:`ExpertQuery <omniscript.expertquery.ExpertQuery>` objects.
    #     Submit more than one query to get a snapshot at the same point in time.
    #     See the :ref:`expert-tables-section` section for the list of tables and columns.

    #     Returns a list of
    #     :class:`ExpertResult <omniscript.expertresult.ExpertResult>` objects.
    #     Match the result to the query by the table name.
    #     """
    #     querys = query_list if isinstance(query_list, list) else [query_list]
    #     request = ET.Element('request')
    #     msg = ET.SubElement(request, 'msg', {'capture-id':str(self.id)})
    #     for q in querys:
    #         q._store(msg)
    #     xml = ET.tostring(msg).replace('\n', '')
    #     response = self._engine._issue_xml_command(invariant.OMNI_EXPERT_EXECUTE_QUERY, xml)
    #     querys = omniscript._parse_command_response(response, 'msg')
    #     return _create_expert_result_list(querys)

    def refresh(self):
        """Refresh the properties of this object.
        The statitics cache is cleared.
        """
        pr = self.perf('capture refresh')
        props = self._engine._issue_command(f'captures/{self.id.format()}/', pr)
        if props is not None:
            self.__init__(self._engine, props)
            return True
        return False

    # def refresh_stats(self):
    #     """Refresh the statistics cache."""
    #     self._get_statistics()

    # def reset(self):
    #     """Reset the capture's statistics and delete all its packets.
    #     This capture object will be refreshed.
    #     """
    #     if self.id is None:
    #         self.logger.error("Failed to get the id for Capture: %s", self.name)
    #         return False
    #     # <captures>
    #     #   <capture id="{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}" />
    #     # </captures>
    #     request = (r'<request><captures><capture id="' + str(self.id) +
    #                r'"/></captures></request>')
    #     response = self._engine._issue_xml_string_result(
    #                 invariant.OMNI_CLEAR_CAPTURES, request)
    #     omniscript._parse_command_response(response)
    #     self.refresh()

    # def save_all_packets(self, filename):
    #     """Save the packets of the capture to a file."""
    #     return self._engine.save_all_packets(self, filename)

    # def select_related(self, packets, criteria=omniscript.SELECT_BY_SOURCE_DESTINATION,
    #                    unique=True):
    #     """Returns a list of packet numbers for the packets and criteria specified.
    #     If unique is True then only unique packet numbers are returned. Otherwise the
    #     list may contain duplicates.
    #     Example: packet 1 matches packets 1,2,5 and packet 3 matches packets 2,3,4,6.
    #     Unique returns [1,2,3,4,5,6], non-unique returns [1,2,5,2,3,4,6].
    #     """
    #     _packets = packets if isinstance(packets, list) else [packets]
    #     magic = 0x4E8B3899
    #     version = 1
    #     logical_addr = 1
    #     packet_count = len(packets)
    #     buf = struct.pack('=II16sIII%dQ' % packet_count, magic, version,
    #                       self.id.bytes_le(), criteria, logical_addr,
    #                       packet_count, *packets)
    #     response = self._engine._issue_command(invariant.OMNI_SELECT_RELATED,
    #                                            buf, len(buf))
    #     try:
    #         omniscript._parse_command_response(response)
    #     except omniscript.OmniError as oe:
    #         raise oe
    #     except Exception:
    #         # Only errors are parseable.
    #         # But ET.parse(data) will throw an exception
    #         #   catch the exception and process the success.
    #         pass
    #     stream = ReadStream(response)
    #     pkt_count = stream.read_uint()
    #     if unique:
    #         return list(set(stream.read_ulong() for i in range(pkt_count)))
    #     else:
    #         return [stream.read_ulong() for i in range(pkt_count)]

    def start(self):
        """Start the capturing packets. Returns True if the capture is
        capturing packets.
        """
        if self.id is None:
            self.logger.error(f'Failed to get the id for Capture: {self.name}')
            return False
        pr = self.perf('capture start')
        command = f'running-captures/{self.id.format()}/'
        props = self._engine._issue_command(command, pr, EO.POST)
        return (props is not None)

    def stop(self):
        """Stop the capturing packets. Returns True if the capture is
        stopped.
        """
        if self.id is None:
            self.logger.error(f'Failed to get the id for Capture: {self.name}')
            return False
        pr = self.perf('capture stop')
        command = f'running-captures/{self.id.format()}/'
        props = self._engine._issue_command(command, pr, EO.DELETE)
        return (props is not None)


def _create_capture_list(engine, resp):
    lst = []
    captures = resp['captures']
    if captures is not None:
        for props in captures:
            lst.append(Capture(engine, props))
    lst.sort(key=lambda x: x.name)
    return lst


def find_all_captures(captures, value, attrib=Capture.find_attributes[0]):
    """Finds all captures that match the value in the capture list."""
    if (not captures) or (attrib not in Capture.find_attributes):
        return None

    if isinstance(captures, list):
        return [i for i in captures if isinstance(i, Capture) and getattr(i, attrib) == value]


def find_capture(captures, value, attrib=Capture.find_attributes[0]):
    """Finds a capture in the list"""
    if not captures or attrib not in Capture.find_attributes:
        return None

    if len(captures) == 0:
        return None

    if isinstance(value, Capture):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    c = next((i for i in captures if getattr(i, attrib) == _value), None)
    return c

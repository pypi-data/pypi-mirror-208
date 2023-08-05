"""ForensicSearch class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import xml.etree.ElementTree as ET

import omniscript

from .invariant import (
    DECODE_PLAIN_TEXT, DECODE_HTML, DECODE_TAG_STREAM, MEDIA_TYPE_802_3, MEDIA_SUB_TYPE_NATIVE,
    OMNI_EXPERT_EXECUTE_QUERY)

# from expertresult import _create_expert_result_list
from .invariant import EngineDataFormat as DF
from .mediainformation import MediaInformation
# from nodestatistic import NodeStatistic
from .omnierror import OmniError
from .omniid import OmniId
from .peektime import PeekTime
# from protocolstatistic import ProtocolStatistic
# from statscontext import StatsContext
# from summarystatistic import SummaryStatistic


_forensic_prop_dict = {
    'id': 'id',
    'name': 'name',
    'adapter': 'adapter',
    'pluginsEnabled': 'analysis_modules',
    'captureName': 'capture_name',
    'captureSessionId': 'session_id',
    'creationTime': 'creation_time',
    'creator': 'creator',
    'creatorSID': 'creator_sid',
    'duration': 'duration',
    'firstPacket': 'first_packet',
    'linkSpeed': 'link_speed',
    'loadPercentProgress': 'load_progress',
    'loadProgress': 'load_percent',
    'mediaInfo': 'media_information',
    'mediaType': 'media_type',
    'mediaSubtype': 'media_sub_type',
    'modificationBy': 'modified_by',
    'modificationTime': 'modification_time',
    'modificationType': 'modification_type',
    'openResult': 'open_result',
    'packetCount': 'packet_count',
    'percentProgress': 'percent_progress',
    'processPercentProgress': 'process_percent_progress',
    'processProgress': 'process_progress',
    'progress': 'progress',
    'startTime': 'start_time',
    'status': 'status',
    'stopTime': 'stop_time',
    'loggedOnUserSid': 'user',
    'expertEnabled': 'option_expert',
    'graphsEnabled': 'option_graphs',
    'indexingEnabled': 'option_indexing',
    'logEnabled': 'option_log',
    'packetBufferEnabled': 'option_packet_buffer',
    'reconstructionEnabled': 'option_reconstruction',
    'statsEnabled': 'option_statistics',
    'voiceEnabled': 'option_voice',
    'webEnabled': 'option_web'
}


class ForensicSearch(object):
    """Forensic Search class.
    """

    id = None
    """The identifier of the search as an OmniId."""

    name = ''
    """The name of the search."""

    adapter = ''
    """The search's adapter's name."""

    analysis_modules = []
    """The ids of the Analysis Modules used the Forensic Search."""

    capture_name = ''
    """The optional name of the source Capture."""

    session_id = ''
    """The session id."""

    creation_time = None
    """The time the Forensic Search was created."""

    creator = ''
    """The user account that created the search."""

    creator_sid = ''
    """The security identifier of the account the created the search."""

    duration = 0
    """The difference between the timestamp of the first packet and the last
    packet in nanoseconds.
    """

    first_packet = 0
    """The index of the first packet."""

    link_speed = 0
    """The link speed of the search's adapter in bits per second."""

    load_progress = 'unknown'
    """The status of the loading process: idle, loading, complete..."""

    load_percent = '0'
    """The percentage of the loading process that has been completed.
    An interger value where 50 indicates 50% complete.
    Or 'Load Completed' when completed.
    """

    media_information = MediaInformation()
    """The :class:`MediaInformation <omniscript.forensicsearch.MediaInformation>` about the
    search.
    """

    media_type = MEDIA_TYPE_802_3
    """The media type of the search."""

    media_sub_type = MEDIA_SUB_TYPE_NATIVE
    """The media sub type of the search."""

    modified_by = ''
    """The name of the user account that last modified the search."""

    modification_time = None
    """The last time a modification was made to the search."""

    modification_type = ''
    """The last type of modification made to the search."""

    open_result = 0
    """The result of opening the search."""

    packet_count = 0
    """The number of packets in the search."""

    percent_progress = 0
    """The percentage of the progress made on the search.
    An integer value where 50 indicates 50%.
    """

    process_percent_progress = 0
    """The percentage of the progress made on the search.
    An integer value where 50 indicates 50%.
    """

    process_progress = 'unknown'
    """The progress status of the process."""

    progress = 'unknown'
    """The amount of progress made."""

    start_time = None
    """The begining of the time range, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    of packets to search.
    """

    status = 0
    """The status of the search: loading = 0, processing = 1, complete = 2."""

    statistics = []
    """The ids of the Statistics used by the Forensic Search."""

    stop_time = None
    """The ending of the time range, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    of packets to search."""

    user = ''
    """The currently logged on User Account."""

    option_expert = False
    """Is the Expert option enabled."""

    option_graphs = False
    """Is the Graphs option enabled."""

    option_indexing = False
    """Is the Indexing option enabled."""

    option_log = False
    """Is the Log option enabled."""

    option_packet_buffer = False
    """Is the Packet Buffer option enabled."""

    option_voice = False
    """Is the Voice and Video Statistics option enabled."""

    option_web = False
    """Is the Web Statistics option enabled."""

    find_attributes = ('name', 'id')

    def __init__(self, props, engine):
        self._engine = engine

        self.id = ForensicSearch.id
        self.name = ForensicSearch.name
        self.adapter = ForensicSearch.adapter
        self.analysis_modules = ForensicSearch.analysis_modules
        self.capture_name = ForensicSearch.capture_name
        self.creation_time = ForensicSearch.creation_time
        self.creator = ForensicSearch.creator
        self.creator_sid = ForensicSearch.creator_sid
        self.duration = ForensicSearch.duration
        self.first_packet = ForensicSearch.first_packet
        self.link_speed = ForensicSearch.link_speed
        self.load_progress = ForensicSearch.load_progress
        self.load_percent = ForensicSearch.load_percent
        self.media_information = MediaInformation()
        self.media_type = ForensicSearch.media_type
        self.media_sub_type = ForensicSearch.media_sub_type
        self.modified_by = ForensicSearch.modified_by
        self.modification_time = ForensicSearch.modification_time
        self.modification_type = ForensicSearch.modification_type
        self.open_result = ForensicSearch.open_result
        self.packet_count = ForensicSearch.packet_count
        self.percent_progress = ForensicSearch.percent_progress
        self.process_percent_progress = ForensicSearch.process_percent_progress
        self.process_progress = ForensicSearch.process_progress
        self.progress = ForensicSearch.progress
        self.start_time = ForensicSearch.start_time
        self.status = ForensicSearch.status
        self.stop_time = ForensicSearch.stop_time
        self.user = ForensicSearch.user
        self.option_expert = ForensicSearch.option_expert
        self.option_graphs = ForensicSearch.option_graphs
        self.option_indexing = ForensicSearch.option_indexing
        self.option_log = ForensicSearch.option_log
        self.option_packet_buffer = ForensicSearch.option_packet_buffer
        self.option_voice = ForensicSearch.option_voice
        self.option_web = ForensicSearch.option_web
        self.load(props)

    def __str__(self):
        return f'ForensicSearch: {self.name} {self.id}'

    # def _get_statistics(self):
    #     """Get the Statistics, a binary blob of data."""
    #     if self.id is None:
    #         self.logger.error("Failed to get the id for Capture: %s",
    #                           self.name)
    #         return None
    #     # self._context = self._engine._api_issue_command(
    #     #                   OMNI_GET_STATS_CONTEXT, str(self.id), 0)
    #     request = struct.pack('16sQ', self.id.bytes_le(), 0)
    #     data = self._engine._issue_command(OMNI_GET_STATS, request, 24)
    #     # with open(r"c:\temp\stat_data.bin", 'wb') as fle:
    #     #    fle.write(data)
    #     self._context = StatsContext(data.raw)

    def get_application_stats(self, refresh=False):
        """Returns a list of
        :class:`ApplicationStatistic <omniscript.applicationstatistic.ApplicationStatistic>`
        objects.

        Args:
            refresh (boolean): refresh the statistics cache. Default is False.
        """
        if self._context is None or refresh:
            self._get_statistics()
        if self._context is None:
            self.logger.error(
                f'Failed to get statistics context for forensic search: {self.name}.')
            return None
        return self._context.get_application_statistics()

    def get_call_stats(self, refresh=False):
        """Returns a
        :class:`CallStatistic <omniscript.callstatistic.CallStatistic>`
        object.
        Note that only one CallStatistic object is returned.

        Args:
            refresh (boolean): refresh the statistics cache. Default is False.
        """
        if self._context is None or refresh:
            self._get_statistics()
        if self._context is None:
            self.logger.error(
                f'Failed to get statistics context for forensic search: {self.name}.')
            return None
        return self._context.get_call_statistics()

    def get_country_stats(self, refresh=False):
        """Returns a list of
        :class:`CountryStatistic <omniscript.countrystatistic.CountryStatistic>`
        objects.

        Args:
            refresh (boolean): refresh the statistics cache. Default is False.
        """
        if self._context is None or refresh:
            self._get_statistics()
        if self._context is None:
            self.logger.error(
                f'Failed to get statistics context for forensic search: {self.name}.')
            return None
        return self._context.get_country_statistics()

    def get_node_stats(self):
        """Returns a list of
        :class:`NodeStatistic <omniscript.nodestatistic.NodeStatistic>`
        objects.
        """
        if self._context is None:
            self._get_statistics()
        if self._context is None:
            self.logger.error(f'Failed to get statistics context for capture: {self.name}.')
            return None
        # node_stats = self._engine._get_stats(self._context, STATS_NODE)
        # lst = []
        # for ns in node_stats:
        #    lst.append(NodeStatistic(ns))
        # return lst
        return self._context.get_node_statistics()

    def get_packet_data(self, number):
        """Returns a bytearry of the packet data.

        Notes:
            The first packet number is 1.

        Example:
            get_packet_data(1) gets the data of the first packet.
        """
        self.refresh()
        if number < self.first_packet:
            return None
        command = f'forensic-searches/{self.id.format()}/packets/{number}/'
        resp = self._engine._issue_command(command)
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

        command = f'forensic-searches/{self.id.format()}/packets/{number}/'
        resp = self._engine._issue_command(command, format=decode)
        return resp

    def get_protocol_stats(self):
        """Returns a list of
        :class:`ProtocolStatistic
        <omniscript.protocolstatistic.ProtocolStatistic>`
        objects.
        """
        if self._context is None:
            self._get_statistics()
        if self._context is None:
            self.logger.error(f'Failed to get statistics context for capture: {self.name}.')
            return None
        # protocol_stats = self._engine._get_stats(self._context, STATS_PROTOCOL)
        # lst = []
        # for ps in protocol_stats:
        #    lst.append(ProtocolStatistic(ps))
        # return lst
        return self._context.get_protocol_statistics()

    def get_stats_context(self, refresh=False):
        """Returns a
        :class:`StatsContext
        <omniscript.statscontext.StatsContext>`
        object.

        Args:
            refresh (boolean): refresh the statistics context. Default is False.
        """
        if self._context is None or refresh:
            self._get_statistics()
        if self._context is None:
            self.logger.error(
                f'Failed to get statistics context for forensic search: {self.name}.')
            return None
        return self._context

    def get_summary_stats(self):
        """Returns a list of
        :class:`SummaryStatistic
        <omniscript.summarystatistic.SummaryStatistic>`
        objects.
        """
        if self._context is None:
            self._get_statistics()
        if self._context is None:
            self.logger.error(f'Failed to get statistics context for capture: {self.name}.')
            return None
        # summary_stats = self._engine._get_stats(self._context, STATS_SUMMARY)
        # return _summary_xml_to_stats_list(summary_xml)
        return self._context.get_summary_statistics()

    def load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = _forensic_prop_dict.get(k)
            if a is None or not hasattr(self, a):
                continue
            if isinstance(getattr(self, a), six.string_types):
                setattr(self, a, v)
            elif isinstance(getattr(self, a), bool):
                setattr(self, a, int(v) != 0)
            elif isinstance(getattr(self, a), int):
                setattr(self, a, int(v))
            elif isinstance(getattr(self, a), MediaInformation):
                self.media_information.load(v)
            elif isinstance(getattr(self, a), list):
                if a == 'analysis_modules':
                    self.analysis_modules.append(OmniId(v))
                elif a == 'statistics':
                    self.statistics.append(OmniId(v))
            elif getattr(self, a) is None:
                if a == 'id':
                    setattr(self, a, OmniId(v))
                elif a in ('creation_time', 'modification_time', 'start_time', 'stop_time'):
                    setattr(self, a, PeekTime(v))

    def query_expert(self, query_list):
        """Query the Expert with one or more
        :class:`ExpertQuery <omniscript.expertquery.ExpertQuery>` objects.
        Submit more than one query to get a snapshot at the same point in time.
        See the :ref:`expert-tables-section` section for the list of tables and columns.

        Returns a list of
        :class:`ExpertResult <omniscript.expertresult.ExpertResult>` objects.
        Match the result to the query by the table name.
        """
        querys = query_list if isinstance(query_list, list) else [query_list]
        request = ET.Element('request')
        msg = ET.SubElement(request, 'msg', {'capture-id': str(self.id)})
        for q in querys:
            q._store(msg)
        xml = ET.tostring(msg).replace('\n', '')
        response = self._engine._issue_xml_command(OMNI_EXPERT_EXECUTE_QUERY, xml)
        querys = omniscript._parse_command_response(response, 'msg')
        # return _create_expert_result_list(querys)
        return []

    def refresh(self):
        """Refresh the properties of this object."""
        search = self._engine.find_forensic_search(str(self.id), 'id')
        if (search is not None) and (search.id == self.id):
            self.name = search.name
            self.adapter = search.adapter
            self.capture_name = search.capture_name
            self.session_id = search.session_id
            self.creator = search.creator
            self.creator_sid = search.creator_sid
            self.duration = search.duration
            self.status = search.status
            self.first_packet = search.first_packet
            self.link_speed = search.link_speed
            self.load_progress = search.load_progress
            self.load_percent = search.load_percent
            self.media_type = search.media_type
            self.media_sub_type = search.media_sub_type
            self.modified_by = search.modified_by
            self.modification_type = search.modification_type
            self.open_result = search.open_result
            self.packet_count = search.packet_count
            self.percent_progress = search.percent_progress
            self.process_percent_progress = search.process_percent_progress
            self.process_progress = search.process_progress
            self.progress = search.progress
            self.start_time = search.start_time
            self.stop_time = search.stop_time
            self.media_information = search.media_information
            self.option_expert = search.option_expert
            self.option_graphs = search.option_graphs
            self.option_indexing = search.option_indexing
            self.option_log = search.option_log
            self.option_packet_buffer = search.option_packet_buffer
            self.option_voice = search.option_voice
            self.option_web = search.option_web

    def save_packets(self, filename):
        """Save all the packets to a file."""
        return self._engine.save_all_packets(self, filename)


def _create_forensic_search_list(engine, resp):
    lst = []
    searches = resp['forensicSearches']
    if searches is not None:
        for props in searches:
            lst.append(ForensicSearch(props, engine))
    lst.sort(key=lambda x: x.name)
    return lst


def find_forensic_search(searches, value, attrib=ForensicSearch.find_attributes[0]):
    """Finds a forensic search in the list"""
    if (not searches) or (attrib not in ForensicSearch.find_attributes):
        return []

    if len(searches) == 0:
        return []

    if isinstance(value, ForensicSearch):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in searches if getattr(i, attrib) == _value), [])

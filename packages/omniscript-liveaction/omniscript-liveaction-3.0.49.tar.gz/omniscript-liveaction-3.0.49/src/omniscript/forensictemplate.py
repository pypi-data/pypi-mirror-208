"""ForensicTemplate class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import json
import six

import xml.etree.ElementTree as ET

import omniscript
from omniscript.adapter import Adapter

from .invariant import (
    LIMIT_TYPE_NONE, LIMIT_TYPE_PACKETS, LIMIT_TYPE_BYTES, LIMIT_TYPE_BUFFER, MEDIA_TYPE_802_3,
    MEDIA_SUB_TYPE_NATIVE, MODE_ACCEPT_ALL, BYTES_PER_KILOBYTE, BYTES_PER_MEGABYTE, PROP_BAG_FALSE,
    PROP_BAG_TRUE)

from .analysismodule import AnalysisModule
from .capturetemplate import VoIPSettings
from .fileinformation import FileInformation
from .filter import Filter
from .omniid import OmniId
from .packetfileinformation import PacketFileInformation
from .peektime import PeekTime
from .statslimit import StatsLimit


# XML Tags
_tag_clsid = 'clsid'
_tag_compass = 'Compass'
_tag_enabled = 'enabled'
_tag_alt_enabled = 'Enabled'
_tag_id = 'id'
_tag_name = 'name'
_tag_object = 'obj'
_tag_props = 'properties'
_tag_prop = 'prop'
_tag_type = 'type'
_tag_prop_bag = 'SimplePropBag'

_json_accept = 'accept'
_json_enabled = 'enabled'
_json_items = 'items'
_json_type = 'type'

stats_labels = {
    '_option_break_out': 'BreakOutStats',
    'option_expert': 'Expert',
    'option_graphs': 'Graphs',
    'option_indexing': 'Index',
    'option_log': 'Log',
    'option_packets': 'Packets',
    'option_plugins': 'Plugins',
    'option_statistics': 'Statistics',
    'option_voice': 'Voice',
    '_option_web': 'Web'
}

break_out_stats = {
    'ApplicationStats': 'option_application',
    'BreakOutStats': '_option_break_out',
    'CountryStats': 'option_country',
    'ErrorStats': 'option_error',
    'HistoryStats': 'option_history',
    'NetworkStats': 'option_network',
    'NodeStats': 'option_node',
    'ConversationStats': 'option_node_protocol_detail',
    'ProtocolStats': 'option_protocol',
    'SizeStats': 'option_size',
    'SummaryStats': 'option_summary',
    'TopTalkerStats': 'option_top_talkers',
    'WirelessChannelStats': 'option_wireless_channel',
    'WirelessNodeStats': 'option_wireless_node'
}

break_out_stats_labels = {
    'option_application': 'ApplicationStats',
    'option_country': 'CountryStats',
    'option_error': 'ErrorStats',
    'option_history': 'HistoryStats',
    'option_network': 'NetworkStats',
    'option_node': 'NodeStats',
    'option_node_protocol_detail': 'ConversationStats',
    'option_protocol': 'ProtocolStats',
    'option_size': 'SizeStats',
    'option_summary': 'SummaryStats',
    'option_top_talkers': 'TopTalkerStats',
    'option_wireless_channel': 'WirelessChannelStats',
    'option_wireless_node': 'WirelessNodeStats'
}

limit_types = {
    'none': LIMIT_TYPE_NONE,
    'packets': LIMIT_TYPE_PACKETS,
    'bytes': LIMIT_TYPE_BYTES,
    'buffer': LIMIT_TYPE_BUFFER
}


def _from_prop_boolean(value):
    return int(value) != 0


def _get_clsid(clsid_name):
    class_name_ids = omniscript.get_class_name_ids()
    id = class_name_ids[clsid_name]
    return id.format() if id else ''


def _set_clsid(obj, clsid_name):
    if _tag_clsid not in obj.attrib:
        class_name_ids = omniscript.get_class_name_ids()
        obj.attrib[_tag_clsid] = str(class_name_ids[clsid_name])


def _set_property_value(parent, value_type, value):
    if not isinstance(value, six.string_types):
        value = str(value)
    ET.SubElement(parent, _tag_prop,
                  {_tag_type: str(value_type)}).text = value


def _to_prop_boolean(value):
    if isinstance(value, six.string_types):
        if int(value):
            return PROP_BAG_TRUE
        return PROP_BAG_FALSE
    if value:
        return PROP_BAG_TRUE
    return PROP_BAG_FALSE


class ExpertAuthentication(object):
    """ExpertAuthentication class.
    """

    types = []
    """Type of Authentication:
    0 = None
    1 = EAP
    2 = LEAP
    3 = PEAP
    4 = EAPTLS
    """

    _json_label = 'authentication'

    def __init__(self):
        self.types = []

    def _get_props(self):
        props = {}
        props[_json_accept] = len(self.types) > 0
        # if len(self.types) > 0:
        props[_json_items] = [{_json_enabled: True, _json_type: v} for v in self.types]
        # else:
        #     props[_json_items] = [{_json_enabled: False, _json_type: 0}]
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for prop in props:
            pass

    def _store(self, props):
        if not isinstance(props, dict):
            return

    def is_enabled(self):
        return bool(self.types)


class ExpertChannel(object):
    """ExpertChannel class.
    """

    class ChannleFamily(object):
        """ChannleFamily class.
        """

        band = 0
        """The channel band."""

        channel = 0
        """The channel."""

        frequency = 0
        """The channel frequency."""

        def __init__(self, band, channel, frequency):
            self.band = band
            self.channel = channel
            self.frequency = frequency

        def _get_props(self):
            return {
                _json_enabled: True,
                'band': self.band,
                'channel': self.channel,
                'frequency': self.frequency
            }

    band = ''
    """The channel band."""

    families = []
    """List of ChannelFamily objects."""

    _json_label = 'channel'
    _json_band = 'channelBand'
    _json_family = 'channelFamily'

    def __init__(self):
        self.band = ExpertChannel.band
        self.families = []

    def _get_props(self):
        props = {}
        props[_json_accept] = bool(self.band or self.families)
        props[ExpertChannel._json_band] = ''
        props[ExpertChannel._json_family] = [
            {_json_items: [v._get_props() for v in self.families]}
        ]
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for prop in props:
            pass

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ExpertChannel._json_label] = self._get_props()

    def is_enabled(self):
        return (self.band and self.families)


class ExpertEncryption(object):
    """ExpertEncryption
    """

    protocols = []
    """list of Protocol Types:
    0 = None
    1 = WEP
    2 = CKIP
    3 = TKIP
    4 = CCMP
    """

    _json_label = 'essId'

    def __init__(self):
        self.items = ExpertEncryption.protocols

    def _get_props(self):
        props = {}
        props[_json_accept] = len(self.protocols) > 0
        # if len(self.protocols) > 0:
        props[_json_items] = [{_json_enabled: True, _json_type: v} for v in self.protocols]
        # else:
        #     props[_json_items] = [{_json_enabled: False, _json_type: 0}]
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for prop in props:
            pass

    def _store(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            pass

    def is_enabled(self):
        return bool(self.protocols)


class ExpertEss(object):
    """Expert Ess Identifiers (names) class.
    """

    names = []
    """List of Protocol names."""

    _json_label = 'essId'
    _json_value = 'value'

    def __init__(self):
        self.names = []

    def _get_props(self):
        props = {}
        props[_json_accept] = len(self.names) > 0
        props[_json_items] = [{_json_enabled: True, ExpertEss._json_value: n} for n in self.names]
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for prop in props:
            pass

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ExpertEss._json_label] = self._get_props()

    def is_enabled(self):
        return bool(self.names)


class ExpertVendor(object):
    """Expert Vendor Id
    """

    class Vendor(object):
        """Vendor class.
        """

        access_point = False
        """Is this an this an access point."""

        client = False
        """Does the vendor have a client."""

        value = ''
        """The value of the Vendor."""

        _json_access_point = 'accessPoint'
        _json_client = 'client'
        _json_value = 'value'

        def __init__(self, access_point, client, value):
            self.access_point = access_point
            self.client = client
            self.value = value

        def _get_props(self):
            return {
                ExpertVendor._json_accessPoint: self.access_point,
                ExpertVendor._json_client: self.client,
                ExpertVendor._json_value: self.value
            }

    vendors = []
    """List of Vendor objects."""

    _json_label = 'vendorId'

    def __init__(self):
        self.vendors = []

    def _get_props(self):
        props = {}
        props[_json_accept] = len(self.vendors) > 0
        props[_json_items] = [v._getProps() for v in self.vendors]
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for prop in props:
            pass

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ExpertVendor._json_label] = self._get_props()

    def is_enabled(self):
        return bool(self.vendors)


class ExpertProblem(object):
    """Expert Problem"""

    group_id = 0
    """The group identifier of the problem."""

    id = 0
    """ The Problem Identifier. Call
    <omniscript.omniscript.get_expert_problem_ids()>`
    to get the dictionary of Problem Label to id.
    """

    minimum_sample = 0
    """The minimum number of samples needed to perform this Expert."""

    sensetivity = 0
    """One of the following levels:
    0 = None
    1 = Low
    2 = Medium
    3 = High
    """

    severity = 0
    """"The Problem's Severity, one of the following levels:
    0 = None
    1 = Informational
    2 = Minor
    3 = Major
    4 = Severe
    """

    value = 0
    """The Problem's Value."""

    _json_label = 'problems'

    def __init__(self, props=None):
        self.group_id = ExpertProblem.group_id
        self.id = ExpertProblem.id
        self.minimum_sample = ExpertProblem.minimum_sample
        self.sensetivity = ExpertProblem.sensetivity
        self.severity = ExpertProblem.severity
        self.value = ExpertProblem.value
        self._load(props)

    def _get_props(self):
        props = {}
        props[_json_enabled] = True
        props['settingsGroupId'] = self.group_id
        props['id'] = self.id
        props['minimumSample'] = self.minimum_sample
        props['sensetivity'] = self.sensetivity
        props['severity'] = self.severity
        props['value'] = self.value
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == 'enabled':
                self.enabled = v
            elif k == 'settingGroupId':
                self.group_id = int(v)
            elif k == 'id':
                self.id = int(v)
            elif k == 'minimumSample':
                self.minimum_sample = int(v)
            elif k == 'sensetivity':
                self.sensetivity = int(v)
            elif k == 'severity':
                self.severity = int(v)
            elif k == 'value':
                self.value = int(v)

    def _store(self, props):
        if not isinstance(props, dict):
            return
        props[ExpertProblem._json_label] = self._get_props()


class ExpertSettings(object):
    """The Expert Settings (Preferences).
    """

    max_streams = 50000
    """The maximum number of streams this Expert can track."""

    authentication = ExpertAuthentication()
    """The authentication of this Expert."""

    channel = ExpertChannel()
    """The channel for this Expert."""

    encryption = ExpertEncryption()
    """The ecryption for this Expert."""

    ess = ExpertEss()
    """The ESS of this Expert."""

    vendor = ExpertVendor()
    """The Vendor of this object."""

    problems = []
    """The list of Problems of this Expert."""

    # JSON Tags
    _json_label = 'expertPrefs'
    _json_max_streams = 'maxStreamCount'
    _json_policy = 'policy'
    _json_authentication = 'authentication'
    _json_channel = 'channel'
    _json_encryption = 'encryption'
    _json_ess = 'essId'
    _json_vendor = 'vendorId'
    _json_problems = 'problems'

    def __init__(self):
        self.max_streams = ExpertSettings.max_streams
        self.authentication = ExpertAuthentication()
        self.channel = ExpertChannel()
        self.encryption = ExpertEncryption()
        self.ess = ExpertEss()
        self.vendor = ExpertVendor()
        self.problems = []

    def _get_props(self):
        props = {}
        props[ExpertSettings._json_max_streams] = self.max_streams
        policy = {
            ExpertSettings._json_authentication: self.authentication._get_props(),
            ExpertSettings._json_channel: self.channel._get_props(),
            ExpertSettings._json_encryption: self.encryption._get_props(),
            ExpertSettings._json_ess: self.ess._get_props(),
            ExpertSettings._json_vendor: self.vendor._get_props()
        }
        props[ExpertSettings._json_policy] = policy
        problems = {}
        props[ExpertSettings._json_problems] = problems
        return props

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            pass

    def _store(self, props):
        if not isinstance(props, dict):
            return
        default = ExpertSettings()
        _current = self._get_props()
        _default = default._get_props()
        _props = {
            'settings': {
                'current': _current,
                'default': _default
            }
        }
        props[ExpertSettings._json_label] = _props

    def is_enabled(self):
        return (self.authentication.is_enabled() and self.channel.is_enabled()
                and self.encryption.is_enabled() and self.ess.is_enabled()
                and self.vendor.is_enabled() and bool(self.problems))


class TimeRange(object):
    """A range of time.
    """

    start = None
    """The begining of the Time Range"""

    end = None
    """The ending of the Time Range"""

    # Tags
    _json_start = 'startTime'
    _json_end = 'endTime'

    def __init__(self, start=None, end=None, props=None):
        self.start = PeekTime(start) if start else TimeRange.start
        self.end = PeekTime(end) if end else TimeRange.end
        self._load(props)

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == TimeRange._json_start:
                self.start = PeekTime(v)
            elif k == TimeRange._json_end:
                self.end = PeekTime(v)

    def _store(self):
        if not self.start and not self.end:
            return None
        props = {
            TimeRange._json_start: self.start.iso_time(),
            TimeRange._json_end: self.end.iso_time()
        }
        return props


class ForensicTemplate(object):
    """Forensic Template class.
    Use a Forensic Template object to create a
    :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
    object with the function
    :func:`create_forensic_search()
    <omniscript.omniengine.OmniEngine.create_forensic_search>`.
    """

    adapter_name = ''
    """The name of the search's adapter."""

    capture_name = ''
    """The name of the Capture to search.
    Specifiy either a capture_name or file[], not both.
    If neither is specified than all packet files are searched.
    """

    capture_session_id = 0
    """The index of the Capture Session."""

    conversation_limits = None
    """The Conversation (Node/Protocol Detail) Limits a
    :class:`StatsLimit <omniscript.statslimit.StatsLimit>`
    object. Set the option_node_protocol_detail attribute to True to
    enable Node/Protocol Details Stats. Either Node Stats or Protocol
    Stats must also be enabled or Node/Protocol Detail Stats will be
    disabled.
    """

    end_time = None
    """The optional ending timestamp, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`
    of the search time span.
    """

    expert = None
    """The Expert Settings (Preferences) of the search"""

    filename = None
    """An optional file name of the Forensic Search Tempalte file."""

    files = []
    """The options list of packet files to search.
    If this list is empty and capture_name is empty, then all packet files
    are search. Do not specifiy capture_name if files is not empty.
    """

    filter = None
    """The
    :class:`Filter <omniscript.filter.Filter>`
    object of the search.
    Use
    :func:`find_filter()
    <omniscript.omniengine.OmniEngine.create_forensic_search>`
    to get one of the engine's filters.
    """

    filter_mode = MODE_ACCEPT_ALL
    """The filter mode:
           0 for MODE_ACCEPT_ALL,
           1 for MODE_ACCEPT_ANY_MATCHING,
           2 for MODE_REJECT_ALL,
           3 for MODE_REJECT_MATCHING,
           4 for MODE_ACCEPT_ALL_MATCHING,
           5 for MODE REJECT_ALL_MATCHING
    """

    graph_interval = 0
    """The time interval for graphing when option[graphs] is enabled."""

    limit = LIMIT_TYPE_NONE
    """Limit the search by:
           0 for 'None' (default),
           1 for 'Packets',
           2 for 'Bytes',
           3 for 'Buffer'.
    """

    limit_size = 0
    """The number of Packets, Bytes or Buffer size in bytes to limit the
    search to."""

    media_type = MEDIA_TYPE_802_3
    """The Media Type of the search."""

    media_sub_type = MEDIA_SUB_TYPE_NATIVE
    """The Media Sub Type of the search."""

    name = ''
    """The name of the search."""

    node_limits = None
    """The Node Limits a
    :class:`StatsLimit <omniscript.statslimit.StatsLimit>`
    object. Set the option_node attribute to True to enable Node Stats.
    """

    plugins = None
    """The list of Plugin (Analysis Module) Ids.
    A Plugin Id may be a string,
    :class:`OmniId <omniscript.omniid.OmniId>`
    or an
    :class:`AnalysisModule <omniscript.analysismodule.AnalysisModule>`
    object.
    Call the
    :func:`get_analysis_module_list()
    <omniscript.omniengine.OmniEngine.get_analysis_module_list>`
    method to get the engine's list of plugins.
    """

    plugins_config = None
    """The list of Plugins (Analysis Modules) configuration."""

    protocol_limits = None
    """The Protocol Limits a
    :class:`StatsLimit <omniscript.statslimit.StatsLimit>`
    object. Set the option_protocol attribute to enable Protocol Stats.
    """

    session_id = None
    """The session id of the search. Do Not Modify."""

    start_time = None
    """The optional begining timestamp, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    of the search time span.
    """

    time_ranges = None
    """The Time Range (start to end) to search."""

    voip = None
    """The VoIP settings, as
    :class:`VoIPSettings <omniscript.capturetemplate.VoIPSettings>`,
    """

    option_all_plugins = False
    """Are all plugins enabled?"""

    option_application = False
    """Is the Application Statistics option enabled?"""

    option_compass = False
    """Is Compass enabled?"""

    option_country = False
    """Is the Country Statistics option enabled?"""

    option_database = False
    """Is the Use Database option enabled?"""

    option_delete_files = False
    """Is the Delete Files option enabled?"""

    option_error = False
    """Is the Error Statistics option enabled?"""

    option_graphs = False
    """Is the Graphs enabled?"""

    option_history = False
    """Is the Traffic History Statistics option enabled?"""

    option_indexing = False
    """Is the Indexing option enabled?"""

    option_log = False
    """Is the Events Log option enabled?"""

    option_network = False
    """Is the Network Statistics option enabled?"""

    option_node_protocol_detail = False
    """Is the Node/Protocol Detail Statistics option enabled?
    Either Node Stats or Protocol Stats must be enabled or Node/Protocol
    Stats will be disabled when the Forensic Search is created.
    """

    option_packets = False
    """Is the Packet option enabled?"""

    option_passive_name_resolution = False
    """Is the Passive Name Resolution option enabled?"""

    option_plugins = False
    """Is the Analysis Modules (Plugins) option enabled?"""

    option_size = False
    """Is the Size Statistics option enabled?"""

    option_statistics = False
    """Is the Statistics option enabled?
    The Statistics option is only enabled by reading in an existing template.
    """

    option_summary = False
    """Is the Summary Statistics option enabled?"""

    option_top_talkers = False
    """Is the Top Talkers option enabled?"""

    option_voice = False
    """Is the Voice and Video Statistics option enabled?"""

    option_web = False
    """ Is the Web Statistics option enabled?"""

    option_wireless_channel = False
    """Is the Wireless Channel Statistics option enabled?"""

    option_wireless_node = False
    """Is the Wireless Node Statistics option enabled?"""

    # Private attributes
    _option_break_out = True
    """Are new options enabled?"""

    # Tags
    _json_classid = 'clsid'
    _json_adapter_name = 'adapterName'
    _json_application = 'application'
    _json_capture_name = 'captureName'
    _json_capture_session_id = 'captureSessionId'
    _json_conversation = 'conversation'
    _json_conversation_limit = 'conversationLimitStatisticSettings'
    _json_country = 'country'
    _json_database = 'useDatabase'
    _json_delete_files = 'deleteFiles'
    _json_error = 'error'
    _json_expert = 'expert'
    _json_expert_prefs = 'expertPrefs'
    _json_end_time = 'endTime'
    _json_files = 'files'
    _json_filter = 'filter'
    _json_filter_mode = 'filterMode'
    _json_filters = 'filters'
    _json_graphs = 'graphs'
    _json_graph_settings = 'graphSettings'
    _json_hidden_plugins_config = 'hiddenPluginsConfig'
    _json_hidden_plugins_list = 'hiddenPluginsList'
    _json_history = 'history'
    _json_indexing = 'indexing'
    _json_limit_number = 'limitNumber'
    _json_limit_type = 'limitType'
    _json_log = 'log'
    _json_media_sub_type = 'mediaSubType'
    _json_media_type = 'mediaType'
    _json_name = 'name'
    _json_network = 'network'
    _json_node = 'node'
    _json_node_limit = 'nodeLimitStatisticSettings'
    _json_packets = 'packets'
    _json_passive_name_resolution = 'passiveNameResolution'
    _json_plugins = 'plugins'
    _json_plugins_config = 'pluginsConfig'
    _json_plugins_list = 'pluginsList'
    _json_protocol = 'protocol'
    _json_protocol_limit = 'protocolLimitStatisticSettings'
    _json_single_files = 'singleFiles'
    _json_size = 'size'
    _json_start_time = 'startTime'
    _json_summary = 'summary'
    _json_time_ranges = 'timeRanges'
    _json_voice = 'voice'
    _json_voip = 'voipSettings'
    _json_web = 'web'
    _json_wireless_channel = 'wirelessChannel'
    _json_wireless_node = 'wirelessNode'

    _tag_root_name = 'ForensicTemplate'
    _tag_adapter_name = 'AdapterName'
    _tag_break_out = 'BreakOutStats'
    _tag_capture_name = 'Capture'
    _tag_config_plugins = 'PluginsConfig'
    _tag_country = 'Country'
    _tag_end_time = 'EndTime'
    _tag_expert = 'Expert'
    _tag_filter = 'Filter'
    _tag_filter_mode = 'FilterMode'
    _tag_graphs = 'Graphs'
    _tag_graph_interval = 'GraphsSampleInterval'
    _tag_indexing = 'Index'
    _tag_limit = 'LimitType'
    _tag_limit_count = 'LimitNum'
    _tag_log = 'Log'
    _tag_media_type = 'MediaType'
    _tag_media_sub_type = 'MediaSubType'
    _tag_name = 'Name'
    _tag_packets = 'Packets'
    _tag_plugin_alt = 'plugin'
    _tag_plugins = 'Plugins'
    _tag_plugins_alt = 'plugins'
    _tag_plugins_clsid = 'PropertyList'
    _tag_plugins_list = 'PluginsList'
    _tag_plugins_config = 'PluginsConfig'
    _tag_prop = 'prop'
    _tag_properties = 'properties'
    _tag_property_list = 'PropertyList'
    _tag_session_id = 'CaptureSessionID'
    _tag_single_file = 'SingleFile'
    _tag_size = 'Size'
    _tag_start_time = 'StartTime'
    _tag_stats = 'Statistics'
    _tag_summary = 'SummaryStats'
    _tag_voice = 'Voice'
    _tag_voip = 'VoIPConfig'
    _tag_web = 'Web'

    def __init__(self, name=None, props=None, filename=None, node=None):
        self.adapter_name = ForensicTemplate.adapter_name
        self.capture_session_id = ForensicTemplate.capture_session_id
        self.capture_name = ForensicTemplate.capture_name
        self.conversation_limits = StatsLimit('conversationLimitStatisticSettings', limit=200000)
        self.end_time = ForensicTemplate.end_time
        self.expert = ExpertSettings()
        self.filename = filename
        self.files = []
        self.filter = []
        self.filter_mode = ForensicTemplate.filter_mode
        self.graph_interval = ForensicTemplate.graph_interval
        self.limit = ForensicTemplate.limit
        self.limit_size = ForensicTemplate.limit_size
        self.media_type = None      # ForensicTemplate.media_type
        self.media_sub_type = None  # ForensicTemplate.media_sub_type
        self.name = name if name is not None else ForensicTemplate.name
        self.node_limits = StatsLimit('nodeLimitStatisticSettings')
        self.plugins = []
        self.plugins_config = []
        self.protocol_limits = StatsLimit('protocolLimitStatisticSettings')
        self.session_id = ForensicTemplate.session_id
        self.start_time = ForensicTemplate.start_time
        self.time_ranges = []
        self.voip = VoIPSettings()
        self.option_all_plugins = ForensicTemplate.option_all_plugins
        self.option_application = ForensicTemplate.option_application
        self.option_compass = ForensicTemplate.option_compass
        self.option_country = ForensicTemplate.option_country
        self.option_database = ForensicTemplate.option_database
        self.option_delete_files = ForensicTemplate.option_delete_files
        self.option_error = ForensicTemplate.option_error
        self.option_graphs = ForensicTemplate.option_graphs
        self.option_history = ForensicTemplate.option_history
        self.option_indexing = ForensicTemplate.option_indexing
        self.option_log = ForensicTemplate.option_log
        self.option_network = ForensicTemplate.option_network
        self.option_node_protocol_detail = ForensicTemplate.option_node_protocol_detail
        self.option_packets = ForensicTemplate.option_packets
        self.option_passive_name_resolution = ForensicTemplate.option_passive_name_resolution
        self.option_plugins = ForensicTemplate.option_plugins
        self.option_size = ForensicTemplate.option_size
        self.option_statistics = ForensicTemplate.option_statistics
        self.option_summary = ForensicTemplate.option_summary
        self.option_top_talkers = ForensicTemplate.option_top_talkers
        self.option_voice = ForensicTemplate.option_voice
        self.option_web = False
        self.option_wireless_channel = ForensicTemplate.option_wireless_channel
        self.option_wireless_node = ForensicTemplate.option_wireless_node
        self._option_break_out = ForensicTemplate._option_break_out
        if self.filename:
            tree = ET.parse(self.filename)
            root = tree.getroot()
            if root.tag == ForensicTemplate._tag_root_name:
                self._load_xml(root)
        elif node:
            self._load_xml(node)
        else:
            self._load(props)

    def __str__(self):
        return f'ForensicTemplate: {self.name}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == '':
                pass

    def _load_xml(self, props):
        if props is None:
            return
        for prop in props:
            name = prop.tag
            if name == ForensicTemplate._tag_adapter_name:
                self.adapter_name = prop.text
            elif name == ForensicTemplate._tag_capture_name:
                self.capture_name = prop.text
            elif name == ForensicTemplate._tag_country:
                self.option_country = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_end_time:
                self.end_time = PeekTime(prop.text)
            elif name == ForensicTemplate._tag_expert:
                self.option_expert = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_filter:
                self.filter = Filter(criteria=prop)
            elif name == ForensicTemplate._tag_filter_mode:
                self.filter_mode = int(prop.text)
            elif name == ForensicTemplate._tag_graphs:
                self.option_graphs = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_graph_interval:
                self.graph_interval = int(prop.text)
            elif name == ForensicTemplate._tag_indexing:
                self.option_indexing = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_limit:
                self.limit = int(prop.text)
            elif name == ForensicTemplate._tag_limit_count:
                self.limit = int(prop.text)
            elif name == ForensicTemplate._tag_log:
                self.option_log = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_media_type:
                self.media_type = int(prop.text)
            elif name == ForensicTemplate._tag_media_sub_type:
                self.media_sub_type = int(prop.text)
            elif name == ForensicTemplate._tag_name:
                self.name = prop.text
            elif name == ForensicTemplate._tag_packets:
                self.option_packets = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_plugins:
                self.option_plugins = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_plugins_list:
                self._load_plugins(prop)
            elif name == ForensicTemplate._tag_session_id:
                self.session_id = OmniId(prop.text) if prop.text[0] == '{' else None
            elif name == ForensicTemplate._tag_single_file:
                self.single_file = prop.text
            elif name == ForensicTemplate._tag_start_time:
                self.start_time = PeekTime(prop.text)
            elif name == ForensicTemplate._tag_stats:
                self.option_statistics = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_summary:
                self.option_summary = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_voice:
                self.option_voice = _from_prop_boolean(prop.text)
            elif name == ForensicTemplate._tag_voip:
                self.voip = VoIPSettings()
                self.voip._load_raw(prop)
            elif name == ForensicTemplate._tag_web:
                # self._option_web = _from_prop_boolean(prop.text)
                self._option_web = False
            elif name == ForensicTemplate._tag_break_out:
                self._option_break_out = _from_prop_boolean(prop.text)
        # Set the break out statistics.
        if self._option_break_out:
            for prop in props:
                name = prop.tag
                if name in break_out_stats:
                    setattr(self, break_out_stats[name], _from_prop_boolean(prop.text))
            self.node_limits.enabled = self.option_node
            self.protocol_limits.enabled = self.option_protocol
            self.node_protocol_detail_limits.enabled = self.option_node_protocol_detail
        self._option_break_out = True

    def _load_plugins(self, pluginlist):
        self.plugins = []
        props = pluginlist.find(ForensicTemplate._tag_properties)
        if props is not None:
            for prop in props.findall(ForensicTemplate._tag_prop):
                self.plugins.append(OmniId(prop.text))
        compass_id = omniscript.get_class_name_ids()[_tag_compass]
        self.option_compass = compass_id in self.plugins

    def add_file(self, name):
        """Add a file to the search."""
        if isinstance(name, FileInformation):
            self.files.append(name.name)
        elif isinstance(name, PacketFileInformation):
            self.files.append(name.path)
            if self.media_type is None:
                self.media_type = name.media_type
                self.media_sub_type = name.media_sub_type
        # elif isinstance(name, Forensic File <<< added space to hide from text search.):
        #     self.files.append(name.path)
        #     if self.media_type == None:
        #         self.media_type = name.media_type
        #         self.media_sub_type = name.media_sub_type
        else:
            self.files.append(name)

    def add_plugin(self, plugin):
        """Add a plugin id to the search.
        A plugin id may be a string,
        :class:`OmniId <omniscript.omniid.OmniId>`
        or an
        :class:`AnalysisModule <omniscript.analysismodule.AnalysisModule>`
        object.
        """
        if isinstance(plugin, six.string_types):
            if OmniId.is_id(plugin):
                self.plugins.append(OmniId(plugin))
            else:
                self.plugins.append(plugin)
        elif isinstance(plugin, OmniId):
            self.plugins.append(plugin)
        elif isinstance(plugin, AnalysisModule):
            self.plugins.append(plugin.id)
        self.option_plugins = True

    def is_node_limits_enabled(self):
        """Is the Node Statistics option enabled?"""
        if self.node_limits is None:
            return False
        return self.node_limits.enabled

    def is_conversation_limits_enabled(self):
        """Is the Conversation (Node Protocol) Statistics option enabled?"""
        if self.node_conversation_limits is None:
            return False
        return self.node_conversation_limits.enabled

    def is_protocol_limits_enabled(self):
        """Is the Protocol Statistics option enabled?"""
        if self.protocol_limits is None:
            return False
        return self.protocol_limits.enabled

    def set_all(self, enable=True):
        """Enable or disable all options."""
        self.set_all_analysis_options(enable)
        self.set_all_output_options(enable)

    def set_all_analysis_options(self, enable=True):
        """Enable or disable all the analysis options."""
        self.node_limits.enabled = enable
        self.node_protocol_detail_limits.enabled = enable
        self.protocol_limits.enabled = enable
        self.option_all_plugins = enable
        self.option_application = enable
        self.option_compass = enable
        self.option_country = enable
        self.option_database = enable
        self.option_delete_files = enable
        self.option_error = enable
        self.option_history = enable
        self.option_network = enable
        self.option_passive_name_resolution = enable
        self.option_plugins = enable
        self.option_size = enable
        self.option_summary = enable
        self.option_top_talkers = enable
        self.option_voice = enable
        self.option_web = enable
        self.option_wireless_channel = enable
        self.option_wireless_node = enable

    def set_all_output_options(self, enable=True):
        """Enable or disable all the output options."""
        self.option_graphs = enable
        self.option_indexing = enable
        self.option_log = enable
        self.option_packets = enable

    def set_limit(self, limit, limit_size):
        """Set a limit on the search.

        Args:
            limit (str): either 'none', 'packets', 'bytes' or 'buffer'.
            limit_size (int): packets are in 1k units, bytes and buffer
            in 1MB units.
        """
        self.limit = limit_types[limit]
        if self.limit == LIMIT_TYPE_BYTES or self.limit == LIMIT_TYPE_BUFFER:
            self.limit_size = limit_size * BYTES_PER_MEGABYTE
        elif self.limit == LIMIT_TYPE_PACKETS:
            self.limit_size = limit_size * BYTES_PER_KILOBYTE
        else:
            self.limit_size = 0

    def store(self, engine=None, new=False, pretty=False, modify=False):
        """Return the Forensic Template as a serialized JSON formatted
        string.
        """
        props = {}
        if self.adapter_name:
            if isinstance(self.adapter_name, six.string_types):
                _name = self.adapter_name
            elif isinstance(self.adapter_name, Adapter):
                _name = self.adapter_name.name
            else:
                _name = self.adapter_name
            props[ForensicTemplate._json_adapter_name] = _name
        if self.option_application:
            props[ForensicTemplate._json_application] = self.option_application
        if self.capture_name:
            props[ForensicTemplate._json_capture_name] = self.capture_name
        if self.capture_session_id > 0:
            props[ForensicTemplate._json_capture_session_id] = self.capture_session_id
        if isinstance(self.conversation_limits, StatsLimit) and self.conversation_limits.enabled:
            props[ForensicTemplate._json_conversation] = True
            self.conversation_limits._store(props)
        if self.option_country:
            props[ForensicTemplate._json_country] = self.option_country
        if self.option_delete_files:
            props[ForensicTemplate._json_delete_files] = self.option_delete_files
        if isinstance(self.end_time, PeekTime) and bool(self.end_time):
            props[ForensicTemplate._json_end_time] = self.end_time.iso_time()
        if self.option_error:
            props[ForensicTemplate._json_error] = self.option_error
        if isinstance(self.expert, ExpertSettings) and self.expert.is_enabled():
            props[ForensicTemplate._json_expert] = True
            self.expert._store(props)
        if len(self.files) > 0:
            props[ForensicTemplate._json_files] = True

        # props['files'] = self.option_files
        if self.filter:
            props[ForensicTemplate._json_filter] = len(self.filter) > 0
            if self.filter_mode > 0:
                props[ForensicTemplate._json_filter_mode] = self.filter_mode
        if self.option_graphs:
            props[ForensicTemplate._json_graphs] = self.option_graphs
        if self.option_history:
            props[ForensicTemplate._json_history] = self.option_history
        if self.option_indexing:
            props[ForensicTemplate._json_indexing] = self.option_indexing
        if (self.limit > 0) and (self.limit_size > 0):
            props[ForensicTemplate._json_limit_number] = self.limit_size
            props[ForensicTemplate._json_limit_type] = self.limit
        if self.option_log:
            props[ForensicTemplate._json_log] = self.option_log

        # the two required attributes:
        props[ForensicTemplate._json_media_type] = (self.media_type
                                                    if self.media_type is not None
                                                    else ForensicTemplate.media_type)
        props[ForensicTemplate._json_media_sub_type] = (self.media_sub_type
                                                        if self.media_sub_type is not None
                                                        else ForensicTemplate.media_sub_type)

        if self.name:
            props[ForensicTemplate._json_name] = self.name
        if self.option_network:
            props[ForensicTemplate._json_network] = self.option_network
        if isinstance(self.node_limits, StatsLimit) and self.node_limits.enabled:
            props[ForensicTemplate._json_node] = True
            self.node_limits._store(props)
        if self.option_packets:
            props[ForensicTemplate._json_packets] = self.option_packets
        if self.option_passive_name_resolution:
            props[ForensicTemplate._json_passive_name_resolution] = (
                self.option_passive_name_resolution)

        if self.plugins:
            pl = {
                ForensicTemplate._json_classid: _get_clsid(ForensicTemplate._tag_plugins_clsid),
                ForensicTemplate._json_plugins: False,
                ForensicTemplate._json_plugins_list: []
            }
            if self.plugins:
                pl[ForensicTemplate._json_plugins] = True
                for plugin in self.plugins:
                    if isinstance(plugin, AnalysisModule):
                        id = plugin.id
                    elif isinstance(plugin, OmniId):
                        id = plugin
                    else:
                        id = OmniId(plugin)
                    pl[ForensicTemplate._json_plugins_list].append(id.format())
            props[ForensicTemplate._json_plugins_list] = pl

        if isinstance(self.protocol_limits, StatsLimit) and self.protocol_limits.enabled:
            props[ForensicTemplate._json_protocol] = True
            self.protocol_limits._store(props)
        if self.files:
            props[ForensicTemplate._json_single_files] = [f for f in self.files]
        if self.option_size:
            props[ForensicTemplate._json_size] = self.option_size
        if isinstance(self.start_time, PeekTime) and bool(self.start_time):
            props[ForensicTemplate._json_start_time] = self.start_time.iso_time()
        if self.option_summary:
            props[ForensicTemplate._json_summary] = self.option_summary
        if len(self.time_ranges) > 0:
            props[ForensicTemplate._json_time_ranges] = [tr._store() for tr in self.time_ranges]
        if self.option_database:
            props[ForensicTemplate._json_database] = self.option_database
        if self.option_voice:
            props[ForensicTemplate._json_voice] = self.option_voice
            if isinstance(self.voip, VoIPSettings):
                props[ForensicTemplate._json_voip] = self.voip._get_props()
        if self.option_web:
            props[ForensicTemplate._json_web] = self.option_web
        if self.option_wireless_channel:
            props[ForensicTemplate._json_wireless_channel] = self.option_wireless_channel
        if self.option_wireless_node:
            props[ForensicTemplate._json_wireless_node] = self.option_wireless_node
        return json.dumps(props)

    def to_xml(self, engine=None):
        """Returns the Forensic Search encoded in XML as a string."""
        if not self._option_break_out:
            for a, p in break_out_stats_labels.iteritems():
                if getattr(self, a):
                    self._option_break_out = True
                    self.option_statistics = False
                    break

        # The Compass hack.
        compass_id = omniscript.get_class_name_ids()[_tag_compass]
        if self.option_compass:
            self.option_plugins = True
            if compass_id not in self.plugins:
                self.plugins.append(compass_id)

        # Sync the stats limits with the options.
        self.option_node_protocol_detail = (self.option_node_protocol_detail
                                            and (self.option_node or self.option_protocol))
        self.node_limits.enabled = self.option_node
        self.node_protocol_detail_limits.enabled = self.option_node_protocol_detail
        self.protocol_limits.enabled = self.option_protocol

        search = ET.Element(ForensicTemplate._tag_root_name)
        if self.files and len(self.files) > 0:
            for f in self.files:
                ET.SubElement(search, ForensicTemplate._tag_single_file).text = f
        ET.SubElement(search, ForensicTemplate._tag_name).text = self.name
        ET.SubElement(search, ForensicTemplate._tag_session_id).text = (str(self.session_id
                                                                            if self.session_id
                                                                            else -1))
        ET.SubElement(search, ForensicTemplate._tag_media_type).text = str(self.media_type)
        ET.SubElement(search, ForensicTemplate._tag_media_sub_type).text = str(self.media_sub_type)
        if self.adapter_name:
            ET.SubElement(search, ForensicTemplate._tag_adapter_name).text = self.adapter_name
        else:
            ET.SubElement(search, ForensicTemplate._tag_adapter_name)
        if self.start_time and self.end_time:
            ET.SubElement(search, ForensicTemplate._tag_start_time).text = str(self.start_time)
            ET.SubElement(search, ForensicTemplate._tag_end_time).text = str(self.end_time)
        ET.SubElement(search, ForensicTemplate._tag_filter_mode).text = str(self.filter_mode)
        if self.filter is not None:
            _filter = ET.SubElement(search, ForensicTemplate._tag_filter)
            self.filter._store(_filter)

        # options
        for a, p in stats_labels.iteritems():
            ET.SubElement(search, p).text = str(int(getattr(self, a)))

        # break_out indicates new options format.
        if self._option_break_out:
            for a, p in break_out_stats_labels.iteritems():
                ET.SubElement(search, p).text = str(int(getattr(self, a)))
            search.append(self.node_limits.to_xml(1))
            search.append(self.protocol_limits.to_xml(1))
            search.append(self.node_protocol_detail_limits.to_xml(1))

        if self.capture_name and len(self.capture_name) > 0:
            ET.SubElement(search, ForensicTemplate._tag_capture_name).text = self.capture_name
        ET.SubElement(search, ForensicTemplate._tag_limit).text = str(self.limit)
        ET.SubElement(search, ForensicTemplate._tag_limit_count).text = str(self.limit_size)
        ET.SubElement(search, ForensicTemplate._tag_graph_interval).text = str(self.graph_interval)

        if self.option_voice and self.voip:
            self.voip._store_raw(search)

        plugins_id = omniscript.get_class_name_ids()[ForensicTemplate._tag_plugins_clsid]
        plugins = ET.SubElement(search, ForensicTemplate._tag_plugins_list,
                                {'clsid': str(plugins_id)})
        props = ET.SubElement(plugins, ForensicTemplate._tag_properties)
        if self.option_plugins and (self.option_all_plugins or self.plugins):
            module_list = engine.get_analysis_module_list() if engine else []
            _set_clsid(plugins, ForensicTemplate._tag_property_list)
            if self.option_all_plugins:
                for module in module_list:
                    if module.id == compass_id:
                        if self.option_compass:
                            _set_property_value(props, 8, module.id)
                    else:
                        _set_property_value(props, 8, module.id)
            else:
                for plugin in self.plugins:
                    id = None
                    if isinstance(plugin, six.string_types):
                        if OmniId.is_id(plugin):
                            id = OmniId(plugin)
                        else:
                            module = next((i for i in module_list
                                           if getattr(i, 'name') == plugin), None)
                            if module:
                                id = module.id
                    elif isinstance(plugin, OmniId):
                        id = plugin
                    elif isinstance(plugin, AnalysisModule):
                        id = plugin.id
                    if id:
                        if id == compass_id:
                            if self.option_compass:
                                _set_property_value(props, 8, id)
                        else:
                            _set_property_value(props, 8, id)

        return ET.tostring(search).replace('\n', '')

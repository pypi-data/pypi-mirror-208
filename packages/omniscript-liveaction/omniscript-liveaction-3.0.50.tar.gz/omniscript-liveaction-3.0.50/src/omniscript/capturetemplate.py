"""CaptureTemplate class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import json
import six
import xml.etree.ElementTree as ET
from enum import Enum

import omniscript

from .invariant import (
    AdapterType, Severity, FILTER_MODE_ACCEPT_MATCHING_ANY, PROP_BAG_FALSE, PROP_BAG_TRUE)

from .adapter import Adapter
from .analysismodule import AnalysisModule
from .filter import Filter
from .omniid import OmniId
from .omnierror import OmniError
from .peektime import PeekTime
from .statslimit import StatsLimit
from .voipsettings import VoIPSettings

from .alarm import find_alarm
from .analysismodule import find_analysis_module
from .filter import find_filter
from .graphtemplate import find_graph_template

LOAD_FROM_NONE = 0
LOAD_FROM_FILE = 1
LOAD_FROM_NODE = 2

SECONDS_IN_A_MINUTE = 60
MINUTES_IN_A_HOUR = 60
SECONDS_IN_A_HOUR = SECONDS_IN_A_MINUTE * MINUTES_IN_A_HOUR
HOURS_IN_A_DAY = 24
SECONDS_IN_A_DAY = SECONDS_IN_A_HOUR * HOURS_IN_A_DAY

BYTES_IN_A_KILOBYTE = 1024
BYTES_IN_A_MEGABYTE = 1024 * 1024
BYTES_IN_A_GIGABYTE = 1024 * 1024 * 1024

GRAPHS_INTERVAL_SECONDS = 1
GRAPHS_INTERVAL_MINUTES = 2
GRAPHS_INTERVAL_HOURS = 3
GRAPHS_INTERVAL_DAYS = 4

interval_multiplier = [
    0,
    1,
    SECONDS_IN_A_MINUTE,
    SECONDS_IN_A_HOUR, SECONDS_IN_A_DAY
]
interval_labels = [
    'None',
    'seconds',
    'minutes',
    'hours',
    'days'
]

# Tags
_tag_classid = '_class_id'
_tag_enabled = 'enabled'
_tag_alt_enabled = 'Enabled'
_tag_id = 'id'
_tag_name = 'name'
_tag_object = 'obj'
_tag_props = 'properties'
_tag_prop = 'prop'
_tag_type = 'type'
_tag_prop_bag = 'SimplePropBag'
_tag_compass = 'Compass'
_tag_value = 'value'
_tag_unknown = ''

# JSON Tags
_json_classid = 'clsid'
_json_enabled = 'enabled'
_json_properties = 'properties'

jtrue = 'true'
jfalse = 'false'


def jbool(b):
    """Returns 'true' if 'b' is True else 'false'."""
    return jtrue if b else jfalse


def _to_interval_units(seconds):
    if (seconds % SECONDS_IN_A_DAY) == 0:
        return ((seconds / SECONDS_IN_A_DAY), GRAPHS_INTERVAL_DAYS)
    if (seconds % SECONDS_IN_A_HOUR) == 0:
        return ((seconds / SECONDS_IN_A_HOUR), GRAPHS_INTERVAL_HOURS)
    if (seconds % SECONDS_IN_A_MINUTE) == 0:
        return ((seconds / SECONDS_IN_A_MINUTE), GRAPHS_INTERVAL_MINUTES)
    return (seconds, GRAPHS_INTERVAL_SECONDS)


def _from_prop_boolean(value):
    return int(value) != 0


def _to_prop_boolean(value):
    if isinstance(value, six.string_types):
        if int(value):
            return PROP_BAG_TRUE
        return PROP_BAG_FALSE
    if value:
        return PROP_BAG_TRUE
    return PROP_BAG_FALSE


def _find_properties(template):
    """Find the main Property Bag of the Capture Template."""
    # or next(e for e in template.iter() if e.tag == 'properties')
    props = template.find(_tag_props)
    if props is None:
        # Restart Capture Template File
        props = template.find('CaptureTemplate/properties')
    return props


def _find_property(props, key):
    if props is None:
        return None
    return next((p for p in props if _tag_name in p.attrib and p.attrib[_tag_name] == key), None)


def _get_class_id(name):
    class_name_ids = omniscript.get_class_name_ids()
    id = class_name_ids[name]
    return id.format() if id else ''


def _is_attribute_enabled(prop, attrib):
    """Return if an attribute of a node is aa non-zero value."""
    return int(prop.attrib.get(attrib, '0')) != 0


def _is_prop_enabled(prop):
    """Return if a prop node has an enabled attribute set to a non-zero
    value.
    """
    return int(prop.attrib.get('enabled', '0')) != 0


def _set_property(parent, key, value_type, value):
    if not isinstance(value, six.string_types):
        value = str(value)
    prop = _find_property(parent, key)
    if prop is not None:
        prop.text = value
        return
    if key:
        ET.SubElement(parent, _tag_prop, {_tag_name: key, _tag_type: str(value_type)}).text = value
    else:
        ET.SubElement(parent, _tag_prop, {_tag_type: str(value_type)}).text = value

# def _set_label_clsid(obj, label, clsid_name):
#     if not _tag_classid in obj.attrib:
#         class_name_ids = omniscript.get_class_name_ids()
#         obj.attrib[_tag_classid] = str(class_name_ids[clsid_name])
#     if not _tag_name in obj.attrib:
#         obj.attrib[_tag_name] = label


class AdditionalReportsStatisticsSettings(object):
    """The Additional Reports Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_conversations_only = False
    option_expert_log = False
    option_voip = False
    option_expert_summary = False
    option_executive_summary = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_conversations_only = 'option_conversations_only'
    _tag_expert_log = 'option_expert_log'
    _tag_voip = 'option_voip'
    _tag_expert_summary = 'option_expert_summary'
    _tag_executive_summary = 'option_executive_summary'

    _additional_reports_stats_prop_dict = {
        'outputAdditionalNode': _tag_output_statistics,
        'outputConversationsOnly': _tag_conversations_only,
        'outputExpertLog': _tag_expert_log,
        'outputVoIP': _tag_voip,
        'outputExpertSummary': _tag_expert_summary,
        'outputExecutiveSummary': _tag_executive_summary
    }

    def __init__(self):
        self.option_output_statistics = (
            AdditionalReportsStatisticsSettings.option_output_statistics)
        self.option_output_statistics = (
            AdditionalReportsStatisticsSettings.option_output_statistics)
        self.option_conversations_only = (
            AdditionalReportsStatisticsSettings.option_conversations_only)
        self.option_expert_log = AdditionalReportsStatisticsSettings.option_expert_log
        self.option_voip = AdditionalReportsStatisticsSettings.option_voip
        self.option_expert_summary = AdditionalReportsStatisticsSettings.option_expert_summary
        self.option_executive_summary = (
            AdditionalReportsStatisticsSettings.option_executive_summary)

    def _load(self, props, engine):
        """Load the  Statics Settings from a Dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = AdditionalReportsStatisticsSettings._additional_reports_stats_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    setattr(self, a, v)


class CaptureLimit(object):
    """The Capture Limit of a Trigger Event Object.
    """

    _class_id = None
    """The Class Identifier of the object."""

    bytes = 0
    """The number of bytes needed to trigger the Trigger."""

    enabled = False
    """Is the Capture Limit enabled?"""

    # Tags
    _json_bytes = 'bytesCaptured'

    _tag_class_name = 'BytesCapturedTriggerEvent'
    _tag_bytes = 'bytes'

    _capture_limit_prop_dict = {
        _json_classid: _tag_classid,
        _tag_enabled: _tag_enabled,
        _json_bytes: _tag_bytes
    }

    def __init__(self, criteria=None):
        self.bytes = CaptureLimit.bytes
        self.enabled = CaptureLimit.enabled
        self._load(criteria)

    def _load(self, props):
        """Load the Capture Limit from a Dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = CaptureLimit._capture_limit_prop_dict.get(k)
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == _tag_enabled:
                    self.enabled = v
                elif a == CaptureLimit._tag_bytes:
                    self.bytes = int(v)
                else:
                    pass

    def _store(self):
        props = {}
        props[CaptureLimit._json_bytes] = self.bytes
        props[_json_enabled] = self.enabled
        props[_json_classid] = _get_class_id(CaptureLimit._tag_class_name)
        return props


class DateLimit(object):
    """The DateLimit of a Trigger Event Object.
    """

    _class_id = None
    """The Class Identifier of the object."""

    elapsed_time = 0
    """The number of nanoseconds"""

    enabled = False
    """Is the Date Limit enabled?"""

    time = None
    """The timestamp of the Date Limit, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    When option_use_elapsed is true create a PeekTime with the time
    in nanoseconds. PeekTime(2 * 1000000000) is 2 seconds.
    """

    option_use_date = False
    """Use the date of the time?"""

    option_use_elapsed = False
    """Use the elapsed time?"""

    # Tags
    _json_elapsed_time = 'elapsedTime'
    _json_time = 'time'
    _json_use_date = 'useDate'
    _json_use_elapsed = 'useElapsedTime'

    _tag_class_name = 'TimeTriggerEvent'
    _tag_elapsed_time = 'elapsed_time'
    _tag_time = 'time'
    _tag_use_date = 'use_date'
    _tag_use_elapsed = 'use_elapsed'
    _tag_time = 'time'

    _date_limit_prop_dict = {
        _json_classid: _tag_classid,
        _json_elapsed_time: _tag_elapsed_time,
        _tag_enabled: _tag_enabled,
        _json_time: _tag_time,
        _json_use_date: _tag_use_date,
        _json_use_elapsed: _tag_use_elapsed
    }

    def __init__(self, criteria=None):
        self.elapsed_time = DateLimit.elapsed_time
        self.enabled = DateLimit.enabled
        self.time = PeekTime(0)
        self.option_use_date = DateLimit.option_use_date
        self.option_use_elapsed = DateLimit.option_use_elapsed
        self._load(criteria)

    def _load(self, props):
        """Load the Date Limit from a Dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = DateLimit._date_limit_prop_dict.get(k)
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == DateLimit._tag_elapsed_time:
                    self.elapsed_time = v
                elif a == _tag_enabled:
                    self.enabled = v
                elif a == DateLimit._tag_time:
                    self.time = v
                elif a == DateLimit._tag_use_date:
                    self.option_use_date = v
                elif a == DateLimit._tag_use_elapsed:
                    self.option_use_elapsed = v
                else:
                    pass

    def _store(self):
        props = {}
        if not isinstance(self.time, PeekTime):
            self.time = PeekTime(self.time)
        props[DateLimit._json_use_date] = self.option_use_date
        props[DateLimit._json_use_elapsed] = self.option_use_elapsed
        props[DateLimit._json_elapsed_time] = self.elapsed_time
        props[DateLimit._json_time] = self.time.iso_time()
        props[_tag_enabled] = self.enabled
        props[_json_classid] = _get_class_id(DateLimit._tag_class_name)
        return props


class FilterLimit(object):
    """The Filter Limit of a Trigger Event Object.
    """

    enabled = False
    """Is the Date Limit enabled?"""

    filters = []
    """A list of filter Ids."""

    mode = 0
    """The filtering mode of the Filters."""

    _filter_ids = []

    # XML Tags
    _json_label = 'filterConfig'
    _json_filters = 'filters'
    _json_mode = 'mode'

    _tag_class_name = 'FilterTriggerEvent'
    _tag_filters = 'filters'
    _tag_mode = 'mode'

    _filter_limit_prop_dict = {
        _json_classid: _tag_classid,
        _tag_enabled: _tag_enabled,
        _json_filters: _tag_filters,
        _json_mode: _tag_mode
    }

    def __init__(self, criteria=None, engine=None):
        self.enabled = FilterLimit.enabled
        self.filters = []
        self.mode = FilterLimit.mode
        self._filter_ids = []
        self._load(criteria, engine)

    def _load(self, props, engine):
        """Load the Date Limit from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = FilterLimit._filter_limit_prop_dict.get(k)
            if a == _tag_classid:
                self._class_id = OmniId(v)
            elif a == _tag_enabled:
                self.enabled = v
            elif a == FilterLimit._tag_filters:
                if isinstance(v, list):
                    for f in v:
                        self.filters.append(OmniId(f))
            elif a == FilterLimit._tag_mode:
                self.mode = v
            else:
                pass

    def _store(self, engine):
        props = {}
        props[FilterLimit._json_mode] = self.mode
        props[FilterLimit._json_filters] = [{id.format()} for id in self.filters]
        props[_json_enabled] = self.enabled
        props[_json_classid] = _get_class_id(FilterLimit._tag_class_name)
        return props


class ExpertStatisticsSettings(object):
    """The Expert Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_flows = False
    option_applications = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_flows = 'option_flows'
    _tag_applications = 'option_application'

    _expert_stats_prop_dict = {
        'outputExpertStatistics': _tag_output_statistics,
        'expertFlows': _tag_flows,
        'expertApplications': _tag_applications
    }

    def __init__(self):
        self.option_output_statistics = ExpertStatisticsSettings.option_output_statistics
        self.option_flows = ExpertStatisticsSettings.option_flows
        self.option_applications = ExpertStatisticsSettings.option_applications

    def _load(self, props, engine):
        """Load the Expert Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = ExpertStatisticsSettings._expert_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)


class GraphsStatisticsSettings(object):
    """The Graphs Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_graphs = False

    # Tags
    _tag_output_graphs = 'option_output_graphs'

    _graphs_stats_prop_dict = {
        'outputGraphs': _tag_output_graphs,
    }

    def __init__(self):
        self.option_output_graphs = GraphsStatisticsSettings.option_output_graphs

    def _load(self, props, engine):
        """Load the Graphs Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = GraphsStatisticsSettings._graphs_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)


class NodeStatisticsSettings(object):
    """The Node Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False   # enabled?
    option_output_details = False
    option_output_hierarchy = False
    option_name = False
    option_packets = False
    option_first_time = False
    option_last_time = False
    option_broad_bytes = False
    option_broad_packets = False
    option_multi_bytes = False
    option_multi_packets = False
    option_minimum_size = False
    option_maximum_size = False
    option_type_physical = False
    option_type_ip = False
    option_type_ipv6 = False
    option_type_dec = False
    option_type_apple = False
    option_type_ipx = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_output_details = 'option_output_details'
    _tag_nodeoutput_hierarchy = 'option_output_hierarchy'
    _tag_name = 'option_node_name'
    _tag_packets = 'option_node_packets'
    _tag_first_time = 'option_node_first_time'
    _tag_last_time = 'option_node_last_time'
    _tag_broad_bytes = 'option_node_broad_bytes'
    _tag_broad_packets = 'option_node_broad_packets'
    _tag_multi_byte = 'option_node_multi_bytes'
    _tag_multi_packet = 'option_node_multi_packets'
    _tag_minimum_size = 'option_node_minimum_size'
    _tag_maximum_size = 'option_node_maximum_size'
    _tag_type_physical = 'option_node_type_physical'
    _tag_type_ip = 'option_node_type_ip'
    _tag_type_ipv6 = 'option_node_type_ipv6'
    _tag_type_dec = 'option_node_type_dec'
    _tag_type_apple = 'option_node_type_apple'
    _tag_type_ipx = 'option_node_type_ipx'

    _node_stats_prop_dict = {
        'outputNodeStatistics': _tag_output_statistics,
        'outputNodeDetails': _tag_output_details,
        'outputNodeHierarchy': _tag_output_details,
        'nodeName': _tag_name,
        'nodePackets': _tag_packets,
        'nodeFirstTime': _tag_first_time,
        'nodeLastTime': _tag_last_time,
        'nodeBroadBytes': _tag_broad_bytes,
        'nodeBroadPackets': _tag_broad_packets,
        'nodeMultiBytes': _tag_multi_byte,
        'nodeMultiPackets': _tag_multi_packet,
        'nodeMinSize': _tag_minimum_size,
        'nodeMaxSize': _tag_maximum_size,
        'nodeTypePhysical': _tag_type_physical,
        'nodeTypeIP': _tag_type_ip,
        'nodeTypeIPv6': _tag_type_ipv6,
        'nodeTypeDEC': _tag_type_dec,
        'nodeTypeApple': _tag_type_apple,
        'nodeTypeIPX': _tag_type_ipx
    }

    def __init__(self):
        self.option_output_statistics = NodeStatisticsSettings.option_output_statistics
        self.option_output_details = NodeStatisticsSettings.option_output_details
        self.option_output_hierarchy = NodeStatisticsSettings.option_output_hierarchy
        self.option_name = NodeStatisticsSettings.option_name
        self.option_packets = NodeStatisticsSettings.option_packets
        self.option_first_time = NodeStatisticsSettings.option_first_time
        self.option_last_time = NodeStatisticsSettings.option_last_time
        self.option_broad_bytes = NodeStatisticsSettings.option_broad_bytes
        self.option_broad_packets = NodeStatisticsSettings.option_broad_packets
        self.option_multi_bytes = NodeStatisticsSettings.option_multi_bytes
        self.option_multi_packets = NodeStatisticsSettings.option_multi_packets
        self.option_minimum_size = NodeStatisticsSettings.option_minimum_size
        self.option_maximum_size = NodeStatisticsSettings.option_maximum_size
        self.option_type_physical = NodeStatisticsSettings.option_type_physical
        self.option_type_ip = NodeStatisticsSettings.option_type_ip
        self.option_type_ipv6 = NodeStatisticsSettings.option_type_ipv6
        self.option_type_dec = NodeStatisticsSettings.option_type_dec
        self.option_type_apple = NodeStatisticsSettings.option_type_apple
        self.option_type_ipx = NodeStatisticsSettings.option_type_ipx

    def _load(self, props, engine):
        """Load the Node Statics Settings from a Dictionairy.
        """

        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = NodeStatisticsSettings._node_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)
                # if a == NodeStatisticsSettings._tag_output_statistics:
                #     self.option_output_statistics = v
                # elif a == NodeStatisticsSettings.option_output_details:
                #     self.option_output_details = v
                # elif a == NodeStatisticsSettings.option_output_hierarchy:
                #     self.option_output_hierarchy = v
                # elif a == NodeStatisticsSettings.option_name:
                #     self.option_name = v
                # elif a == NodeStatisticsSettings.option_packets:
                #     self.option_packets = v
                # elif a == NodeStatisticsSettings.option_first_time:
                #     self.option_first_time = v
                # elif a == NodeStatisticsSettings.option_last_time:
                #     self.option_last_time = v
                # elif a == NodeStatisticsSettings.option_broad_bytes:
                #     self.option_broad_bytes = v
                # elif a == NodeStatisticsSettings.option_broad_packets:
                #     self.option_broad_packets = v
                # elif a == NodeStatisticsSettings.option_multi_bytes:
                #     self.option_multi_bytes = v
                # elif a == NodeStatisticsSettings.option_multi_packets:
                #     self.option_multi_packets = v
                # elif a == NodeStatisticsSettings.option_minimum_size:
                #     self.option_minimum_size = v
                # elif a == NodeStatisticsSettings.option_maximum_size:
                #     self.option_maximum_size = v
                # elif a == NodeStatisticsSettings.option_type_physical:
                #     self.option_type_physical = v
                # elif a == NodeStatisticsSettings.option_type_ip:
                #     self.option_type_ip = v
                # elif a == NodeStatisticsSettings.option_type_ipv6:
                #     self.option_type_ipv6 = v
                # elif a == NodeStatisticsSettings.option_type_dec:
                #     self.option_type_dec = v
                # elif a == NodeStatisticsSettings.option_type_apple:
                #     self.option_type_apple = v
                # elif a == NodeStatisticsSettings.option_type_ipx:
                #     self.option_type_ipx = v


class ProtocolStatisticsSettings(object):
    """The Protocal Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_packets = False
    option_path = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_packets = 'option_packets'
    _tag_path = 'option_path'

    _protocol_stats_prop_dict = {
        'outputProtocolStatistics': _tag_output_statistics,
        'protocolPackets': _tag_packets,
        'protocolPath': _tag_path
    }

    def __init__(self):
        self.option_output_statistics = ProtocolStatisticsSettings.option_output_statistics
        self.option_packets = ProtocolStatisticsSettings.option_packets
        self.option_path = ProtocolStatisticsSettings.option_path

    def _load(self, props, engine):
        """Load the Summary Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = ProtocolStatisticsSettings._protocol_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)


class SummaryStatisticsSettings(object):
    """The Summary Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_percent_packets = False
    option_percent_bytes = False
    option_packets_per_second = False
    option_bytes_per_second = False
    option_snapshots = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_percent_packets = 'option_percent_packets'
    _tag_percent_bytes = 'option_percent_bytes'
    _tag_packets_per_second = 'option_packets_per_second'
    _tag_bytes_per_second = 'option_bytes_per_second'
    _tag_snapshots = 'option_snapshots'

    _summary_stats_prop_dict = {
        'sumPackets': _tag_output_statistics,
        'sumPercentPackets': _tag_percent_packets,
        'sumPercentBytes': _tag_percent_bytes,
        'sumPacketsPerSecond': _tag_packets_per_second,
        'sumBytesPerSecond': _tag_bytes_per_second,
        'outputSnapshots': _tag_snapshots
    }

    def __init__(self):
        self.option_output_statistics = SummaryStatisticsSettings.option_output_statistics
        self.option_percent_packets = SummaryStatisticsSettings.option_percent_packets
        self.option_percent_bytes = SummaryStatisticsSettings.option_percent_bytes
        self.option_packets_per_second = SummaryStatisticsSettings.option_packets_per_second
        self.option_bytes_per_second = SummaryStatisticsSettings.option_bytes_per_second
        self.option_snapshots = SummaryStatisticsSettings.option_snapshots

    def _load(self, props, engine):
        """Load the Summary Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = SummaryStatisticsSettings._summary_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)


class WirelessChannelStatisticsSettings(object):
    """The Wireless Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_frequency = False
    option_band = False
    option_data_packets = False
    option_data_bytes = False
    option_management_packets = False
    option_management_bytes = False
    option_control_packets = False
    option_control_bytes = False
    option_local_packets = False
    option_local_bytes = False
    option_from_ds_packets = False
    option_from_ds_bytes = False
    option_to_ds_packets = False
    option_to_ds_bytes = False
    option_ds_to_ds_packets = False
    option_ds_to_ds_bytes = False
    option_retry_packets = False
    option_retry_bytes = False
    option_protected_packets = False
    option_protected_bytes = False
    option_order_packets = False
    option_order_bytes = False
    option_crc_packets = False
    option_icv_error_packets = False
    option_signal_minimum = False
    option_signal_maximum = False
    option_signal_current = False
    option_signal_average = False
    option_signal_dbm_minimum = False
    option_signal_dbm_maximum = False
    option_signal_dbm_current = False
    option_signal_dbm_average = False
    option_noise_minimum = False
    option_noise_maximum = False
    option_noise_current = False
    option_noise_average = False
    option_noise_dbm_minimum = False
    option_noise_dbm_maximum = False
    option_noise_dbm_current = False
    option_noise_dbm_average = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_frequency = 'option_frequency'
    _tag_band = 'option_band'
    _tag_data_packets = 'option_data_packets'
    _tag_data_bytes = 'option_data_bytes'
    _tag_management_packets = 'option_management_packets'
    _tag_management_bytes = 'option_management_bytes'
    _tag_control_packets = 'option_control_packets'
    _tag_control_bytes = 'option_control_bytes'
    _tag_local_packets = 'option_local_packets'
    _tag_local_bytes = 'option_local_bytes'
    _tag_from_ds_packets = 'option_from_ds_packets'
    _tag_from_ds_bytes = 'option_from_ds_bytes'
    _tag_to_ds_packets = 'option_to_ds_packets'
    _tag_to_ds_bytes = 'option_to_ds_bytes'
    _tag_ds_to_ds_packets = 'option_ds_to_ds_packets'
    _tag_ds_to_ds_bytes = 'option_ds_to_ds_bytes'
    _tag_retry_packets = 'option_retry_packets'
    _tag_retry_bytes = 'option_retry_bytes'
    _tag_protected_packets = 'option_protected_packets'
    _tag_protected_bytes = 'option_protected_bytes'
    _tag_order_packets = 'option_order_packets'
    _tag_order_bytes = 'option_order_bytes'
    _tag_crc_packets = 'option_crc_packets'
    _tag_icv_error_packets = 'option_icv_error_packets'
    _tag_signal_minimum = 'option_signal_minimum'
    _tag_signal_maximum = 'option_signal_maximum'
    _tag_signal_current = 'option_signal_current'
    _tag_signal_average = 'option_signal_average'
    _tag_signal_dbm_minimum = 'option_signal_dbm_minimum'
    _tag_signal_dbm_maximum = 'option_signal_dbm_maximum'
    _tag_signal_dbm_current = 'option_signal_dbm_current'
    _tag_signal_dbm_average = 'option_signal_dbm_average'
    _tag_noise_minimum = 'option_noise_minimum'
    _tag_noise_maximum = 'option_noise_maximum'
    _tag_noise_current = 'option_noise_current'
    _tag_noise_average = 'option_noise_average'
    _tag_noise_dbm_minimum = 'option_noise_dbm_minimum'
    _tag_noise_dbm_maximum = 'option_noise_dbm_maximum'
    _tag_noise_dbm_current = 'option_noise_dbm_current'
    _tag_noise_dbm_average = 'option_noise_dbm_average'

    _wireless_stats_prop_dict = {
        'outputWirelessChannelsStatistics': _tag_output_statistics,
        'wirelessChannelFrequency': _tag_frequency,
        'wirelessChannelBand': _tag_band,
        'wirelessChannelDataPackets': _tag_data_packets,
        'wirelessChannelDataBytes': _tag_data_bytes,
        'wirelessChannelManagementPacets': _tag_management_packets,
        'wirelessChannelManagementBytes': _tag_management_bytes,
        'wirelessChannelControlPackets': _tag_control_packets,
        'wirelessChannelControlBytes': _tag_control_bytes,
        'wirelessChannelLocalPackets': _tag_local_packets,
        'wirelessChannelLocalBytes': _tag_local_bytes,
        'wirelessChannelFromDSPackets': _tag_from_ds_packets,
        'wirelessChannelFromDSBytes': _tag_from_ds_bytes,
        'wirelessChannelToDSPackets': _tag_to_ds_packets,
        'wirelessChannelToDSBytes': _tag_to_ds_bytes,
        'wirelessChannelDS2DSPackets': _tag_ds_to_ds_packets,
        'wirelessChannelDS2DSBytes': _tag_ds_to_ds_bytes,
        'wirelessChannelRetryPackets': _tag_retry_packets,
        'wirelessChannelRetryBytes': _tag_retry_bytes,
        'wirelessChannelProtectedPacket': _tag_protected_packets,
        'wirelessChannelProtectedBytes': _tag_protected_bytes,
        'wirelessChannelOrderPackets': _tag_order_packets,
        'wirelessChannelOrderBytes': _tag_order_bytes,
        'wirelessChannelCRCPackets': _tag_crc_packets,
        'wirelessChannelICVErrorPacket': _tag_icv_error_packets,
        'wirelessChannelSignalMin': _tag_signal_minimum,
        'wirelessChannelSignalMax': _tag_signal_maximum,
        'wirelessChannelSignalCurrent': _tag_signal_current,
        'wirelessChannelSignalAverage': _tag_signal_average,
        'wirelessChannelSignaldBmMin': _tag_signal_dbm_minimum,
        'wirelessChannelSignaldBmMax': _tag_signal_dbm_maximum,
        'wirelessChannelSignaldBmCurrent': _tag_signal_dbm_current,
        'wirelessChannelSignaldBmAverage': _tag_signal_dbm_average,
        'wirelessChannelNoiseMin': _tag_noise_minimum,
        'wirelessChannelNoiseMax': _tag_noise_maximum,
        'wirelessChannelNoiseCurrent': _tag_noise_current,
        'wirelessChannelNoiseAverage': _tag_noise_average,
        'wirelessChannelNoisedBmMin': _tag_noise_dbm_minimum,
        'wirelessChannelNoisedBmMax': _tag_noise_dbm_maximum,
        'wirelessChannelNoisedBmCurrent': _tag_noise_dbm_current,
        'wirelessChannelNoisedBmAverage': _tag_noise_dbm_average
    }

    def __init__(self):
        self.option_output_statistics = WirelessChannelStatisticsSettings.option_output_statistics
        self.option_Frequency = WirelessChannelStatisticsSettings._tag_Frequency
        self.option_Band = WirelessChannelStatisticsSettings._tag_Band
        self.option_DataPackets = WirelessChannelStatisticsSettings._tag_DataPackets
        self.option_DataBytes = WirelessChannelStatisticsSettings._tag_DataBytes
        self.option_ManagementPacket = WirelessChannelStatisticsSettings._tag_ManagementPacket
        self.option_ManagementBytes = WirelessChannelStatisticsSettings._tag_ManagementBytes
        self.option_ControlPackets = WirelessChannelStatisticsSettings._tag_ControlPackets
        self.option_ControlBytes = WirelessChannelStatisticsSettings._tag_ControlBytes
        self.option_LocalPackets = WirelessChannelStatisticsSettings._tag_LocalPackets
        self.option_LocalBytes = WirelessChannelStatisticsSettings._tag_LocalBytes
        self.option_FromDSPackets = WirelessChannelStatisticsSettings._tag_FromDSPackets
        self.option_FromDSBytes = WirelessChannelStatisticsSettings._tag_FromDSBytes
        self.option_ToDSPackets = WirelessChannelStatisticsSettings._tag_ToDSPackets
        self.option_ToDSBytes = WirelessChannelStatisticsSettings._tag_ToDSBytes
        self.option_DS2DSPackets = WirelessChannelStatisticsSettings._tag_DS2DSPackets
        self.option_DS2DSBytes = WirelessChannelStatisticsSettings._tag_DS2DSBytes
        self.option_RetryPackets = WirelessChannelStatisticsSettings._tag_RetryPackets
        self.option_RetryBytes = WirelessChannelStatisticsSettings._tag_RetryBytes
        self.option_ProtectedPackets = WirelessChannelStatisticsSettings._tag_ProtectedPackets
        self.option_ProtectedBytes = WirelessChannelStatisticsSettings._tag_ProtectedBytes
        self.option_OrderPackets = WirelessChannelStatisticsSettings._tag_OrderPackets
        self.option_OrderBytes = WirelessChannelStatisticsSettings._tag_OrderBytes
        self.option_CRCPackets = WirelessChannelStatisticsSettings._tag_CRCPackets
        self.option_ICVErrorPackets = WirelessChannelStatisticsSettings._tag_ICVErrorPackets
        self.option_SignalMin = WirelessChannelStatisticsSettings._tag_SignalMin
        self.option_SignalMax = WirelessChannelStatisticsSettings._tag_SignalMax
        self.option_SignalCurrent = WirelessChannelStatisticsSettings._tag_SignalCurrent
        self.option_SignalAverage = WirelessChannelStatisticsSettings._tag_SignalAverage
        self.option_SignaldBmMin = WirelessChannelStatisticsSettings._tag_SignaldBmMin
        self.option_SignaldBmMax = WirelessChannelStatisticsSettings._tag_SignaldBmMax
        self.option_SignaldBmCurrent = WirelessChannelStatisticsSettings._tag_SignaldBmCurrent
        self.option_SignaldBmAverage = WirelessChannelStatisticsSettings._tag_SignaldBmAverage
        self.option_NoiseMin = WirelessChannelStatisticsSettings._tag_NoiseMin
        self.option_NoiseMax = WirelessChannelStatisticsSettings._tag_NoiseMax
        self.option_NoiseCurrent = WirelessChannelStatisticsSettings._tag_NoiseCurrent
        self.option_NoiseAverage = WirelessChannelStatisticsSettings._tag_NoiseAverage
        self.option_NoisedBmMin = WirelessChannelStatisticsSettings._tag_NoisedBmMin
        self.option_NoisedBmMax = WirelessChannelStatisticsSettings._tag_NoisedBmMax
        self.option_NoisedBmCurrent = WirelessChannelStatisticsSettings._tag_NoisedBmCurrent
        self.option_NoisedBmAverage = WirelessChannelStatisticsSettings._tag_NoisedBmAverage

    def _load(self, props, engine):
        """Load the Wireless Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = WirelessChannelStatisticsSettings._wireless_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                self.setattr(self, a, v)


class WirelessDataRatesStatisticsSettings(object):
    """The Wireless Data Rates Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_packets = False
    option_bytes = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_packets = 'option_packets'
    _tag_bytes = 'option_bytes'

    _wireless_data_rates_stats_prop_dict = {
        'outputDataRates': _tag_output_statistics,
        'dataRatesPackets': _tag_packets,
        'dataRatesBytes': _tag_bytes
    }

    def __init__(self):
        self.option_output_statistics = (
            WirelessDataRatesStatisticsSettings.option_output_statistics)
        self.option_packets = WirelessDataRatesStatisticsSettings.option_packets
        self.option_bytes = WirelessDataRatesStatisticsSettings.option_bytes

    def _load(self, props, engine):
        """Load the  Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = WirelessDataRatesStatisticsSettings._wireless_data_rates_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)


class WLANStatisticsSettings(object):
    """The WLAN Statistics Settings of an
    StatisticsOutputPreferencesSettings Object.
    """

    option_output_statistics = False
    option_name = False
    option_type = False
    option_first_time_sent = False
    option_last_time_sent = False
    option_first_time_received = False
    option_last_time_received = False
    option_packets_sent = False
    option_packets_received = False
    option_broadcast_packets = False
    option_broadcast_bytes = False
    option_multicast_packets = False
    option_multicast_bytes = False
    option_minimum_size_sent = False
    option_maximum_size_sent = False
    option_average_size_sent = False
    option_maximum_size_received = False
    option_minimum_size_received = False
    option_average_size_received = False
    option_retry_packets = False
    option_beacon_packets = False
    option_wep_packets = False
    option_icv_error_packets = False
    option_essid = False
    option_channel = False
    option_wep_key = False
    option_signal_minimum = False
    option_signal_maximum = False
    option_signal_current = False
    option_signal_minimum_dbm = False
    option_signal_maximum_dbm = False
    option_signal_current_dbm = False
    option_noise_minimum = False
    option_noise_maximum = False
    option_noise_current = False
    option_noise_minimum_dbm = False
    option_noise_maximum_dbm = False
    option_noise_current_dbm = False
    option_duration = False
    option_encryption = False
    option_authentication = False
    option_privacy = False
    option_beacon_essid = False
    option_associations = False
    option_trust = False

    # Tags
    _tag_output_statistics = 'option_output_statistics'
    _tag_name = 'option_name'
    _tag_type = 'option_type'
    _tag_first_time_sent = 'option_first_time_sent'
    _tag_last_time_sent = 'option_last_time_sent'
    _tag_first_time_received = 'option_first_time_received'
    _tag_last_time_received = 'option_last_time_received'
    _tag_packets_sent = 'option_packets_sent'
    _tag_packets_received = 'option_packets_received'
    _tag_broadcast_packets = 'option_broadcast_packets'
    _tag_broadcast_bytes = 'option_broadcast_bytes'
    _tag_multicast_packets = 'option_multicast_packets'
    _tag_multicast_bytes = 'option_multicast_bytes'
    _tag_minimum_size_sent = 'option_minimum_size_sent'
    _tag_maximum_size_sent = 'option_maximum_size_sent'
    _tag_average_size_sent = 'option_average_size_sent'
    _tag_maximum_size_received = 'option_maximum_size_received'
    _tag_minimum_size_received = 'option_minimum_size_received'
    _tag_average_size_received = 'option_average_size_received'
    _tag_retry_packets = 'option_retry_packets'
    _tag_beacon_packets = 'option_beacon_packets'
    _tag_wep_packets = 'option_wep_packets'
    _tag_icv_error_packets = 'option_icv_error_packets'
    _tag_essid = 'option_essid'
    _tag_channel = 'option_channel'
    _tag_wep_key = 'option_wep_key'
    _tag_signal_minimum = 'option_signal_minimum'
    _tag_signal_maximum = 'option_signal_maximum'
    _tag_signal_current = 'option_signal_current'
    _tag_signal_minimum_dbm = 'option_signal_minimum_dbm'
    _tag_signal_maximum_dbm = 'option_signal_maximum_dbm'
    _tag_signal_current_dbm = 'option_signal_current_dbm'
    _tag_noise_minimum = 'option_noise_minimum'
    _tag_noise_maximum = 'option_noise_maximum'
    _tag_noise_current = 'option_noise_current'
    _tag_noise_minimum_dbm = 'option_noise_minimum_dbm'
    _tag_noise_maximum_dbm = 'option_noise_maximum_dbm'
    _tag_noise_current_dbm = 'option_noise_current_dbm'
    _tag_duration = 'option_duration'
    _tag_encryption = 'option_encryption'
    _tag_authentication = 'option_authentication'
    _tag_privacy = 'option_privacy'
    _tag_beacon_essid = 'option_beacon_essid'
    _tag_associations = 'option_associations'
    _tag_trust = 'option_trust'

    _wlan_stats_prop_dict = {
        'outputWLANStatistics': _tag_output_statistics,
        'wlanName': _tag_name,
        'wlanType': _tag_type,
        'wlanFirstTimeSent': _tag_first_time_sent,
        'wlanLastTimeSent': _tag_last_time_sent,
        'wlanFirstTimeReceived': _tag_first_time_received,
        'wlanLastTimeReceived': _tag_first_time_received,
        'wlanPacketsSent': _tag_packets_sent,
        'wlanPacketsReceived': _tag_packets_received,
        'wlanBroadcastPackets': _tag_broadcast_bytes,
        'wlanBroadcastBytes': _tag_broadcast_packets,
        'wlanMulticastPackets': _tag_multicast_packets,
        'wlanMulticastBytes': _tag_multicast_bytes,
        'wlanMinSizeSent': _tag_minimum_size_sent,
        'wlanMaxSizeSent': _tag_maximum_size_sent,
        'wlanAverageSizeSent': _tag_average_size_sent,
        'wlanMaxSizeReceived': _tag_maximum_size_received,
        'wlanMinSizeReceived': _tag_maximum_size_received,
        'wlanAverageSizeReceived': _tag_average_size_received,
        'wlanRetryPackets': _tag_retry_packets,
        'wlanBeaconPackets': _tag_beacon_packets,
        'wlanWEPPackets': _tag_wep_packets,
        'wlanICVErrorPackets': _tag_icv_error_packets,
        'wlanESSID': _tag_essid,
        'wlanChannel': _tag_channel,
        'wlanWEPKey': _tag_wep_key,
        'wlanSignalMin': _tag_signal_minimum,
        'wlanSignalMax': _tag_signal_maximum,
        'wlanSignalCurrent': _tag_signal_current,
        'wlanSignalMindBm': _tag_signal_minimum_dbm,
        'wlanSignalMaxdBm': _tag_signal_maximum_dbm,
        'wlanSignalCurrentdBm': _tag_signal_current_dbm,
        'wlanNoiseMin': _tag_noise_maximum,
        'wlanNoiseMax': _tag_noise_maximum,
        'wlanNoiseCurrent': _tag_noise_current,
        'wlanNoiseMindBm': _tag_noise_minimum_dbm,
        'wlanNoiseMaxdBm': _tag_noise_maximum_dbm,
        'wlanNoiseCurrentdBm': _tag_noise_current_dbm,
        'wlanDuration': _tag_duration,
        'wlanEncryption': _tag_encryption,
        'wlanAuthentication': _tag_authentication,
        'wlanPrivacy': _tag_privacy,
        'wlanBeaconESSID': _tag_beacon_essid,
        'wlanAssociations': _tag_associations,
        'wlanTrust': _tag_trust
    }

    def __init__(self):
        self.option_output_statistics = WLANStatisticsSettings.option_output_statistics
        self.option_name = WLANStatisticsSettings.option_name
        self.option_type = WLANStatisticsSettings.option_type
        self.option_first_time_sent = WLANStatisticsSettings.option_first_time_sent
        self.option_last_time_sent = WLANStatisticsSettings.option_last_time_sent
        self.option_first_time_received = WLANStatisticsSettings.option_first_time_received
        self.option_last_time_received = WLANStatisticsSettings.option_last_time_received
        self.option_packets_sent = WLANStatisticsSettings.option_packets_sent
        self.option_packets_received = WLANStatisticsSettings.option_packets_received
        self.option_broadcast_packets = WLANStatisticsSettings.option_broadcast_packets
        self.option_broadcast_bytes = WLANStatisticsSettings.option_broadcast_bytes
        self.option_multicast_packets = WLANStatisticsSettings.option_multicast_packets
        self.option_multicast_bytes = WLANStatisticsSettings.option_multicast_bytes
        self.option_minimum_size_sent = WLANStatisticsSettings.option_minimum_size_sent
        self.option_maximum_size_sent = WLANStatisticsSettings.option_maximum_size_sent
        self.option_average_size_sent = WLANStatisticsSettings.option_average_size_sent
        self.option_maximum_size_received = WLANStatisticsSettings.option_maximum_size_received
        self.option_minimum_size_received = WLANStatisticsSettings.option_minimum_size_received
        self.option_average_size_received = WLANStatisticsSettings.option_average_size_received
        self.option_retry_packets = WLANStatisticsSettings.option_retry_packets
        self.option_beacon_packets = WLANStatisticsSettings.option_beacon_packets
        self.option_wep_packets = WLANStatisticsSettings.option_wep_packets
        self.option_icv_error_packets = WLANStatisticsSettings.option_icv_error_packets
        self.option_essid = WLANStatisticsSettings.option_essid
        self.option_channel = WLANStatisticsSettings.option_channel
        self.option_wep_key = WLANStatisticsSettings.option_wep_key
        self.option_signal_minimum = WLANStatisticsSettings.option_signal_minimum
        self.option_signal_maximum = WLANStatisticsSettings.option_signal_maximum
        self.option_signal_current = WLANStatisticsSettings.option_signal_current
        self.option_signal_minimum_dbm = WLANStatisticsSettings.option_signal_minimum_dbm
        self.option_signal_maximum_dbm = WLANStatisticsSettings.option_signal_maximum_dbm
        self.option_signal_current_dbm = WLANStatisticsSettings.option_signal_current_dbm
        self.option_noise_minimum = WLANStatisticsSettings.option_noise_minimum
        self.option_noise_maximum = WLANStatisticsSettings.option_noise_maximum
        self.option_noise_current = WLANStatisticsSettings.option_noise_current
        self.option_noise_minimum_dbm = WLANStatisticsSettings.option_noise_minimum_dbm
        self.option_noise_maximum_dbm = WLANStatisticsSettings.option_noise_maximum_dbm
        self.option_noise_current_dbm = WLANStatisticsSettings.option_noise_current_dbm
        self.option_duration = WLANStatisticsSettings.option_duration
        self.option_encryption = WLANStatisticsSettings.option_encryption
        self.option_authentication = WLANStatisticsSettings.option_authentication
        self.option_privacy = WLANStatisticsSettings.option_privacy
        self.option_beacon_essid = WLANStatisticsSettings.option_beacon_essid
        self.option_associations = WLANStatisticsSettings.option_associations
        self.option_trust = WLANStatisticsSettings.option_trust

    def _load(self, props, engine):
        """Load the WLAN Statics Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = WLANStatisticsSettings._wlan_stats_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                setattr(self, a, v)


class AdapterSettings(object):
    """The Adapter Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    device_name = None
    """The device name of the adapter: Broadcom, Intel..."""

    limit = 0
    """The number of times to replay a file adapter: 0 for infininte."""

    mode = 0
    """The timestamping mode of a file adapter."""

    name = None
    """The name (or description) of the adapter."""

    speed = 1.0
    """The replay speed multiplier of a file adapter."""

    adapter_type = AdapterType.NIC
    """The type of adapter. One of the ADAPTER TYPE constants."""

    # Tags
    _json_label = 'adapterSettings'
    _json_class_name = _tag_prop_bag
    _json_enumerator = 'enumerator'
    _json_name = _tag_name
    _json_type = _tag_type
    _json_limit = 'replayLimit'
    _json_mode = 'replayTimeStampMode'
    _json_speed = 'replaySpeed'

    _tag_adapter_type = 'adapter_type'
    _tag_as_type = "Type"
    _tag_device_name = 'device_name'
    _tag_enumerator = 'enumerator'
    _tag_label = 'AdapterSettings'
    _tag_limit = 'limit'
    _tag_mode = 'mode'
    _tag_root_name = _tag_props
    _tag_speed = 'speed'

    _adapter_prop_dict = {
        _json_classid: _tag_classid,
        _json_name: _tag_device_name,
        _json_type: _tag_adapter_type,
        _json_enumerator: _tag_enumerator,
        _json_limit: _tag_limit,
        _json_mode: _tag_mode,
        _json_speed: _tag_speed
    }

    def __init__(self):
        self.device_name = AdapterSettings.device_name
        self.limit = AdapterSettings.limit
        self.mode = AdapterSettings.mode
        self.name = AdapterSettings.name
        self.speed = AdapterSettings.speed
        self.adapter_type = AdapterSettings.adapter_type

    def __str__(self):
        return f'AdapterSettings: {self.name}'

    @property
    def description(self):
        """Return the name as the description of the adapter."""
        return self.name

    def _load(self, props):
        """Load the Adapter Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = AdapterSettings._adapter_prop_dict.get(k)
            if a is None or not hasattr(self, a):
                continue
            if a == _json_classid:
                self._class_id = OmniId(v)
            elif a == AdapterSettings._tag_device_name:
                self.device_name = v
            elif a == AdapterSettings._tag_limit:
                self.limit = v
            elif a == AdapterSettings._tag_mode:
                self.mode = int(v)
            elif a == _tag_name:
                self.name = v
            elif a == AdapterSettings._tag_speed:
                self.speed = int(v)
            elif a == AdapterSettings._tag_adapter_type:
                self.adapter_type = int(v)
        # if self.adapter_type == AdapterType.FILE:
        #     _find_property(props, AdapterSettings._tag_limit)
        #     _find_property(props, AdapterSettings._tag_speed)
        #     _find_property(props, AdapterSettings._tag_mode)
        # prop = _find_property(props, AdapterSettings._tag_as_name)
        # if prop is not None:
        #     self.name = prop.text

    def _load_xml(self, obj):
        """Load the Adapter Settings from an ETree SubElement."""
        props = obj.find(AdapterSettings._tag_root_name)
        prop_type = _find_property(props, AdapterSettings._tag_as_type)
        if prop_type is not None:
            self.adapter_type = int(prop_type.text)
        #     if self.adapter_type == config.ADAPTER_TYPE_FILE:
        #         _find_property(props, AdapterSettings._tag_limit)
        #         _find_property(props, AdapterSettings._tag_speed)
        #         _find_property(props, AdapterSettings._tag_mode)
        # prop = _find_property(props, AdapterSettings._tag_as_name)
        # if prop is not None:
        #     self.name = prop.text

    def _store(self, props, engine):
        """Store the Adapter Settings into a dictionary."""
        if not isinstance(props, dict):
            return
        _props = {}
        if engine is not None:
            if self.adapter_type == AdapterType.FILE:
                _props[AdapterSettings._json_name] = self.name
                _props[AdapterSettings._json_limit] = self.limit
                _props[AdapterSettings._json_mode] = self.mode
                _props[AdapterSettings._json_speed] = self.speed
                _props[AdapterSettings._json_adapter_type] = self.adapter_type
            else:
                adapter = None
                if self.name is not None:
                    adapter = engine.find_adapter(self.name)
                elif self.device_name is not None:
                    adapter = engine.find_adapter(self.device_name, 'device_name')

                if adapter is None:
                    raise OmniError('Adapter not found')

                _props[AdapterSettings._json_enumerator] = adapter.adapter_id
                _props[AdapterSettings._json_name] = adapter.name
                _props[AdapterSettings._json_type] = adapter.adapter_type
        elif self.name is not None:
            _props[AdapterSettings._json_name] = self.name
        _props[_json_classid] = _get_class_id(AdapterSettings._json_class_name)
        props[AdapterSettings._json_label] = _props


class AlarmSettings(object):
    """The Alarm Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    alarms = []
    """A list of Alarms.
    :class:`Alarm <omniscript.alarm.Alarm>` or
    :class:`OmniId <omniscript.omniid.OmniId>`
    """

    # Tags
    _json_label = 'alarmConfig'
    _json_class_name = 'AlarmConfig'
    _json_alarms = 'alarms'

    _tag_alarms = 'alarms'
    _tag_label = 'AlarmConfig'

    _tag_xml_config = "AlarmConfig"
    _tag_xml_alarm = "Alarm"
    _tag_xml_alarms = "Alarms"

    _alarm_prop_dict = {
        _json_classid: _tag_classid,
        _json_alarms: _tag_alarms
    }

    def __init__(self):
        self.alarms = AlarmSettings.alarms

    def _load(self, props, engine=None):
        """Load the Alarm Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = AlarmSettings._alarm_prop_dict.get(k)
            if a is not None and hasattr(self, a):
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == 'alarms':
                    self.alarms = []
                    for id in v:
                        self.alarms.append(OmniId(id))

    def _load_xml(self, obj, engine=None):
        """Load the Alarm from an ETree.SubElement."""
        _config = obj.find(AlarmSettings._tag_xml_config)
        if _config is not None:
            alarm_list = None
            if engine is not None:
                alarm_list = engine.get_alarm_list()
            alarms = _config.find(AlarmSettings._tag_xml_alarms)
            for alarm in alarms.findall(AlarmSettings._tag_xml_alarm):
                id = OmniId(alarm.attrib[_tag_id])
                _alarm = None
                if alarm_list is not None:
                    _alarm = find_alarm(alarm_list, id)
                if _alarm is not None:
                    self.alarms.append(_alarm)
                else:
                    self.alarms.append(id)

    def _store(self, props):
        """Store the Alarms into a JSON props."""
        if not isinstance(props, dict) or len(self.alarms) == 0:
            return
        _props = {}
        _props[AlarmSettings._tag_alarms] = [a.format() for a in self.alarms]
        _props[_json_classid] = _get_class_id(AlarmSettings._json_class_name)
        props[AlarmSettings._json_label] = _props


class AnalysisModules(object):
    """The Analysis Module section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    All the Analysis Modules installed on the engine and listed in
    modules by name and in ids listed by
    :class:`OmniId <omniscript.omniid.OmniId>` will be enabled in the capture.
    """

    modules = []
    """A list of
    :class:`AnalysisModule <omniscript.analysismodule.AnalysisModule>`
    objects.
    """

    option_enable_all = False
    """When True all of the engine's Analysis Modules will be enabled.
    """

    # Tags
    _json_class_name = 'PropertyList'
    _json_config_class_name = 'PluginsConfig'
    _json_config_label = 'pluginsConfig'
    _json_ids = 'ids'
    _json_label = 'pluginsList'

    _tag_ids = 'ids'
    _tag_label = 'PluginsList'
    _tag_options = 'options'
    _tag_plugins = 'plugins'
    _tag_root_name = _tag_props

    _tag_xml_plugin = 'plugin'
    _tag_xml_plugins = 'plugins'

    _analysis_modules_prop_list = {
        _json_classid: _tag_classid,
        _tag_props: _tag_ids
    }

    def __init__(self):
        self.modules = []
        self.option_enable_all = AnalysisModules.option_enable_all

    def _load(self, props, engine=None):
        """Load the Analysis Modules List from a Dictionairy."""
        self.modules = []
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = AnalysisModules._analysis_modules_prop_list.get(k)
            if a is not None and hasattr(self, a):
                if a == AnalysisModules._tag_ids:
                    for m in v:
                        # {'type': 8, 'value': '{9A138D11-5773-4C77-8DBF-16EAC5EFE083}'}
                        if isinstance(m, dict) and ('value' in m):
                            self.modules.append(AnalysisModule(id=m['value']))
        # props = obj.find(AnalysisModules._tag_root_name)
        # if props is not None:
        #     for prop in props.findall(_tag_prop):
        #         if OmniId.is_id(prop.text):
        #             id = OmniId(prop.text)
        #             module_name = None
        #             if module_list:
        #                 module = next((i for i in module_list if getattr(i, 'id') == id), None)
        #                 if module is not None:
        #                     module_name = module.name
        #             if not module_name:
        #                 if id in id_class_names:
        #                     module_name = id_class_names[id]
        #             if module_name:
        #                 if module_name not in self.modules:
        #                     self.modules.append(module_name)
        #                 else:
        #                     self.ids.append(id)
        #         else:
        #             if prop.text not in self.modules:
        #                 self.modules.append(prop.text)

    def _load_xml(self, obj, engine):
        """Load the list of Analysis Modules from an ETree.SubElement."""
        if self.modules is None:
            self.modules = []

        if 'null' in obj.attrib:
            null_enabled = obj.attrib['null']
            if null_enabled:
                return

        """ Build Analysis Module list """
        props = obj.find(AnalysisModules._tag_root_name)
        if props is not None:
            for prop in props.findall(_tag_prop):
                if OmniId.is_id(prop.text):
                    id = OmniId(prop.text)
                    plugin = find_analysis_module(self.modules, id, 'id')
                    if plugin is None:
                        self.modules.append(AnalysisModule(engine, id=id))

    def _load_xml_config(self, obj, engine):
        props = obj.find(AnalysisModules._tag_xml_plugins)
        if props is not None:
            for prop in props.findall(AnalysisModules._tag_xml_plugin):
                prop_id = prop.attrib.get('clsid')
                if prop_id:
                    if OmniId.is_id(prop_id):
                        id = OmniId(prop_id)
                        plugin = find_analysis_module(self.modules, id, 'id')
                        if plugin is None:
                            plugin = AnalysisModule(engine, id=id)
                            self.modules.append(plugin)
                        if plugin is not None:
                            plugin.set_configuration(prop)

    def _store(self, props):
        """Store the Analysis Module list into a JSON props."""
        if not isinstance(props, dict):
            return
        prop_list = [
            {
                _tag_type: 8,
                _tag_value: str(plugin.id)
            } for plugin in self.modules
        ]
        _props = {
            AnalysisModules._tag_root_name: prop_list,
            _json_classid: _get_class_id(AnalysisModules._json_class_name)
        }
        props[AnalysisModules._json_label] = _props

        have_config = [m.configuration is not None for m in self.modules]
        if any(have_config):
            config_list = [
                {
                    _json_classid: str(plugin.id),
                    _tag_name: plugin.name,
                    AnalysisModules._tag_options: plugin.get_configuration()
                } for plugin in self.modules
            ]
            config_props = {
                AnalysisModules._tag_plugins: config_list,
                _json_classid: _get_class_id(AnalysisModules._json_config_class_name)
            }
            props[AnalysisModules._json_config_label] = config_props

    def set_all(self, enable=True):
        """Enable or disable enabeling all of the Analysis Modules on
        the Engine.
        """
        self.option_enable_all = enable


class AnalysisSettings(object):
    """The Analysis Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    node_limit = None
    """The Node Statistics settings."""

    node_protocol_detail_limit = None
    """The Node and Protocol Detail Statistics settings."""

    protocol_limit = None
    """The Protocol Statistics settings."""

    option_alarms = False
    """Is the Alarms option enabled?"""

    option_analysis_modules = False
    """Is the Analysis Module option enabled?"""

    option_application = False
    """Is the Application Statistics option enabled?"""

    option_compass = False
    """Is Compass enabled?"""

    option_country = False
    """Is the Country Statistics option enabled?"""

    option_error = False
    """Is the Error Statistics option enabled?"""

    option_expert = False
    """Is the Expert Analysis option enabled?"""

    option_network = False
    """Is the Network Statistics option enabled?"""

    option_passive_name_resolution = False
    """Is the Passive Name Resolution option enabled?"""

    option_size = False
    """Is the Size Statistics option enabled?"""

    option_summary = False
    """Is the Summary Statistics option enabled?"""

    option_top_talker = False
    """Is the Traffic History Statistics option enabled?
    This option may be unsupported.
    """

    option_traffic_history = False
    """Is the Traffic History Statistics option enabled?"""

    option_voice_video = False
    """Is the Voice and Video Analysis option enabled?"""

    option_web = False
    """Is the Web Analysis option enabled?"""

    option_wireless_channel = False
    """Is the Wireless Channel Statistics option enabled?"""

    option_wireless_node = False
    """Is the Wireless Node Statistics option enabled?"""

    # Tags
    _json_label = 'performanceConfig'
    _json_class_name = _tag_prop_bag
    _json_alarms = 'alarms'
    _json_analysis_modules = 'analysisModules'
    _json_application = 'applicationStatistics'
    _json_compass = 'compass'
    _json_country = 'countryStatistics'
    _json_node_protocol = 'nodeProtocolDetailStatistics'
    _json_error = 'errorStatistics'
    _json_expert = 'expertAnalysis'
    _json_network = 'networkStatistics'
    _json_node = 'nodeStatistics'
    _json_passive = 'passiveNameResolution'
    _json_protocol = 'protocolStatistics'
    _json_size = 'sizeStatistics'
    _json_summary = 'summaryStatistics'
    _json_top_talker = 'topTalkerStatistics'
    _json_traffic = 'trafficHistoryStatistics'
    _json_voice_video = 'voiceAndVideoAnalysis'
    _json_web = 'webAnalysis'
    _json_wireless_channel = 'wirelessChannelStatistics'
    _json_wireless_node = 'wirelessNodeStatistics'

    _tag_alarms = 'option_alarms'
    _tag_analysis_modules = 'option_analysis_modules'
    _tag_application = 'option_application'
    _tag_compass = 'option_compass'
    _tag_country = 'option_country'
    _tag_detail_limit = "Node/Protocol Detail Statistics"
    _tag_error = 'option_error'
    _tag_expert = 'option_expert'
    _tag_label = 'PerfConfig'
    _tag_network = 'option_network'
    _tag_node = 'node_limit'
    _tag_node_limit = "Node Statistics"
    _tag_node_protocol = 'node_protocol_detail_limit'
    _tag_passive = 'option_passive_name_resolution'
    _tag_protocol = 'protocol_limit'
    _tag_protocol_limit = "Protocol Statistics"
    _tag_root_name = _tag_props
    _tag_size = 'option_size'
    _tag_summary = 'option_summary'
    _tag_top_talker = 'option_top_talker'
    _tag_traffic = 'option_traffic_history'
    _tag_voice_video = 'option_voice_video'
    _tag_web = 'option_web'
    _tag_wireless_channel = 'option_wireless_channel'
    _tag_wireless_node = 'option_wireless_node'

    _tag_xml_alarms = "Alarms"
    _tag_xml_analysis_modules = "Analysis Modules"
    _tag_xml_application_stats = "Application Statistics"
    _tag_xml_country_stats = "Country Statistics"
    _tag_xml_detail_limit = "Node/Protocol Detail Statistics"
    _tag_xml_error_stats = "Error Statistics"
    _tag_xml_expert = "Expert Analysis"
    _tag_xml_network_stats = "Network Statistics"
    _tag_xml_node_limit = "Node Statistics"
    _tag_xml_protocol_limit = "Protocol Statistics"
    _tag_xml_size_stats = "Size Statistics"
    _tag_xml_summary_stats = "Summary Statistics"
    _tag_xml_top_talker_stats = "Top Talker Statistics"
    _tag_xml_traffic_stats = "Traffic History Statistics"
    _tag_xml_voice_video = "Voice and Video Analysis"

    _analysis_prop_dict = {
        _json_classid: _tag_classid,
        _json_alarms: _tag_alarms,
        _json_analysis_modules: _tag_analysis_modules,
        _json_application: _tag_application,
        _json_compass: _tag_compass,
        _json_country: _tag_country,
        _json_node_protocol: _tag_node_protocol,
        _json_error: _tag_error,
        _json_expert: _tag_expert,
        _json_network: _tag_network,
        _json_node: _tag_node,
        _json_passive: _tag_passive,
        _json_protocol: _tag_protocol,
        _json_size: _tag_size,
        _json_summary: _tag_summary,
        _json_top_talker: _tag_top_talker,
        _json_traffic: _tag_traffic,
        _json_voice_video: _tag_voice_video,
        _json_web: _tag_web,
        _json_wireless_channel: _tag_wireless_channel,
        _json_wireless_node: _tag_wireless_node,
    }

    def __init__(self):
        self._class_id = None
        self.node_limit = StatsLimit(AnalysisSettings._tag_node_limit)
        self.node_protocol_detail_limit = StatsLimit(AnalysisSettings._tag_detail_limit,
                                                     limit=500000)
        self.protocol_limit = StatsLimit(AnalysisSettings._tag_protocol_limit)
        self.option_alarms = AnalysisSettings.option_alarms
        self.option_analysis_modules = AnalysisSettings.option_analysis_modules
        self.option_application = AnalysisSettings.option_application
        self.option_compass = AnalysisSettings.option_compass
        self.option_country = AnalysisSettings.option_country
        self.option_error = AnalysisSettings.option_error
        self.option_expert = AnalysisSettings.option_expert
        self.option_network = AnalysisSettings.option_network
        self.option_passive_name_resolution = AnalysisSettings.option_passive_name_resolution
        self.option_size = AnalysisSettings.option_size
        self.option_summary = AnalysisSettings.option_summary
        self.option_top_talker = AnalysisSettings.option_top_talker
        self.option_traffic_history = AnalysisSettings.option_traffic_history
        self.option_voice_video = AnalysisSettings.option_voice_video
        self.option_web = AnalysisSettings.option_web
        self.option_wireless_channel = AnalysisSettings.option_wireless_channel
        self.option_wireless_node = AnalysisSettings.option_wireless_node

    def _load(self, props, engine=None):
        """Load the Analysis Settings from a Dictionairy."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            a = AnalysisSettings._analysis_prop_dict.get(k)
            if a is None or not hasattr(self, a):
                continue
            if a == _tag_classid:
                self._class_id = OmniId(v)
            # elif a == AnalysisSettings._tag_node_limit:
            #     self.node_limit = StatsLimit(AnalysisSettings._tag_node_limit)
            #     self.node_limit.enabled = v
            # elif a == AnalysisSettings._tag_detail_limit:
            #     self.node_protocol_detail_limit = StatsLimit(AnalysisSettings._tag_detail_limit)
            #     self.node_protocol_detail_limit.enabled = v
            # elif a == AnalysisSettings._tag_protocol_limit:
            #     self.protocol_limit = StatsLimit(AnalysisSettings._tag_protocol_limit)
            #     self.protocol_limit.enabled = v
            elif a == AnalysisSettings._tag_alarms:
                self.option_alarms = v
            elif a == AnalysisSettings._tag_analysis_modules:
                self.option_analysis_modules = v
            elif a == AnalysisSettings._tag_application:
                self.option_application = v
            elif a == AnalysisSettings._tag_compass:
                self.option_compass = v
            elif a == AnalysisSettings._tag_country:
                self.option_country = v
            elif a == AnalysisSettings._tag_error:
                self.option_error = v
            elif a == AnalysisSettings._tag_expert:
                self.option_expert = v
            elif a == AnalysisSettings._tag_network:
                self.option_network = v
            elif a == AnalysisSettings._tag_passive:
                self.option_passive_name_resolution = v
            elif a == AnalysisSettings._tag_size:
                self.option_size = v
            elif a == AnalysisSettings._tag_summary:
                self.option_summary = v
            elif a == AnalysisSettings._tag_top_talker:
                self.option_top_talker = v
            elif a == AnalysisSettings._tag_traffic:
                self.option_traffic_history = v
            elif a == AnalysisSettings._tag_voice_video:
                self.option_voice_video = v
            elif a == AnalysisSettings._tag_web:
                self.option_web = v
            elif a == AnalysisSettings._tag_wireless_channel:
                self.option_wireless_channel = v
            elif a == AnalysisSettings._tag_wireless_node:
                self.option_wireless_node = v

    def _load_xml(self, obj, engine=None):
        """Load the Analysis Settings from an ETree.SubElement."""
        props = obj.find(AnalysisSettings._tag_root_name)
        if props is not None:
            for obj in props.findall(_tag_object):
                objName = obj.attrib[_tag_name]
                if objName == AnalysisSettings._tag_xml_node_limit:
                    self.node_limit.parse(obj)
                elif objName == AnalysisSettings._tag_xml_detail_limit:
                    self.node_protocol_detail_limit.parse(obj)
                elif objName == AnalysisSettings._tag_xml_protocol_limit:
                    self.protocol_limit.parse(obj)
            for prop in props.findall(_tag_prop):
                propName = prop.attrib[_tag_name]
                if propName == AnalysisSettings._tag_xml_alarms:
                    self.option_alarms = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_analysis_modules:
                    self.option_analysis_modules = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_application_stats:
                    self.option_application = _from_prop_boolean(prop.text)
                elif propName == _tag_compass:
                    self.option_compass = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_country_stats:
                    self.option_country = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_error_stats:
                    self.option_error = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_expert:
                    self.option_expert = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_network_stats:
                    self.option_network = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_size_stats:
                    self.option_size = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_summary_stats:
                    self.option_summary = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_top_talker_stats:
                    self.option_top_talker = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_traffic_stats:
                    self.option_traffic = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_voice_video:
                    self.option_voice_video = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_node_limit:
                    self.node_limit = StatsLimit(AnalysisSettings._tag_xml_node_limit)
                    self.node_limit.enabled = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_detail_limit:
                    self.node_protocol_detail_limit = StatsLimit(
                        AnalysisSettings._tag_xml_detail_limit)
                    self.node_protocol_detail_limit.enabled = _from_prop_boolean(prop.text)
                elif propName == AnalysisSettings._tag_xml_protocol_limit:
                    self.protocol_limit = StatsLimit(AnalysisSettings._tag_xml_protocol_limit)
                    self.protocol_limit.enabled = _from_prop_boolean(prop.text)

    def _store(self, props):
        """Store the Analysis Settings into the ETree.SubElement."""
        if not isinstance(props, dict):
            return
        _props = {}
        _props[AnalysisSettings._json_node] = self.node_limit.enabled
        _props[AnalysisSettings._json_protocol] = self.protocol_limit.enabled
        _props[AnalysisSettings._json_node_protocol] = self.protocol_limit.enabled
        _props[AnalysisSettings._json_alarms] = self.option_alarms
        _props[AnalysisSettings._json_analysis_modules] = self.option_analysis_modules
        _props[AnalysisSettings._json_application] = self.option_application
        _props[AnalysisSettings._json_compass] = self.option_compass
        _props[AnalysisSettings._json_country] = self.option_country
        _props[AnalysisSettings._json_passive] = self.option_passive_name_resolution
        _props[AnalysisSettings._json_error] = self.option_error
        _props[AnalysisSettings._json_expert] = self.option_expert
        _props[AnalysisSettings._json_network] = self.option_network
        _props[AnalysisSettings._json_size] = self.option_size
        _props[AnalysisSettings._json_summary] = self.option_summary
        _props[AnalysisSettings._json_top_talker] = self.option_top_talker
        _props[AnalysisSettings._json_traffic] = self.option_traffic_history
        _props[AnalysisSettings._json_voice_video] = self.option_voice_video
        _props[AnalysisSettings._json_web] = self.option_web
        _props[AnalysisSettings._json_wireless_channel] = self.option_wireless_channel
        _props[AnalysisSettings._json_wireless_node] = self.option_wireless_node
#         # If a limit is None or disabled, then set it as a bool property.
#         if self.node_limit is None or not self.node_limit.enabled:
#             _set_property(props, AnalysisSettings._tag_node_limit, 22,
#                           _to_prop_boolean(False))
#         else:
#             props.append(self.node_limit.to_xml())
#         if self.node_protocol_detail_limit is None or not self.node_protocol_detail_limit.enabled:
#             _set_property(props, AnalysisSettings._tag_detail_limit, 22,
#                           _to_prop_boolean(False))
#         else:
#             props.append(self.node_protocol_detail_limit.to_xml())
#         if self.protocol_limit is None or not self.protocol_limit.enabled:
#             _set_property(props, AnalysisSettings._tag_protocol_limit, 22,
#                           _to_prop_boolean(False))
#         else:
#             props.append(self.protocol_limit.to_xml())
        _props[_json_classid] = _get_class_id(AdapterSettings._json_class_name)
        props[AnalysisSettings._json_label] = _props

    def set_all(self, enable=True):
        """Enable or disable all of the Analysis Options."""
        self.node_limit.enabled = enable
        self.node_protocol_detail_limit.enabled = enable
        self.protocol_limit.enabled = enable
        self.option_alarms = enable
        self.option_analysis_modules = enable
        self.option_application = enable
        self.option_compass = enable
        self.option_country = enable
        self.option_error = enable
        self.option_expert = enable
        self.option_network = enable
        self.option_passive_name_resolution = enable
        self.option_size = enable
        self.option_summary = enable
        self.option_top_talker = enable
        self.option_traffic_history = enable
        self.option_voice_video = enable
        self.option_web = enable
        self.option_wireless_channel = enable
        self.option_wireless_node = enable


class FilterSettings(object):
    """The Filter Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    filters = []
    """A list of Filter Names."""

    ids = []
    """A list of :class:`OmniId <omniscript.omniid.OmniId>` of the enabled
    filters.
    """

    mode = FILTER_MODE_ACCEPT_MATCHING_ANY
    """The filtering mode. One of the FILTER MODE constants."""

    # Tags
    _json_label = 'filterConfig'
    _json_class_name = 'FilterConfig'
    _json_filters = 'filters'
    _json_ids = 'ids'
    _json_mode = 'mode'

    _tag_config = "filterconfig"
    _tag_filters = 'filters'
    _tag_ids = 'ids'
    _tag_label = 'FilterConfig'
    _tag_mode = 'mode'

    _filter_prop_dict = {
        _json_classid: _tag_classid,
        _json_filters: _tag_filters,
        _json_ids: _tag_ids,
        _json_mode: _tag_mode
    }

    def __init__(self):
        self.filters = []
        self.ids = []
        self.mode = FilterSettings.mode

    def _load(self, props):
        """Load the Filter Settings from a Dictionairy."""
        self.filters = []
        self._filter_ids = []
        if isinstance(props, dict):
            for k, v in props.items():
                a = FilterSettings._filter_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if a == _tag_classid:
                        self._class_id = OmniId(v)
                    elif a == FilterSettings._tag_filters:
                        if isinstance(v, list):
                            for f in v:
                                self.ids.append(OmniId(f))
                    elif a == FilterSettings._tag_mode:
                        self.mode = int(v)
        # obj.find(FilterSettings._tag_root_name)
        # """ Build filter_list """
        # pass

    def _load_xml(self, obj):
        """Load the Filter Settings from an ETree.SubElement."""
        self.filters = []
        self._filter_ids = []

        if 'null' in obj.attrib:
            null_enabled = obj.attrib['null']
            if null_enabled:
                return

        config = obj.find(FilterSettings._tag_config)
        if config:
            mode = config.attrib.get(FilterSettings._tag_mode)
            self.mode = int(mode) if mode is not None else FilterSettings.mode

        """ Build filter_list """
        pass

    def _store(self, props, engine):
        """Store the Filter Settings into a JSON props."""
        if not isinstance(props, dict):
            return
        if not self.ids:
            fl = engine.get_filter_list()
            for fn in self.filters:
                f = find_filter(fl, fn, 'name')
                if f and f.id and f.id not in self.ids:
                    self.ids.append(f.id)
            if not self.ids:
                return
        _props = {}
        _props[FilterSettings._json_filters] = [
            id.format() for id in self.ids
        ]
        _props[FilterSettings._json_mode] = self.mode
        _props[_json_classid] = _get_class_id(FilterSettings._json_class_name)
        props[FilterSettings._json_label] = _props


class GeneralSettings(object):
    """The General Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    buffer_size = 100 * BYTES_IN_A_MEGABYTE
    """The size of the capture buffer in bytes. Default is 100 megabytes"""

    comment = None
    """The optional comment string. Default is None."""

    directory = None
    """The optional directory to save Capture to Disk files in. Default is
    the OmniEngine's Data Directory.
    """

    file_pattern = 'Capture 1-'
    """The Capture to Disk file pattern. Default is 'Capture 1-'."""

    file_size = 256 * BYTES_IN_A_MEGABYTE
    """The size in gigabytes of the all the capture's packet files.
    Default is 256 Megabytes.
    """

    group_id = None
    """The Id of the capture's group."""

    group_name = ''
    """The name of the capture's group."""

    id = None
    """The Global Unique Identier of the capture."""

    intelligent_ctd_count = 0
    """The ctd intelligent count value."""

    keep_last_files_count = 10
    """The number of files to keep if
    :func:`option_keep_last_files
    <omniscript.capturetemplate.generalsettings.option_keep_last_files>`
    is enabled.
    Default is 10.
    """

    max_file_age = SECONDS_IN_A_DAY
    """The maximum number of seconds a capture file may be open until
    a new file is created if
    :func:`option_file_age
    <omniscript.capturetemplate.generalsettings.option_file_age>`
    is enabled. Default is 1 day.
    """

    max_total_file_size = 10 * BYTES_IN_A_GIGABYTE
    """The maximum amount of disk space if
    :func:`option_total_file_size
    <omniscript.capturetemplate.generalsettings.option_total_file_size>`
    is enabled.
    Default is 10 gigabytes.
    """

    name = 'Capture 1'
    """The name of the capture. Default is 'Capture 1'."""

    owner = None
    """The name of the account that owns the capture."""

    reserved_size = 16384
    """Amount of diskspace in megabytes (confirm) to reserve on a
    Timeline for captures. Default is 16 Gigabytes.
    """

    slice_length = 128
    """The number of bytes to slice a packet to when option_slicing is
    enabled. Default is 128 bytes.
    """

    tap_timestamps = 0
    """The type of tap timestamps. One of the TAP TIMESTAMPS
    constants.
    """

    option_capture_to_disk = False
    """Is Capture to disk is enabled? Default is False."""

    option_continuous_capture = True
    """Is continuous capture enabled? Default is True."""

    option_deduplicate = False
    """Is discarding duplicate packets enabled? Default is False."""

    option_file_age = False
    """Is the option to start a new capture files when file has been
    open for
    :func:`max_file_age
    <omniscript.capturetemplate.generalsettings.max_file_age>`
    seconds is enabled? Default is False.
    """

    option_intelligent_ctd = False
    """Is the intelligent ctd option enabled."""

    option_keep_last_files = False
    """Is the option to keep only the last
    :func:`keep_last_files_count
    <omniscript.capturetemplate.generalsettings.keep_last_files_count>`
    files option enabled? Default is False.
    """

    option_multistream = False
    """Is multistream enabled? Default is False."""

    option_priority_ctd = False
    """Is priority to Capture to Disk disk enabled. Default is False.
    If enabled priority will be given to Capture to Disk over packet
    processing.
    """

    option_save_as_template = False
    """Save these setting as a Capture Template. Default is False."""

    option_slicing = False
    """Is packet slicing enabled? Default is False."""

    option_spotlight_capture = False
    """Is Capture the Spotlight Capture? Default is False."""

    option_start_capture = False
    """Is the option to start the capture when its created enabled?
    Default is False.
    """

    option_timeline_app_stats = False
    """Is Application Statistics enabled? Default is False."""

    option_timeline_stats = False
    """Is Timeline Statistics enabled? Default is False."""

    option_timeline_top_stats = False
    """Is Top Statistics enabled? Default is False."""

    option_timeline_voip_stats = False
    """Is VoIP Statistics enabled? Default is False."""

    option_total_file_size = False
    """Is the option to restrict the maximum amount of diskspace to
    a total of
    :func:`max_total_file_size
    <omniscript.capturetemplate.generalsettings.max_total_file_size>`
    bytes is enabled? Default is False.
    """

    # Tags
    _json_label = 'generalSettings'
    _json_class_name = _tag_prop_bag
    _json_buffer_size = 'bufferSize'
    _json_id = 'captureId'
    _json_capture_to_disk = 'captureToDisk'
    _json_comment = 'comment'
    _json_continuous_capture = 'continuousCapture'
    _json_file_pattern = 'ctdFilePattern'
    _json_file_size = 'ctdFileSize'
    _json_intelligent_count = 'ctdIntelligentCount'
    _json_keep_last_files = 'ctdKeepLastFiles'
    _json_keep_last_files_count = 'ctdKeepLastFilesCount'
    _json_max_file_age = 'ctdMaxFileAge'
    _json_priority_ctd = 'ctdPriority'
    _json_file_age = 'ctdUseMaxFileAge'
    _json_intelligent_ctd = 'ctdIntelligent'
    _json_total_file_size = 'ctdUseMaxTotalFileSize'
    _json_deduplicate = 'deduplicate'
    _json_app_stats = 'enableAppStats'
    _json_timeline_stats = 'enableTimelineStats'
    _json_top_stats = 'enableTopStats'
    _json_voip_stats = 'enableVoIPStats'
    _json_name = 'name'
    _json_owner = 'owner'
    _json_save_as_template = 'saveAsTemplate'
    _json_slice_length = 'sliceLength'
    _json_slicing = 'slicing'
    _json_start_capture = 'startCapture'
    _json_tap_timestamps = 'tapTimestamps'

    _tag_buffer_size = 'buffer_size'
    _tag_comment = 'comment'
    _tag_directory = 'directory'
    _tag_file_pattern = 'file_pattern'
    _tag_file_size = 'file_size'
    _tag_group_id = 'group_id'
    _tag_group_name = 'group_name'
    _tag_intelligent_count = 'intelligent_ctd_count'
    _tag_keep_last_files_count = 'keep_last_files_count'
    _tag_label = 'GeneralSettings'
    _tag_max_file_age = 'max_file_age'
    _tag_max_total_file_size = 'max_total_file_size'
    _tag_owner = 'owner'
    _tag_reserved_size = 'reserved_size'
    _tag_slice_length = 'slice_length'
    _tag_tap_timestamps = 'tap_timestamps'
    _tag_capture_to_disk = 'option_capture_to_disk'
    _tag_continuous_capture = 'option_continuous_capture'
    _tag_deduplicate = 'option_deduplicate'
    _tag_file_age = 'option_file_age'
    _tag_intelligent_ctd = 'option_intelligent_ctd'
    _tag_keep_last_files = 'option_keep_last_files'
    _tag_multistream = 'option_multistream'
    _tag_priority_ctd = 'option_priority_ctd'
    _tag_root_name = _tag_props
    _tag_save_as_template = 'option_save_as_template'
    _tag_slicing = 'option_slicing'
    _tag_spotlight_capture = 'option_spotlight_capture'
    _tag_start_capture = 'option_start_capture'
    _tag_app_stats = 'option_timeline_app_stats'
    _tag_timeline_stats = 'option_timeline_stats'
    _tag_top_stats = 'option_timeline_top_stats'
    _tag_voip_stats = 'option_timeline_voip_stats'
    _tag_total_file_size = 'option_total_file_size'

    _tag_xml_application_stats = "EnableAppStats"
    _tag_xml_buffer_size = "BufferSize"
    _tag_xml_capture_id = "CaptureID"
    _tag_xml_capture_to_disk = "CaptureToDisk"
    _tag_xml_comment = "Comment"
    _tag_xml_continuous_capture = "ContinuousCapture"
    _tag_xml_deduplicate = "Deduplicate"
    _tag_xml_directory = "CtdDir"
    _tag_xml_file_age = "CtdUseMaxFileAge"
    _tag_xml_file_pattern = "CtdFilePattern"
    _tag_xml_file_size = "CtdFileSize"
    _tag_xml_group_id = "GroupID"
    _tag_xml_group_name = "GroupName"
    _tag_xml_keep_last_files = "CtdKeepLastFiles"
    _tag_xml_keep_last_files_count = "CtdKeepLastFilesCount"
    _tag_xml_max_file_age = "CtdMaxFileAge"
    _tag_xml_max_total_file_size = "CtdMaxTotalFileSize"
    _tag_xml_multistream = "MultiStream"
    _tag_xml_gs_name = "Name"
    _tag_xml_owner = "Owner"
    _tag_xml_priority_ctd = "CtdPriority"
    _tag_xml_reserved_size = "CtdReservedSize"
    _tag_xml_save_as_template = "SaveAsTemplate"
    _tag_xml_slice_length = "SliceLength"
    _tag_xml_slicing = "Slicing"
    _tag_xml_spotlight_capture = "SpotlightCapture"
    _tag_xml_start_capture = "StartCapture"
    _tag_xml_tap_timestamps = "TapTimestamps"
    _tag_xml_timeline_stats = "EnableTimelineStats"
    _tag_xml_timeline_top_stats = "EnableTopStats"
    _tag_xml_total_file_size = "CtdUseMaxTotalFileSize"
    _tag_xml_voip_stats = "EnableVoIPStats"

    _general_prop_dict = {
        _json_classid: _tag_classid,
        _json_buffer_size: _tag_buffer_size,
        _json_id: _tag_id,
        _json_capture_to_disk: _tag_capture_to_disk,
        _json_comment: _tag_comment,
        _json_continuous_capture: _tag_continuous_capture,
        _json_file_pattern: _tag_file_pattern,
        _json_file_size: _tag_file_size,
        _json_intelligent_count: _tag_intelligent_count,
        _json_keep_last_files: _tag_keep_last_files,
        _json_keep_last_files_count: _tag_keep_last_files_count,
        _json_max_file_age: _tag_max_file_age,
        _json_priority_ctd: _tag_priority_ctd,
        _json_file_age: _tag_file_age,
        _json_intelligent_ctd: _tag_intelligent_ctd,
        _json_total_file_size: _tag_total_file_size,
        _json_deduplicate: _tag_deduplicate,
        _json_app_stats: _tag_app_stats,
        _json_timeline_stats: _tag_timeline_stats,
        _json_top_stats: _tag_top_stats,
        _json_voip_stats: _tag_voip_stats,
        _json_name: _tag_name,
        _json_owner: _tag_owner,
        _json_save_as_template: _tag_save_as_template,
        _json_slice_length: _tag_slice_length,
        _json_slicing: _tag_slicing,
        _json_start_capture: _tag_start_capture,
        _json_tap_timestamps: _tag_tap_timestamps
    }

    def __init__(self):
        self._class_id = None
        self.buffer_size = GeneralSettings.buffer_size
        self.comment = GeneralSettings.comment
        self.directory = GeneralSettings.directory
        self.file_pattern = GeneralSettings.file_pattern
        self.file_size = GeneralSettings.file_size
        self.group_id = GeneralSettings.group_id
        self.group_name = None
        self.id = GeneralSettings.id
        self.intelligent_ctd_count = GeneralSettings.intelligent_ctd_count
        self.keep_last_files_count = GeneralSettings.keep_last_files_count
        self.max_file_age = GeneralSettings.max_file_age
        self.max_total_file_size = GeneralSettings.max_total_file_size
        self.name = GeneralSettings.name
        self.owner = GeneralSettings.owner
        self.reserved_size = GeneralSettings.reserved_size
        self.slice_length = GeneralSettings.slice_length
        self.tap_timestamps = GeneralSettings.tap_timestamps
        self.option_capture_to_disk = GeneralSettings.option_capture_to_disk
        self.option_continuous_capture = GeneralSettings.option_continuous_capture
        self.option_deduplicate = GeneralSettings.option_deduplicate
        self.option_file_age = GeneralSettings.option_file_age
        self.option_intelligent_ctd = GeneralSettings.option_intelligent_ctd
        self.option_keep_last_files = GeneralSettings.option_keep_last_files
        self.option_multistream = GeneralSettings.option_multistream
        self.option_priority_ctd = GeneralSettings.option_priority_ctd
        self.option_save_as_template = GeneralSettings.option_save_as_template
        self.option_slicing = GeneralSettings.option_slicing
        self.option_start_capture = GeneralSettings.option_start_capture
        self.option_timeline_app_stats = GeneralSettings.option_timeline_app_stats
        self.option_timeline_stats = GeneralSettings.option_timeline_stats
        self.option_timeline_top_stats = GeneralSettings.option_timeline_top_stats
        self.option_timeline_voip_stats = GeneralSettings.option_timeline_voip_stats
        self.option_total_file_size = GeneralSettings.option_total_file_size
        self.option_spotlight_capture = GeneralSettings.option_spotlight_capture

    def _load(self, props):
        """Load the General Settings from a dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = GeneralSettings._general_prop_dict.get(k)
                if a is None or not hasattr(self, a):
                    continue
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == GeneralSettings._tag_buffer_size:
                    self.buffer_size = int(v)
                elif a == _tag_id:
                    self.id = OmniId(v)
                elif a == GeneralSettings._tag_capture_to_disk:
                    self.option_capture_to_disk = v
                elif a == GeneralSettings._tag_comment:
                    self.comment = v
                elif a == GeneralSettings._tag_continuous_capture:
                    self.option_continuous_capture = v
                elif a == GeneralSettings._tag_deduplicate:
                    self.option_deduplicate = v
                elif a == GeneralSettings._tag_directory:
                    self.directory = v
                elif a == GeneralSettings._tag_file_age:
                    self.option_file_age = v
                elif a == GeneralSettings._tag_file_pattern:
                    self.file_pattern = v
                elif a == GeneralSettings._tag_file_size:
                    self.file_size = int(v)
                elif a == GeneralSettings._tag_group_id:
                    self.group_id = OmniId(v)
                elif a == GeneralSettings._tag_group_name:
                    self.group_name = v
                elif a == GeneralSettings._tag_keep_last_files:
                    self.option_keep_last_files = v
                elif a == GeneralSettings._tag_keep_last_files_count:
                    self.keep_last_files_count = int(v)
                elif a == GeneralSettings._tag_max_file_age:
                    self.max_file_age = int(v)
                elif a == GeneralSettings._tag_max_total_file_size:
                    self.max_total_file_size = int(v)
                elif a == GeneralSettings._tag_multistream:
                    self.option_multistream = v
                elif a == _tag_name:
                    self.name = v
                elif a == GeneralSettings._tag_owner:
                    self.owner = v
                elif a == GeneralSettings._tag_priority_ctd:
                    self.option_priority_ctd = v
                elif a == GeneralSettings._tag_reserved_size:
                    self.reserved_size = int(v)
                elif a == GeneralSettings._tag_save_as_template:
                    self.option_save_as_template = v
                elif a == GeneralSettings._tag_slice_length:
                    self.slice_length = int(v)
                elif a == GeneralSettings._tag_spotlight_capture:
                    self.option_spotlight_capture = v
                elif a == GeneralSettings._tag_slicing:
                    self.option_slicing = v
                elif a == GeneralSettings._tag_start_capture:
                    self.option_start_capture = v
                elif a == GeneralSettings._tag_tap_timestamps:
                    self.tap_timestamps = int(v)
                elif a == GeneralSettings._tag_timeline_stats:
                    self.option_timeline_stats = v
                elif a == GeneralSettings._tag_app_stats:
                    self.option_timeline_app_stats = v
                elif a == GeneralSettings._tag_top_stats:
                    self.option_timeline_top_stats = v
                elif a == GeneralSettings._tag_total_file_size:
                    self.option_total_file_size = v
                elif a == GeneralSettings._tag_voip_stats:
                    self.option_timeline_voip_stats = v

    def _load_xml(self, obj):
        """Load the General Settings from an ETree.SubElement."""
        props = obj.find(GeneralSettings._tag_root_name)
        if props is not None:
            for prop in props.findall(_tag_prop):
                propName = prop.attrib[_tag_name]
                if propName == GeneralSettings._tag_buffer_size:
                    self.buffer_size = int(prop.text)
                elif propName == GeneralSettings._tag_xml_capture_id:
                    self.id = OmniId(prop.text)
                elif propName == GeneralSettings._tag_xml_capture_to_disk:
                    self.option_capture_to_disk = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_comment:
                    self.comment = prop.text
                elif propName == GeneralSettings._tag_xml_continuous_capture:
                    self.option_continuous_capture = \
                        _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_deduplicate:
                    self.option_deduplicate = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_directory:
                    self.directory = prop.text
                elif propName == GeneralSettings._tag_xml_file_age:
                    self.option_file_age = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_file_pattern:
                    self.file_pattern = prop.text
                elif propName == GeneralSettings._tag_xml_file_size:
                    self.file_size = int(prop.text)
                elif propName == GeneralSettings._tag_xml_group_id:
                    self.group_id = OmniId(prop.text)
                elif propName == GeneralSettings._tag_xml_group_name:
                    self.group_name = prop.text
                elif propName == GeneralSettings._tag_xml_keep_last_files:
                    self.option_keep_last_files = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_keep_last_files_count:
                    self.keep_last_files_count = int(prop.text)
                elif propName == GeneralSettings._tag_xml_max_file_age:
                    self.max_file_age = int(prop.text)
                elif propName == GeneralSettings._tag_xml_max_total_file_size:
                    self.max_total_file_size = int(prop.text)
                elif propName == GeneralSettings._tag_xml_multistream:
                    self.option_multistream = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_gs_name:
                    self.name = prop.text
                elif propName == GeneralSettings._tag_xml_owner:
                    self.owner = prop.text
                elif propName == GeneralSettings._tag_xml_priority_ctd:
                    self.option_priority_ctd = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_reserved_size:
                    self.reserved_size = int(prop.text)
                elif propName == GeneralSettings._tag_xml_save_as_template:
                    self.option_save_as_template = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_slice_length:
                    self.slice_length = int(prop.text)
                elif propName == GeneralSettings._tag_xml_spotlight_capture:
                    self.option_spotlight_capture = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_slicing:
                    self.option_slicing = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_start_capture:
                    self.option_start_capture = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_tap_timestamps:
                    self.tap_timestamps = int(prop.text)
                elif propName == GeneralSettings._tag_xml_timeline_stats:
                    self.option_timeline_stats = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_application_stats:
                    self.option_timeline_app_stats = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_timeline_top_stats:
                    self.option_timeline_top_stats = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_total_file_size:
                    self.option_total_file_size = _from_prop_boolean(prop.text)
                elif propName == GeneralSettings._tag_xml_voip_stats:
                    self.option_timeline_voip_stats = _from_prop_boolean(prop.text)

    def _store(self, props, new):
        """Store the General Settings into the ETree.SubElement."""
        if not isinstance(props, dict):
            return
        if new:
            self.id = OmniId(True)
        _props = {}
        _props[GeneralSettings._json_buffer_size] = self.buffer_size
        _props[GeneralSettings._json_id] = self.id.format()
        _props[GeneralSettings._json_capture_to_disk] = self.option_capture_to_disk
        _props[GeneralSettings._json_comment] = self.comment
        _props[GeneralSettings._json_continuous_capture] = self.option_continuous_capture
        _props[GeneralSettings._json_file_pattern] = self.file_pattern
        _props[GeneralSettings._json_file_size] = self.file_size
        _props[GeneralSettings._json_keep_last_files] = self.option_keep_last_files
        _props[GeneralSettings._json_keep_last_files_count] = self.keep_last_files_count
        _props[GeneralSettings._json_max_file_age] = self.max_file_age
        _props[GeneralSettings._json_priority_ctd] = self.option_priority_ctd
        _props[GeneralSettings._json_file_age] = self.option_file_age
        _props[GeneralSettings._json_total_file_size] = self.option_total_file_size
        _props[GeneralSettings._json_deduplicate] = self.option_deduplicate
        _props[GeneralSettings._json_app_stats] = self.option_timeline_app_stats
        _props[GeneralSettings._json_timeline_stats] = self.option_timeline_stats
        _props[GeneralSettings._json_top_stats] = self.option_timeline_top_stats
        _props[GeneralSettings._json_voip_stats] = self.option_timeline_voip_stats
        _props[GeneralSettings._json_name] = self.name
        _props[GeneralSettings._json_owner] = self.owner
        _props[GeneralSettings._json_save_as_template] = self.option_save_as_template
        _props[GeneralSettings._json_slice_length] = self.slice_length
        _props[GeneralSettings._json_slicing] = self.option_slicing
        _props[GeneralSettings._json_start_capture] = self.option_start_capture
        _props[GeneralSettings._json_tap_timestamps] = self.tap_timestamps
        _props[_json_classid] = _get_class_id(GeneralSettings._json_class_name)
        props[GeneralSettings._json_label] = _props

    def set_timeline(self, enable=True):
        self.option_timeline_stats = enable
        self.option_timeline_app_stats = enable
        self.option_timeline_top_stats = enable
        self.option_timeline_voip_stats = enable

    def set_multistream(self, enable=False):
        self.option_multistream = enable


class GraphsSettings(object):
    """The Graphs Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    graphs = []
    """A list of
    :class:`GraphTemplate <omniscript.graphtemplate.GraphTemplate>`,
    or OmniId or OmniId as a string.

    The function :func:`get_graph_template_list()
    <omniscript.omniengine.OmniEngine.get_graph_template_list>`
    returns a list of GraphTemplate objects.
    """

    enabled = False
    """Are graphs enabled."""

    interval = 15
    """The interval in seconds."""

    file_count = 2

    file_buffer_size = 50

    hours_to_keep = 1
    """Keep most recent in hours."""

    option_preserve_files = False

    # XML Tags
    _json_label = 'graphSettings'
    _json_class_name = 'GraphSettings'
    _json_graphs = 'graphs'
    _json_interval = 'interval'
    _json_interval_units = 'intervalUnit'
    _json_file_count = 'fileCount'
    _json_file_buffer_size = 'fileBufferSize'
    _json_hours_to_keep = 'hoursToKeep'
    _json_memory = 'memory'
    _json_preserve_files = 'preserveFiles'
    _json_templates = 'templates'

    _tag_file_buffer_size = 'file_buffer_size'
    _tag_file_count = 'file_count'
    _tag_graphs = 'graphs'
    _tag_hours_to_keep = 'hours_to_keep'
    _tag_interval = 'interval'
    _tag_interval_units = 'interval_units'
    _tag_label = 'GraphSettings'
    _tag_memory = 'memory'
    _tag_preserve_files = 'option_preserve_files'
    _tag_templates = 'templates'

    _tag_xml_graphdata = "graphdata"
    _tag_xml_interval = "Interval"
    _tag_xml_file_count = "FileCnt"
    _tag_xml_file_buffer_size = "FileBufferSize"
    _tag_xml_preserve_files = "PreserveFiles"
    _tag_xml_hours_to_keep = "memory"
    _tag_xml_templates = "templates"
    _tag_xml_template = "template"
    _tag_xml_units = "IntervalUnit"

    _graphs_prop_dict = {
        _json_classid: _tag_classid,
        _json_enabled: _tag_enabled,
        _json_file_buffer_size: _tag_file_buffer_size,
        _json_file_count: _tag_file_count,
        _json_interval: _tag_interval,
        _json_interval_units: _tag_interval_units,
        _json_hours_to_keep: _tag_hours_to_keep,
        _json_memory: _tag_memory,
        _json_preserve_files: _tag_preserve_files,
        _json_templates: _tag_templates
    }

    def __init__(self):
        self.graphs = []
        self.enabled = GraphsSettings.enabled
        self.interval = GraphsSettings.interval
        self.file_count = GraphsSettings.file_count
        self.file_buffer_size = GraphsSettings.file_buffer_size
        self.hours_to_keep = GraphsSettings.hours_to_keep
        self.option_preserve_files = GraphsSettings.option_preserve_files

    def _load(self, props, engine=None):
        """Load the Graph Settings from a Dictionairy."""
        # TODO: Implement this.
        # _interval = 1
        # _interval_units = 1
        if isinstance(props, dict):
            for k, v in props.items():
                a = GraphsSettings._graphs_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if a == _tag_classid:
                        self._class_id = OmniId(v)
                    elif a == _tag_enabled:
                        self.enabled = v
                    # elif a == GraphsSettings._tag_interval:
                    #     _interval = int(v)
                    # elif a == GraphsSettings._tag_interval_units:
                    #     _interval_units = int(v)
                    elif a == GraphsSettings._tag_file_count:
                        self.file_count = int(v)
                    elif a == GraphsSettings._tag_file_buffer_size:
                        self.file_buffer_size = int(v)
                    elif a == GraphsSettings._tag_hours_to_keep:
                        self.hours_to_keep = int(v)
                    elif a == GraphsSettings._tag_preserve_files:
                        self.option_preserve_files = v
        # graph_template_list = []
        # if engine is not None:
        #     graph_template_list = engine.get_graph_template_list()
        # if graph_data is not None:
        #     templates = graph_data.find(GraphsSettings._tag_templates)
        #     for template in templates.findall(GraphsSettings._tag_template):
        #         id = OmniId(template.attrib[_tag_id])
        #         template = find_graph_template(graph_template_list, id, 'id')
        #         if template:
        #             self.graphs.append(template)
        #         # else:
        #         #     name = id
        # if (_units < GRAPHS_INTERVAL_SECONDS) or (_units > GRAPHS_INTERVAL_DAYS):
        #     _units = GRAPHS_INTERVAL_SECONDS
        # self.interval = _interval * interval_multiplier[_units]

    def _load_xml(self, obj, engine=None):
        """Load the Graph Settings from an ETree.SubElement."""
        graph_data = obj.find(GraphsSettings._tag_xml_graphdata)
        self.enabled = _is_attribute_enabled(graph_data, _tag_alt_enabled)
        self.file_count = int(graph_data.attrib.get(
            GraphsSettings._tag_xml_file_count, str(GraphsSettings.file_count)))
        self.file_buffer_size = int(graph_data.attrib.get(
            GraphsSettings._tag_xml_file_buffer_size, str(GraphsSettings.file_buffer_size)))
        self.hours_to_keep = int(graph_data.attrib.get(
            GraphsSettings._tag_xml_hours_to_keep, str(GraphsSettings.hours_to_keep)))
        self.option_preserve_files = _is_attribute_enabled(
            graph_data, GraphsSettings._tag_xml_preserve_files)
        _interval = int(graph_data.attrib.get(
            GraphsSettings._tag_xml_interval, str(GraphsSettings.interval)))
        _units = int(graph_data.attrib.get(GraphsSettings._tag_xml_units, '1'))

        graph_template_list = []
        if engine is not None:
            graph_template_list = engine.get_graph_template_list()
        if graph_data is not None:
            templates = graph_data.find(GraphsSettings._tag_xml_templates)
            for template in templates.findall(GraphsSettings._tag_xml_template):
                id = OmniId(template.attrib[_tag_id])
                template = find_graph_template(graph_template_list, id, 'id')
                if template:
                    self.graphs.append(template)
                # else:
                #     name = id

        if (_units < GRAPHS_INTERVAL_SECONDS) or (_units > GRAPHS_INTERVAL_DAYS):
            _units = GRAPHS_INTERVAL_SECONDS
        self.interval = _interval * interval_multiplier[_units]

    def _store(self, props):
        """Store the Graphs Data in a JSON props."""
        if not isinstance(props, dict) or not self.enabled:
            return
        _interval, _units = _to_interval_units(self.interval)
        _props = {}
        _props[_json_enabled] = self.enabled
        _props[GraphsSettings._json_file_buffer_size] = self.file_buffer_size
        _props[GraphsSettings._json_file_count] = self.file_count
        _props[GraphsSettings._json_interval] = _interval
        _props[GraphsSettings._json_interval_units] = _units
        _props[GraphsSettings._json_hours_to_keep] = self.hours_to_keep
        _props[GraphsSettings._json_preserve_files] = self.option_preserve_files
        _props[_json_classid] = _get_class_id(GraphsSettings._json_class_name)
        props[GraphsSettings._json_label] = _props


class HardwareConfig(object):
    """The Hardware Configuration section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = OmniId('6F3377D6-FBD7-4CBD-A740-2EAE63DBF639')
    """The Class Identifier of the object."""

    profile_list = []

    # Tags
    _json_label = 'hardwareConfig'
    _json_class_name = 'HardwareConfig'
    _json_profile_list = 'hardwareProfiles'

    _tag_profile_list = 'profile_list'

    _hardware_prop_dict = {
        _json_classid: _tag_classid,
        _json_profile_list: _tag_profile_list
    }

    def __init__(self):
        self._class_id = None
        self.profile_list = []

    def _load(self, props, engine=None):
        """Load the Hardware Configuration from a Dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = HardwareConfig._hardware_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if a == _tag_classid:
                        self._class_id = OmniId(v)
                    elif a == 'profiles':
                        for p in v:
                            self.profile_list.append(OmniId(p))

    def _store(self, props):
        """Store the Hardware Configuration into a JSON props."""
        if not isinstance(props, dict) or not self.profile_list:
            return
        _props = {}
        _props[HardwareConfig._json_profile_list] = self.profile_list
        _props[_json_classid] = _get_class_id(HardwareConfig._json_class_name)
        props[HardwareConfig._json_label] = _props


class IndexingSettings(object):
    """The Indexing Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    option_application = False
    """Is Application indexing enabled?"""

    option_country = False
    """Is Country indexing enabled?"""

    option_ethernet = False
    """Is Ethernet indexing enabled?"""

    option_ipv4 = False
    """Is IPv4 indexing enabled?"""

    option_ipv6 = False
    """Is IPv6 indexing enabled?"""

    option_mpls = False
    """Is MPLS indexing enabled?"""

    option_port = False
    """Is Port indexing enabled?"""

    option_protospec = False
    """Is Protospec indexing enabled?"""

    option_vlan = False
    """Is VLAN indexing enabled?"""

    # Tags
    _json_label = 'indexingSettings'
    _json_class_name = 'PropertyList'

    _tag_label = 'IndexingSettings'
    _tag_root_name = _tag_props

    # Options list of tuples(attribute, name)
    _options = [
        ('option_ipv4', 'Indexing IPv4'),
        ('option_ipv6', 'Indexing IPv6'),
        ('option_ethernet', 'Indexing Ethernet'),
        ('option_port', 'Indexing Port'),
        ('option_protospec', 'Indexing Protospec'),
        ('option_application', 'Indexing Application'),
        ('option_vlan', 'Indexing VLAN'),
        ('option_mpls', 'Indexing MPLS'),
        ('option_country', 'Indexing Country')
    ]

    _indexing_prop_dict = {
        _json_classid: _tag_classid,
        _tag_props: _tag_props
    }

    def __init__(self):
        self.option_application = IndexingSettings.option_application
        self.option_country = IndexingSettings.option_country
        self.option_ethernet = IndexingSettings.option_ethernet
        self.option_ipv4 = IndexingSettings.option_ipv4
        self.option_ipv6 = IndexingSettings.option_ipv6
        self.option_mpls = IndexingSettings.option_mpls
        self.option_port = IndexingSettings.option_port
        self.option_protospec = IndexingSettings.option_protospec
        self.option_vlan = IndexingSettings.option_vlan

    def _load(self, props):
        """Load the Indexing Settings from a Dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = IndexingSettings._indexing_prop_dict.get(k)
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == _tag_props:
                    for p in v:
                        if isinstance(p, dict) and (_tag_value in p):
                            # TODO: implement this.
                            # i = int(p[_tag_value])
                            pass
        # self.set_all(False)
        # props = obj.find(IndexingSettings._tag_root_name)
        # if props is not None:
        #     for prop in props.findall(_tag_prop):
        #         _index = int(prop.text)
        #         if (_index < len(IndexingSettings._options)
        #             and hasattr(self, IndexingSettings._options[_index])):
        #             setattr(self, IndexingSettings._options[_index], True)

    def _load_xml(self, obj):
        """Load the Indexing Settings from an ETree.SubElement."""
        if 'null' in obj.attrib:
            null_enabled = obj.attrib['null']
            if null_enabled:
                return
        self.set_all(False)
        props = obj.find(IndexingSettings._tag_root_name)
        if props is not None:
            for prop in props.findall(_tag_prop):
                _index = int(prop.text)
                if _index < len(IndexingSettings._options) and \
                        hasattr(self, IndexingSettings._options[_index]):
                    setattr(self, IndexingSettings._options[_index], True)

    def _store(self, props):
        """Store the Indexing Data in a JSON props."""
        if not isinstance(props, dict):
            return
        _props = {}
        _props[_tag_props] = []
        if self.option_ipv4:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 0})
        if self.option_ipv6:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 1})
        if self.option_ethernet:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 2})
        if self.option_port:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 3})
        if self.option_protospec:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 4})
        if self.option_application:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 5})
        if self.option_vlan:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 6})
        if self.option_mpls:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 7})
        if self.option_country:
            _props[_tag_props].append({_tag_type: 17, _tag_value: 8})
        if not _props[_tag_props]:
            return
        _props[_json_classid] = _get_class_id(IndexingSettings._json_class_name)
        props[IndexingSettings._json_label] = _props

    def set_all(self, enable=True):
        """Enable (default) or disable all the indexing options."""
        self.option_application = enable
        self.option_country = enable
        self.option_ethernet = enable
        self.option_ipv4 = enable
        self.option_ipv6 = enable
        self.option_mpls = enable
        self.option_port = enable
        self.option_protospec = enable
        self.option_vlan = enable


class StatisticsOutputSettings(object):
    """The Statistics Output Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    enabled = False
    """Are the Statistics Output Settings enabled?"""

    files_to_keep = 60
    """The number of files to keep."""

    interval = 60
    """Output interval in seconds"""

    new_set_interval = 60
    """New Set interval in seconds"""

    report_path = ''
    """The path where reports will be written."""

    report_type = 4
    """The report format type."""

    user_path = ''
    """The user path."""

    option_notify = False
    """Is the notification option enabled?"""

    option_align_new_set = False
    """Are new sets to be aligned?"""

    option_align_output = False
    """Is the output to be aligned?"""

    option_new_set = False
    """Is the new set option enabled?"""

    option_scheduled = False
    """Is the scheduled option enabled?"""

    option_keep_files = False
    """Is the keep files option enabled?"""

    option_reset_output = False
    """Is the reset output option enabled?"""

    # Tags
    _json_label = 'statsOutput'
    _json_class_name = 'StatsOutput'
    _json_files_to_keep = 'keep'
    _json_interval = 'outputInterval'
    _json_interval_units = 'outputIntervalUnit'
    _json_new_set_interval = 'newSetInterval'
    _json_new_set_units = 'newSetIntervalUnit'
    _json_report_path = 'reportPath'
    _json_report_type = 'reportType'
    _json_user_path = 'userPath'
    _json_notify = 'notify'
    _json_align_new_set = 'alignNewSet'
    _json_align_output = 'alignOutput'
    _json_new_set = 'newSet'
    _json_scheduled = 'scheduled'
    _json_keep_files = 'keepFiles'
    _json_reset_output = 'resetOutput'

    _tag_files_to_keep = 'files_to_keep'
    _tag_interval = 'interval'
    _tag_interval_units = 'interval_units'
    _tag_label = 'StatsOutput'
    _tag_new_set_interval = 'new_set_interval'
    _tag_new_set_units = 'new_set_interval_units'
    _tag_report_path = 'report_path'
    _tag_report_type = 'report_type'
    _tag_user_path = 'user_path'
    _tag_notify = 'option_notify'
    _tag_align_new_set = 'option_align_new_set'
    _tag_align_output = 'option_align_output'
    _tag_new_set = 'option_new_set'
    _tag_scheduled = 'option_scheduled'
    _tag_keep_files = 'option_keep_files'
    _tag_reset_output = 'option_reset_output'

    _tag_xml_align_new_set = "alignNewSet"
    _tag_xml_align_output = "alignOutput"
    _tag_xml_files_to_keep = "keep"
    _tag_xml_keep_files = "keepEnabled"
    _tag_xml_new_set = "newSetEnabled"
    _tag_xml_new_set_interval = "newSetInterval"
    _tag_xml_new_set_units = "newSetIntervalUnit"
    _tag_xml_notify = "notify"
    _tag_xml_interval = "outputInterval"
    _tag_xml_report_path = "reportPath"
    _tag_xml_report_type = "outputType"
    _tag_xml_reset_output = "ResetOutput"
    _tag_xml_root_name = "statsoutput"
    _tag_xml_scheduled = "scheduled"
    _tag_xml_units = "outputIntervalUnit"
    _tag_xml_user_path = "userPath"

    _statistics_output_prop_dict = {
        _json_classid: _tag_classid,
        _tag_enabled: _tag_enabled,
        _json_files_to_keep: _tag_files_to_keep,
        _json_interval: _tag_interval,
        _json_interval_units: _tag_interval_units,
        _json_new_set_interval: _tag_new_set_interval,
        _json_new_set_units: _tag_new_set_units,
        _json_report_path: _tag_report_path,
        _json_report_type: _tag_report_type,
        _json_user_path: _tag_user_path,
        _json_notify: _tag_notify,
        _json_align_new_set: _tag_align_new_set,
        _json_align_output: _tag_align_output,
        _json_new_set: _tag_new_set,
        _json_scheduled: _tag_scheduled,
        _json_keep_files: _tag_keep_files,
        _json_reset_output: _tag_reset_output,
    }

    def __init__(self):
        self.enabled = StatisticsOutputSettings.enabled
        self.files_to_keep = StatisticsOutputSettings.files_to_keep
        self.interval = StatisticsOutputSettings.interval
        self.new_set_interval = StatisticsOutputSettings.new_set_interval
        self.report_path = StatisticsOutputSettings.report_path
        self.report_type = StatisticsOutputSettings.report_type
        self.user_path = StatisticsOutputSettings.user_path
        self.option_notify = StatisticsOutputSettings.option_notify
        self.option_align_new_set = StatisticsOutputSettings.option_align_new_set
        self.option_align_output = StatisticsOutputSettings.option_align_output
        self.option_new_set = StatisticsOutputSettings.option_new_set
        self.option_scheduled = StatisticsOutputSettings.option_scheduled
        self.option_keep_files = StatisticsOutputSettings.option_keep_files
        self.option_reset_output = StatisticsOutputSettings.option_reset_output

    def _load(self, props):
        """Load the Statistics Output Settings from a Dictionairy."""
        if isinstance(props, dict):
            _interval = 0
            _interval_units = 0
            _new_set_interval = 0
            _new_set_units = 0
            for k, v in props.items():
                a = StatisticsOutputSettings._statistics_output_prop_dict.get(k)
                if a is None or not hasattr(self, a):
                    continue
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == _tag_enabled:
                    self.enabled = v
                elif a == StatisticsOutputSettings._tag_files_to_keep:
                    self.files_to_keep = int(v)
                elif a == StatisticsOutputSettings._tag_interval:
                    _interval = int(v)
                elif a == StatisticsOutputSettings._tag_interval_units:
                    _interval_units = int(v)
                elif a == StatisticsOutputSettings._tag_new_set_interval:
                    _new_set_interval = int(v)
                elif a == StatisticsOutputSettings._tag_new_set_units:
                    _new_set_units = int(v)
                elif a == StatisticsOutputSettings._tag_report_path:
                    self.report_path = v
                elif a == StatisticsOutputSettings._tag_report_type:
                    self.report_type = int(v)
                elif a == StatisticsOutputSettings._tag_user_path:
                    self.user_path = v
                elif a == StatisticsOutputSettings._tag_notify:
                    self.option_notify = v
                elif a == StatisticsOutputSettings._tag_align_new_set:
                    self.option_align_new_set = v
                elif a == StatisticsOutputSettings._tag_align_output:
                    self.option_align_output = v
                elif a == StatisticsOutputSettings._tag_new_set:
                    self.option_new_set = v
                elif a == StatisticsOutputSettings._tag_scheduled:
                    self.option_scheduled = v
                elif a == StatisticsOutputSettings._tag_keep_files:
                    self.option_keep_files = v
                elif a == StatisticsOutputSettings._tag_reset_output:
                    self.option_reset_output = v

            if ((_interval_units < GRAPHS_INTERVAL_SECONDS)
                    or (_interval_units > GRAPHS_INTERVAL_DAYS)):
                _interval_units = GRAPHS_INTERVAL_SECONDS
            self.interval = _interval * interval_multiplier[_interval_units]
            if ((_new_set_units < GRAPHS_INTERVAL_SECONDS)
                    or (_new_set_units > GRAPHS_INTERVAL_DAYS)):
                _new_set_units = GRAPHS_INTERVAL_SECONDS
            self.new_set_interval = _new_set_interval * interval_multiplier[_new_set_units]

    def _load_xml(self, obj):
        """Load the Statistics Output Settings from an ETree.SubElement."""
        settings = obj.find(StatisticsOutputSettings._tag_xml_root_name)
        if settings is not None:
            self.enabled = _is_attribute_enabled(settings, StatisticsOutputSettings.enabled)
            self.files_to_keep = int(settings.attrib.get(
                StatisticsOutputSettings._tag_xml_files_to_keep,
                StatisticsOutputSettings.files_to_keep))
            self.report_path = settings.attrib.get(
                StatisticsOutputSettings._tag_xml_report_path,
                StatisticsOutputSettings.report_path)
            self.report_type = settings.attrib.get(
                StatisticsOutputSettings._tag_xml_report_type,
                StatisticsOutputSettings.report_type)
            self.user_path = settings.attrib.get(
                StatisticsOutputSettings._tag_xml_user_path,
                StatisticsOutputSettings.user_path)
            self.option_notify = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_notify)
            self.option_align_new_set = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_align_new_set)
            self.option_align_output = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_align_output)
            self.option_new_set = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_new_set)
            self.option_scheduled = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_scheduled)
            self.option_keep_files = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_keep_files)
            self.option_reset_output = _is_attribute_enabled(
                settings, StatisticsOutputSettings._tag_xml_reset_output)

            _interval = int(settings.attrib.get(StatisticsOutputSettings._tag_xml_interval, 1))
            _units = int(settings.attrib.get(StatisticsOutputSettings._tag_xml_units, 3))
            if _units < GRAPHS_INTERVAL_SECONDS or _units > GRAPHS_INTERVAL_DAYS:
                _units = GRAPHS_INTERVAL_SECONDS
            self.interval = _interval * interval_multiplier[_units]

            _new_set_interval = int(
                settings.attrib.get(StatisticsOutputSettings._tag_xml_new_set_interval, 1))
            _new_set_units = int(
                settings.attrib.get(StatisticsOutputSettings._tag_xml_new_set_units, 4))
            if _new_set_units < GRAPHS_INTERVAL_SECONDS or _new_set_units > GRAPHS_INTERVAL_DAYS:
                _new_set_units = GRAPHS_INTERVAL_SECONDS
            self.new_set_interval = _new_set_interval * interval_multiplier[_new_set_units]

    def _store(self, props):
        """Store the Statistics Output Settings in a JSON props."""
        if not isinstance(props, dict) or not self.enabled:
            return
        _interval, _interval_units = _to_interval_units(self.interval)
        _new_set_interval, _new_set_units = _to_interval_units(self.new_set_interval)

        _props = {}
        _props[_json_enabled] = self.enabled
        _props[StatisticsOutputSettings._json_interval] = _interval
        _props[StatisticsOutputSettings._json_interval_units] = _interval_units
        _props[StatisticsOutputSettings._json_new_set_interval] = _new_set_interval
        _props[StatisticsOutputSettings._json_new_set_units] = _new_set_units
        _props[StatisticsOutputSettings._json_report_path] = self.report_path
        _props[StatisticsOutputSettings._json_report_type] = self.report_type
        _props[StatisticsOutputSettings._json_user_path] = self.user_path
        _props[StatisticsOutputSettings._json_notify] = self.option_notify
        _props[StatisticsOutputSettings._json_align_new_set] = self.option_align_new_set
        _props[StatisticsOutputSettings._json_align_output] = self.option_align_output
        _props[StatisticsOutputSettings._json_new_set] = self.option_new_set
        _props[StatisticsOutputSettings._json_scheduled] = self.option_scheduled
        _props[StatisticsOutputSettings._json_keep_files] = self.option_keep_files
        _props[StatisticsOutputSettings._json_reset_output] = self.option_reset_output
        _props[_json_classid] = _get_class_id(StatisticsOutputSettings._json_class_name)
        props[StatisticsOutputSettings._json_label] = _props


class StatisticsOutputPreferencesSettings(object):
    """The Statistics Output Preferences Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    _class_id = None
    """The Class Identifier of the object."""

    enabled = False
    """Are the Statistics Output Preferences Settings enabled?"""

    report_type = 3
    """The Report type. One of the REPORT TYPE constances."""

    # Tags
    _json_label = 'statsOutputPrefs'
    _json_class_name = 'StatsOutputPrefs'
    _json_report_type = 'reportType'

    _tag_label = 'StatsOutputPrefs'
    _tag_report_type = 'report_type'

    _stats_out_prefs_prop_dict = {
        _json_classid: _tag_classid,
        _tag_enabled: _tag_enabled,
        _json_report_type: _tag_report_type
    }

    def __init__(self):
        self.enabled = StatisticsOutputPreferencesSettings.enabled
        self.report_type = StatisticsOutputPreferencesSettings.report_type

    def _load(self, props):
        """Load the Statistics Output Preferences Settings from a
        Dictionairy.
        """
        if isinstance(props, dict):
            for k, v in props.items():
                a = StatisticsOutputPreferencesSettings._stats_out_prefs_prop_dict.get(k)
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == _tag_enabled:
                    self.enabled = v
                elif a == StatisticsOutputPreferencesSettings._tag_report_type:
                    self.report_type = int(v)

    def _load_xml(self, obj):
        """Load the Statistics Output Preferences Settings from an ETree.SubElement."""
        settings = obj.find(StatisticsOutputPreferencesSettings._tag_root_name)
        if settings is not None:
            self.enabled = _is_attribute_enabled(settings,
                                                 StatisticsOutputPreferencesSettings.enabled)
            self.report_type = int(settings.attrib.get(
                StatisticsOutputPreferencesSettings._tag_report_type,
                StatisticsOutputPreferencesSettings.report_type))

    def _store(self, props):
        """Store the Statistics Output Preferences Settings in a JSON
        props.
        """
        if not isinstance(props, dict) or not self.enabled:
            return
        _props = {}
        _props[_json_enabled] = self.enabled
        _props[_json_classid] = _get_class_id(
            StatisticsOutputPreferencesSettings._json_class_name)
        props[StatisticsOutputPreferencesSettings._json_label] = _props


class TriggerSettings(object):
    """The Trigger Settings section of a
    :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
    """

    class TriggerType(Enum):
        START = 1
        STOP = 2
        REPEAT = 3

    _class_id = None
    """The Class Identifier of the object."""

    _type = None
    """The type of Trigger: 0: Start, 1: Stop, 3: Repeat"""

    captured = None
    """The CaptureLimit of the Trigger. Initialized to a
    :class:`CaptureLimit <omniscript.capturetemplate.CaptureLimit>`
    object.
    """

    enabled = False
    """Is the trigger enabled."""

    filter = None
    """The Filter Limit of the Trigger. Initialized to a
    :class:`FilterLimit <omniscript.capturetemplate.FilterLimit>`
    object.
    """

    severity = Severity.INFORMATIONAL
    """The Severity of the the notification. One of the SEVERITY
    constants
    """

    time = None
    """The Date Limit of the Trigger. Initialized to a
    :class:`DateLimit <omniscript.capturetemplate.DateLimit>`
    object.
    """

    option_notify = True
    """Is notification enabled for when the Trigger triggers."""

    option_toggle_capture = True
    """Is Toggling the Capture when the Trigger triggers enabled?"""

    _label = None
    """The label of Trigger: either Start, Stop or Repeat Trigger."""

    _label_json = None
    """The json label of Trigger: either Start, Stop or Repeat Trigger."""

    # Tags
    _json_repeat = 'repeatTrigger'
    _json_start = 'startTrigger'
    _json_stop = 'stopTrigger'
    _json_notify = 'notify'
    _json_severity = 'severity'
    _json_toggle_capture = 'toggleCapture'
    _json_trigger_events = 'triggerEvents'

    _tag_class_name = 'Trigger'
    _tag_label_repeat = 'RepeatTrigger'
    _tag_label_start = 'StartTrigger'
    _tag_label_stop = 'StopTrigger'
    _tag_repeat = 'repeat'
    _tag_start = 'start'
    _tag_stop = 'stop'
    _tag_severity = 'severity'
    _tag_trigger_events = 'trigger_events'
    _tag_notify = 'option_notify'
    _tag_toggle_capture = 'option_toggle_capture'

    _tag_xml_events = "triggerevents"
    _tag_xml_event_obj = "triggereventobj"
    _tag_xml_notify = "notify"
    _tag_xml_root_name = "trigger"
    _tag_xml_severity = "severity"
    _tag_xml_toggle = "togglecapture"

    # Trigger Event Names
    _class_bytes_captured = "BytesCapturedTriggerEvent"
    _class_time = "TimeTriggerEvent"
    _class_flter = "FilterTriggerEvent"

    _trigger_prop_dict = {
        _json_classid: _tag_classid,
        _tag_enabled: _tag_enabled,
        _json_notify: _tag_notify,
        _json_severity: _tag_severity,
        _json_toggle_capture: _tag_toggle_capture,
        _json_trigger_events: _tag_trigger_events
    }

    _label_tag = {
        TriggerType.START: 'start',
        TriggerType.STOP: 'stop',
        TriggerType.REPEAT: 'repeat'
    }

    _label_json = {
        TriggerType.START: 'startTrigger',
        TriggerType.STOP: 'stopTrigger',
        TriggerType.REPEAT: 'repeatTrigger'
    }

    def __init__(self, trigger_type):
        self.enabled = TriggerSettings.enabled
        self.severity = TriggerSettings.severity
        self.captured = CaptureLimit()
        self.filter = FilterLimit()
        self.time = DateLimit()
        self.option_notify = TriggerSettings.option_notify
        self.option_toggle_capture = TriggerSettings.option_toggle_capture
        self._label = TriggerSettings._label_tag[trigger_type]
        self._label_json = TriggerSettings._label_json[trigger_type]

    def _load(self, props, engine):
        """Load the Trigger Settings from a dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = TriggerSettings._trigger_prop_dict.get(k)
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == _tag_enabled:
                    self.enabled = v
                elif a == TriggerSettings._tag_severity:
                    self.severity = Severity(v) if v in Severity else Severity.INFORMATIONAL
                elif a == TriggerSettings._tag_notify:
                    self.option_notify = v
                elif a == TriggerSettings._tag_toggle_capture:
                    self.option_toggle_capture = v
                elif a == TriggerSettings._tag_trigger_events:
                    if not isinstance(v, list):
                        continue
                    capture_class_id = _get_class_id(CaptureLimit._tag_class_name)
                    date_class_id = _get_class_id(DateLimit._tag_class_name)
                    filter_class_id = _get_class_id(FilterLimit._tag_class_name)
                    for limit in v:
                        if not isinstance(limit, dict):
                            continue
                        class_id = limit.get(_json_classid)
                        if class_id:
                            id = OmniId(class_id)
                            if id == capture_class_id:
                                self.captured._load(limit)
                            elif id == date_class_id:
                                self.time._load(limit)
                            elif id == filter_class_id:
                                self.filter._load(limit, engine)
                            else:
                                pass

    def _load_xml(self, obj, engine):
        """Load the Trigger Settings from an ETree SubElement."""
        self._name = obj.attrib[_tag_name]
        trigger = obj.find(TriggerSettings._tag_xml_root_name)
        self.enabled = _is_prop_enabled(trigger)
        self.option_notify = _is_attribute_enabled(
            trigger, TriggerSettings._tag_xml_notify)
        self.severity = int(trigger.attrib.get(
            TriggerSettings._tag_xml_severity, str(TriggerSettings.severity)))
        self.option_toggle_capture = _is_attribute_enabled(
            trigger, TriggerSettings._tag_xml_toggle)
        events = trigger.find(TriggerSettings._tag_xml_events)
        for ev_obj in events.findall(TriggerSettings._tag_xml_event_obj):
            class_name_ids = omniscript.get_class_name_ids()
            id = OmniId(ev_obj.attrib.get(_tag_classid))
            if id == class_name_ids[TriggerSettings._class_bytes_captured]:
                self.captured = CaptureLimit()
                self.captured._load(ev_obj)
            elif id == class_name_ids[TriggerSettings._class_time]:
                self.time = DateLimit()
                self.time._load(ev_obj)
            elif id == class_name_ids[TriggerSettings._class_flter]:
                self.filter = FilterLimit()
                self.filter._load(ev_obj, engine)

    def _store(self, props, engine):
        """Store the Trigger Settings into the ETree SubElement"""
        if not isinstance(props, dict):
            return
        _props = {}
        _props[_json_enabled] = self.enabled
        _props[TriggerSettings._json_notify] = self.option_notify
        _props[TriggerSettings._json_severity] = self.severity
        _props[TriggerSettings._json_toggle_capture] = self.option_toggle_capture
        if self.captured or self.filter or self.time:
            events = []
            if self.captured:
                events.append(self.captured._store())
            if self.filter:
                events.append(self.filter._store(engine))
            if self.time:
                events.append(self.time._store())
            _props[TriggerSettings._json_trigger_events] = events
        _props[_json_classid] = _get_class_id(TriggerSettings._tag_class_name)
        props[self._label_json] = _props


class CaptureTemplate(object):
    """Basic Capture Template class, defaults come from the Capture
    Template file. Load the Adapter, General and Filter settings from
    an existing capture template file. Modify the various settings.
    Then create the capture on an OmniEngine:
    engine.create_capture(template)
    """

    _class_id = None
    """The Class Identifier of the object."""

    adapter = None
    """The Adapter Settings of the capture. Initialized to a
    :class:`AdapterSettings <omniscript.capturetemplate.AdapterSettings>`
    object.
    """

    alarms = None
    """The Alarm Settings of the capture."""

    analysis = None
    """The Analysis Settings of the capture. Initialized to a
    :class:`AnalysisSettings <omniscript.capturetemplate.AnalysisSettings>`
    """

    filename = None
    """An optional file name of a Capture Template file."""

    filter = None
    """The list of enabled filters of the capture. Initialized to a
    :class:`FilterSettings <omniscript.capturetemplate.FilterSettings>`
    object.
    """

    general = None
    """The General Settings of the capture. Initialized to a
    :class:`GeneralSettings <omniscript.capturetemplate.GeneralSettings>`
    object.
    """

    graphs = None
    """The Graphs Settings of the capture. Initialized to a
    :class:`GraphsSettings <omniscript.capturetemplate.GraphsSettings>`
    object.
    """

    hardware = None
    """The Hardware Configuration of the capture. Initialized to a
    :class:`HardwareConfig <omniscript.capturetemplate.HardwareConfig>`
    object.
    """

    id = None
    """The
    :class:`OmniId <omniscript.omniid.OmniId>` of the template.
    """

    indexing = None
    """The Indexing Settings of the capture. Initialized to a
    :class:`IndexingSettings <omniscript.capturetemplate.IndexingSettings>`
    object.
    """

    plugins = None
    """The Analysis Modules of the capture. Initialized to a
    :class:`AnalysisModules <omniscript.capturetemplate.AnalysisModules>`
    object.
    """

    plugins_config = None
    """The list of Plugins (Analysis Modules) configuration."""

    repeat_trigger = None
    """The capture's Repeat Trigger option. Initialzed to None so that
    value is not set. Set this attribute to '1' to enable, or '0' to
    disable the Repeat Trigger option.
    """

    start_trigger = None
    """The Start Trigger of the capture. Initialized to a
    :class:`TriggerSettings <omniscript.capturetemplate.TriggerSettings>`
    object.
    """

    statistics_output = None
    """The Statistics Output settings of the capture. Initialized to a
    :class:`StatisticsOutputSettings <omniscript.capturetemplate.StatisticsOutputSettings>`
    object.
    """

    statistics_output_preferences = None
    """The Statistics Output settings of the capture. Initialized to a
    :class:`StatisticsOutputSettings <omniscript.capturetemplate.StatisticsOutputSettings>`
    object.
    """

    stop_trigger = None
    """The Stop Trigger of the capture. Initialized to a
    :class:`TriggerSettings <omniscript.capturetemplate.TriggerSettings>`
    object.
    """

    voip = None
    """The VoIP configuration
    :class:`VoIP Settings <omniscript.capturetemplate.VoIPSettings>`
    object.
    """

    find_attributes = ('name', 'id')

    _default_filename = False
    """Is the default capture template being used?"""

    _load_from = LOAD_FROM_NONE

    # Tags
    _json_plugins_config = 'pluginsConfig'

    _tag_adapter = 'adapter'
    _tag_template = 'template'
    _tag_alarms = 'alarms'
    _tag_analysis = 'analysis'
    _tag_filename = 'filename'
    _tag_filter = 'filter'
    _tag_general = 'general'
    _tag_graphs = 'graphs'
    _tag_hardware = 'hardware'
    _tag_indexing = 'indexing'
    _tag_plugins = 'plugins'
    _tag_plugins_config = 'plugins_config'
    _tag_repeat_trigger = 'repeat_trigger'
    _tag_start_trigger = 'start_trigger'
    _tag_statistics_output = 'statistics_output'
    _tag_statistics_output_preferences = 'statistics_output_preferences'
    _tag_stop_trigger = 'stop_trigger'
    _tag_voip = 'voip'

    _tag_xml_plugins_config = 'PluginsConfig'

    _template_prop_dict = {
        _json_classid: _tag_classid,
        AdapterSettings._json_label: _tag_adapter,
        AlarmSettings._json_label: _tag_alarms,
        AnalysisModules._json_label: _tag_plugins,
        AnalysisSettings._json_label: _tag_analysis,
        FilterSettings._json_label: _tag_filter,
        GeneralSettings._json_label: _tag_general,
        GraphsSettings._json_label: _tag_graphs,
        HardwareConfig._json_label: _tag_hardware,
        IndexingSettings._json_label: _tag_indexing,
        _json_plugins_config: _tag_plugins_config,
        StatisticsOutputSettings._json_label: _tag_statistics_output,
        StatisticsOutputPreferencesSettings._json_label:
            _tag_statistics_output_preferences,
        TriggerSettings._json_repeat: _tag_repeat_trigger,
        TriggerSettings._json_start: _tag_start_trigger,
        TriggerSettings._json_stop: _tag_stop_trigger,
        VoIPSettings._json_label: _tag_voip
    }

    def __init__(self, filename=None, props=None, engine=None):
        self._load_from = CaptureTemplate._load_from
        self.filename = filename
        if self.filename is not None and len(self.filename) == 0:
            self.filename = None
        # self.props = props
        self.adapter = AdapterSettings()
        self.alarms = AlarmSettings()
        self.analysis = AnalysisSettings()
        self.filter = FilterSettings()
        self.general = GeneralSettings()
        self.graphs = GraphsSettings()
        self.hardware = HardwareConfig()
        self.id = CaptureTemplate.id
        self.indexing = IndexingSettings()
        self.plugins = AnalysisModules()
        self.plugins_config = None
        self.repeat_trigger = CaptureTemplate.repeat_trigger
        self.start_trigger = TriggerSettings(TriggerSettings.TriggerType.START)
        self.statistics_output = StatisticsOutputSettings()
        self.statistics_output_preferences = StatisticsOutputPreferencesSettings()
        self.stop_trigger = TriggerSettings(TriggerSettings.TriggerType.STOP)
        self.voip = VoIPSettings()
        # if not self.filename:
        #     _dirname = os.path.dirname(omniscript.__file__)
        #     self.filename = os.path.join(_dirname, 'data', '_capture_template.xml')
        #     self._default_filename = True
        if self.filename is not None:
            tree = ET.parse(self.filename)
            file_props = _find_properties(tree)
            self.load_xml(file_props, engine)
            self._load_from = LOAD_FROM_FILE
        if props is not None:
            self._load(props, engine)
            self._load_from = LOAD_FROM_NODE

    def __repr__(self) -> str:
        return f'CaptureTemplate: {self.general.name} {self.id.format()}'

    def __str__(self) -> str:
        return f'CaptureTemplate: {self.general.name}'

    def _load(self, props, engine):
        if not isinstance(props, dict):
            return
        self.id = OmniId(props['id']) if 'id' in props else None
        self.type = props['type'] if 'type' in props else None
        self.clsid = props[_json_classid] if _json_classid in props else None
        template = (props[CaptureTemplate._tag_template]
                    if CaptureTemplate._tag_template in props
                    else props)
        if isinstance(template, dict):
            for k, v in template.items():
                a = CaptureTemplate._template_prop_dict.get(k)
                if a is None or not hasattr(self, a):
                    continue
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == CaptureTemplate._tag_adapter:
                    self.adapter._load(v)
                elif a == CaptureTemplate._tag_alarms:
                    self.alarms._load(v)
                elif a == CaptureTemplate._tag_analysis:
                    self.analysis._load(v)
                elif a == CaptureTemplate._tag_filter:
                    self.filter._load(v)
                elif a == CaptureTemplate._tag_general:
                    self.general._load(v)
                elif a == CaptureTemplate._tag_graphs:
                    self.graphs._load(v)
                elif a == CaptureTemplate._tag_hardware:
                    self.hardware._load(v)
                elif a == CaptureTemplate._tag_indexing:
                    self.indexing._load(v)
                elif a == CaptureTemplate._tag_plugins:
                    self.plugins._load(v, engine)
                elif a == CaptureTemplate._tag_plugins_config:
                    self.plugins_config = None
                elif a == CaptureTemplate._tag_repeat_trigger:
                    self.repeat_trigger = v
                elif a == CaptureTemplate._tag_start_trigger:
                    self.start_trigger._load(v, engine)
                elif a == CaptureTemplate._tag_statistics_output:
                    self.statistics_output._load(v)
                elif a == CaptureTemplate._tag_statistics_output_preferences:
                    self.statistics_output_preferences._load(v)
                elif a == CaptureTemplate._tag_stop_trigger:
                    self.stop_trigger._load(v, engine)
                elif a == CaptureTemplate._tag_voip:
                    self.voip._load(v)

    @property
    def name(self):
        """The Capture Template's name. (Read Only)"""
        return self.general.name

    def add_filter(self, omnifilter):
        """Add a filter to the capture template."""
        name = None
        if isinstance(omnifilter, six.string_types):
            name = omnifilter
        if isinstance(omnifilter, Filter):
            name = omnifilter.name
        if name is not None:
            if name not in self.filter.filters:
                self.filter.filters.append(name)

    # def add_filters(self, *filters):
    #     """Add filters to the capture template."""
    #     for item in filters:
    #         if isinstance(item, (list, tuple)):
    #             for f in item:
    #                 self.add_filters(f)
    #         else:
    #             self.add_filter(item)

    def load_xml(self, props, engine):
        if props is not None:
            for obj in props.findall(_tag_object):
                objName = obj.attrib[_tag_name]
                if objName == AdapterSettings._tag_label:
                    self.adapter._load_xml(obj)
                elif objName == AlarmSettings._tag_label:
                    self.alarms._load_xml(obj)
                elif objName == AnalysisSettings._tag_label:
                    self.analysis._load_xml(obj)
                elif objName == FilterSettings._tag_label:
                    self.filter._load_xml(obj)
                elif objName == GeneralSettings._tag_label:
                    self.general._load_xml(obj)
                elif objName == GraphsSettings._tag_label:
                    self.graphs._load_xml(obj)
                elif objName == IndexingSettings._tag_label:
                    self.indexing._load_xml(obj)
                elif objName == AnalysisModules._tag_label:
                    self.plugins._load_xml(obj, engine)
                elif objName == AnalysisSettings._tag_label:
                    self.plugins_config = None
                elif objName == TriggerSettings._tag_label_start:
                    if self.start_trigger is None:
                        self.start_trigger = TriggerSettings(CaptureTemplate._tag_start)
                    self.start_trigger._load_xml(obj, engine)
                elif objName == StatisticsOutputSettings._tag_label:
                    self.statistics_output._load_xml(obj)
                elif objName == TriggerSettings._tag_label_stop:
                    if self.stop_trigger is None:
                        self.stop_trigger = TriggerSettings(CaptureTemplate._tag_stop)
                    self.stop_trigger._load_xml(obj, engine)
                elif objName == VoIPSettings.get_label():
                    self.voip._load_xml(obj)
                elif objName == CaptureTemplate._tag_xml_plugins_config:
                    self.plugins._load_xml_config(obj, engine)
            for prop in props.findall(_tag_prop):
                propName = prop.attrib[_tag_name]
                if propName == TriggerSettings._tag_label_repeat:
                    self.repeat_trigger = int(prop.text)

    # def save(self, filename, engine=None):
    #     """Save the capture template to file."""
    #     f = open(filename, 'w')
    #     f.write(self.to_xml(engine, True))   #True: pretty print.
    #     f.close

    def set_adapter(self, value):
        """Set the adapter; only it's name/description is stored."""
        if isinstance(value, six.string_types):
            self.adapter.adapter_type = AdapterType.UNKNOWN
            self.adapter.name = value
        elif isinstance(value, Adapter):
            self.adapter.adapter_type = value.adapter_type
            self.adapter.name = value.name
        # elif isinstance(value, FileAdapter):
        #     self.adapter.adapter_type = AdapterType.FILE
        #     self.adapter.name = value.filename
        #     self.adapter.limit = value.limit
        #     self.adapter.mode = value.mode
        #     self.adapter.speed = value.speed

    def set_all(self, enable=True):
        """Set all analysis options, default is True.
        When True all Analysis Options are enabled, all plugins are
        enabled and all Timeline Stats are enabled.
        When False the above are all disabled.
        """
        self.analysis.set_all(enable)
        self.plugins.set_all(enable)
        self.general.set_timeline(enable)

    # def set_filters(self, filter_list):
    #     """Set the filters of the capture."""
    #     self.filter.filters = []
    #     self.add_filters(filter_list)

    # def set_multistream(self, enable=False):
    #     """Set the capture multistream."""
    #     self.general.set_multistream(enable)

    def set_repeat_trigger(self, value):
        """Set the Repeat Trigger option.

        Args:
            value(bool): will the start trigger repeat.
        """
        self.repeat_trigger = bool(value)

    def store(self, engine=None, new=False, encapsulate=False):
        """Return the Capture Template as a serialized JSON formatted
        string.
        """
        props = {}
        if engine:
            self.adapter._store(props, engine)
            self.filter._store(props, engine)
        self.alarms._store(props)
        self.analysis._store(props)
        self.general._store(props, new)
        self.graphs._store(props)
        self.hardware._store(props)
        self.indexing._store(props)
        self.plugins._store(props)
        if self.plugins_config:
            self.plugins_config._store(props)
        if self.repeat_trigger is not None:
            props[TriggerSettings._json_repeat] = True if self.repeat_trigger else False
        if self.start_trigger:
            self.start_trigger._store(props, engine)
        self.statistics_output._store(props)
        self.statistics_output_preferences._store(props)
        if self.stop_trigger:
            self.stop_trigger._store(props, engine)
        if self.voip:
            props[VoIPSettings._json_label] = self.voip._get_props()

        if encapsulate:
            props['type'] = 1
            template = {
                'clsid': _get_class_id('CaptureTemplateItem'),
                'id': OmniId(True).format(),
                'template': props
            }
            return json.dumps(template)
        else:
            return json.dumps(props)

    # def to_xml(self, engine=None, new=False, pretty=False, modify=False):
    #     """Return the Capture Template encoded in XML as a string."""
    #     if self._load_from == LOAD_FROM_FILE or self._load_from == LOAD_FROM_NONE:
    #         if self._default_filename and engine:
    #             _dirname = os.path.dirname(omniscript.__file__)
    #             hp = engine.get_host_platform()
    #             if hp and hp.os == omniscript.OPERATING_SYSTEM_LINUX:
    #                 _filename = os.path.join(_dirname, '_capture_template_linux.xml')
    #             else:
    #                 _filename = os.path.join(_dirname, '_capture_template_windows.xml')
    #         else:
    #             _filename = self.filename
    #         with open(_filename, 'r') as xmlfile:
    #             xml = xmlfile.read().replace('\n', '').replace('\t', '')

    #     if new:
    #         self.general.id = OmniId(True)

    #     if self._load_from == LOAD_FROM_NODE and self.node is not None:
    #         props = self.node
    #     else:
    #         template = ET.fromstring(xml)
    #         props = _find_properties(template)

    #     for obj in props.findall(_tag_object):
    #         objName = obj.attrib[_tag_name]
    #         if objName == CaptureTemplate._tag_adapter:
    #             self.adapter._store(obj, engine)
    #         #elif objName == CaptureTemplate._tag_alarms:
    #         #    self.alarms._store(obj)
    #         elif objName == CaptureTemplate._tag_analysis:
    #             self.analysis._store(obj)
    #         elif objName == CaptureTemplate._tag_filter:
    #             self.filter._store(obj, engine)
    #         elif objName == CaptureTemplate._tag_general:
    #             self.general._store(obj)
    #         elif objName == CaptureTemplate._tag_graphs:
    #             self.graphs._store(obj)
    #         elif objName == CaptureTemplate._tag_indexing:
    #             self.indexing._store(obj)
    #         elif objName == CaptureTemplate._tag_plugins:
    #             self.plugins._store(obj, engine, self.analysis.option_compass)
    #         elif objName == CaptureTemplate._tag_start and self.start_trigger is not None:
    #             self.start_trigger._store(obj, engine)
    #         elif objName == CaptureTemplate._tag_stop and self.stop_trigger is not None:
    #             self.stop_trigger._store(obj, engine)
    #     if self.repeat_trigger is not None:
    #         _set_property(props, CaptureTemplate._tag_repeat, 22,
    #                 int(self.repeat_trigger))

    #     #template = ET.Element('capturetemplate', {'version':'1.0'})
    #     #props = ET.SubElement(template, 'properties')
    #     #self.adapter._store(ET.SubElement(props, 'obj'), engine)
    #     #self.alarms._store(ET.SubElement(props, 'obj'))
    #     #self.analysis._store(ET.SubElement(props, 'obj'))
    #     #self.filter._store(ET.SubElement(props, 'obj'), engine)
    #     #self.general._store(ET.SubElement(props, 'obj'))
    #     #self.graphs._store(ET.SubElement(props, 'obj'))
    #     #self.start_trigger._store(ET.SubElement(props, 'obj'), engine)
    #     #self.statistics_output._store(ET.SubElement(props, 'obj'))
    #     #self.stop_trigger._store(ET.SubElement(props, 'obj'), engine)
    #     #self.voip._store(ET.SubElement(props, 'obj'))
    #     #
    #     #_set_property(props, CaptureTemplate._tag_repeat, '22',
    #     #              self.repeat_trigger)

    #     if modify:
    #         mod = ET.Element(_tag_props)
    #         obj = ET.SubElement(mod, _tag_object)
    #         _set_label_clsid(obj, 'options', _tag_prop_bag)
    #         _set_property(mod, _tag_id, 8, str(self.general.id))
    #         obj.append(props)
    #         props = mod

    #     if props is None:
    #         raise OmniError('Failed to create CaptureTemplate')
    #     return ET.tostring(props).replace('\n', '')


def _create_capture_template_list(engine, resp):
    lst = []
    templates = resp['templates']
    if templates is not None:
        for props in templates:
            lst.append(CaptureTemplate(None, props, engine))
    # lst.sort(key=lambda x: x.description)
    return lst


def find_capture_template(templates, value, attrib=CaptureTemplate.find_attributes[0]):
    """Finds a Capture Template in the list"""
    if (not templates) or (attrib not in CaptureTemplate.find_attributes):
        return None

    if len(templates) == 0:
        return None

    if isinstance(value, CaptureTemplate):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    t = next((i for i in templates if getattr(i.general, attrib) == _value), None)
    return t

# def get_graph_template_names():
#     """ Returns the list of Graph Template Names."""
#     id_graph_names = omniscript.get_id_graph_names()
#     return id_graph_names.values() if id_graph_names is not None else None

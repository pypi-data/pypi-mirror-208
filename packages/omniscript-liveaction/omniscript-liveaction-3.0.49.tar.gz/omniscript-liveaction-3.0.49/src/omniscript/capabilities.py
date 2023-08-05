"""Capabilities class.
"""
# Copyright (c) LiveAction, Inc. 2023. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

# from typing import Union

from .invariant import PacketFileIndexing, VariantType
from .omniid import OmniId
from .helpers import (
    create_object_list, load_native_props_from_dict, repr_array, str_array, load_props_from_dict)


# Global JSON tags
_json_id = 'id'
_json_name = 'name'


class AdministratorDefaults(object):
    """The AdministratorDefaults class has the attributes of engine admin defaults."""

    id = OmniId()
    """Id."""

    value = 0
    """Value."""

    def __init__(self, props=None):
        self.id = AdministratorDefaults.id
        self.value = AdministratorDefaults.value
        self._load(props)

    def __repr__(self):
        return (
            f'AdministratorDefaults({{'
            f'id: "{self.id}", '
            f'value: {self.value}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Administrator Defaults: '
            f'id="{self.id}", '
            f'value={self.value}'
        )

    def _load(self, props):
        """Load attributes from a dictionary."""
        if isinstance(props, dict):
            for k, v in props.items():
                if k == _json_id:
                    self.id = OmniId(v)
                elif k == _json_name:
                    self.name = str(v) if v else ''


class PacketFileIndex(object):
    """The PacketFileIndex class has the attributes of an engine packet file index."""

    id = PacketFileIndexing.IPV4
    """Index id."""

    name = ''
    """Index name."""

    def __init__(self, props=None):
        self.id = PacketFileIndex.id
        self.name = PacketFileIndex.name
        self._load(props)

    def __repr__(self):
        return (
            f'PacketFileIndex({{'
            f'id: {self.id}, '
            f'name: "{self.name}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Packet File Index: '
            f'id={self.id}, '
            f'name="{self.name}"'
        )

    def _load(self, props):
        """Load attributes from a dictionary."""
        if isinstance(props, dict):
            for k, v in props.items():
                if k == _json_id:
                    if isinstance(v, int):
                        self.id = (PacketFileIndexing(v)
                                   if v < len(PacketFileIndexing) else PacketFileIndexing.IPV4)
                elif k == _json_name:
                    self.name = str(v) if v else ''


_performance_item_dict = {
    'cost': 'cost',
    'name': 'name',
    'statisticLimit': 'has_limit'
}


class PerformanceItem(object):
    """The PerformanceItem class has the attributes of an engine performance item."""

    cost = 50
    """Performance percentage."""

    name = ''
    """Performance item name."""

    has_limit = False
    """Whether there is a statistical limit."""

    def __init__(self, props=None):
        self._load(props)

    def __repr__(self):
        return (
            f'PerformanceItem({{'
            f'name: "{self.name}", '
            f'cost: {self.cost}, '
            f'has_limit: {self.has_limit}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Performance Item: '
            f'Name="{self.name}", '
            f'Cost %={self.cost}, '
            f'Has Statistics Limit={self.has_limit}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _performance_item_dict)


_option_item_dict = {
    'description': 'description',
    'maximum': 'maximum',
    'minimum': 'minimum',
    'name': 'name',
    'value': 'value'
}


class OptionItem(object):
    """The OptionItem class has the attributes of an engine option."""

    description = ''
    """Option description."""

    maximum = 0
    """Maximum value."""

    minimum = 0
    """Minimum value."""

    name = ''
    """Option name."""

    option_list = []
    """List of options."""

    type = VariantType.EMPTY
    """Option type."""

    value = 0
    """Value."""

    def __init__(self, props=None):
        self._load(props)

    def __repr__(self):
        return (
            f'OptionItem({{'
            f'description: "{self.description}", '
            f'maximum: {self.maximum}, '
            f'minimum: {self.minimum}, '
            f'name: "{self.name}", '
            f'options: [{repr_array(self.options)}], '
            f'type: {self.type}, '
            f'value: {self.value}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Option Item: '
            f'description="{self.description}", '
            f'maximum={self.maximum}, '
            f'minimum={self.minimum}, '
            f'name="{self.name}", '
            f'options=[{str_array(self.options)}], '
            f'type={self.type}, '
            f'value={self.value}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _option_item_dict)

        if isinstance(props, dict):
            options = None
            if 'options' in props:
                options = props['options']
            if isinstance(options, list):
                self.options = []
                for v in options:
                    self.options.append(v)

            variantType = props['type']
            if isinstance(variantType, int):
                self.type = variantType if variantType in VariantType else VariantType.EMPTY


_plugin_info_dict = {
    'clsid': 'id',
    'file': 'file',
    'name': 'name',
    'publisher': 'publisher',
    'version': 'version'
}

_plugin_features_dict = {
    'handlerId': 'handler_id',
    'options': 'has_options',
    'options2': 'has_extended_options',
    'packetSummary': 'has_packet_summary',
    'pluginAdapter': 'is_plugin_adapter',
    'processPackets': 'has_process_packets',
    'summaryStatistics': 'has_summary_statistics'
}

_json_category_id_list = 'categoryIds'
_json_default_option_list = 'defaultOptions'
_json_features = 'features'


class PluginInformation(object):
    """The PluginInformation class has the attributes of engine plugin."""

    category_id_list = []
    """List of plugin category ids."""

    default_option_list = None
    """Default plugin options."""

    file = ''
    """Path to plugin file."""

    handler_id = OmniId()
    """Plugin handler id."""

    has_options = False
    """Whether plugin has options."""

    has_extended_options = False
    """Whether plugin has extended options."""

    has_packet_summary = False
    """Whether plugin has packet summaries."""

    has_process_packets = False
    """Whether plugin has processes packet."""

    has_summary_statistics = False
    """Whether plugin has summary statistics."""

    is_adapter = False
    """Whether plugin is an adapter."""

    is_filter = False
    """Whether plugin filters packets."""

    name = ''
    """Plugin name."""

    publisher = ''
    """Plugin publisher."""

    version = ''
    """Plugin version."""

    def __init__(self, props=None):
        self.id = PluginInformation.handler_id
        self.has_options = PluginInformation.has_options
        self.has_extended_options = PluginInformation.has_extended_options
        self.has_packet_summary = PluginInformation.has_packet_summary
        self.has_process_packets = PluginInformation.has_process_packets
        self.has_summary_statistics = PluginInformation.has_summary_statistics
        self.is_adapter = PluginInformation.is_adapter
        self.is_filter = PluginInformation.is_filter
        self._load(props)

    def __repr__(self):
        return (
            f'PluginInfo({{'
            f'category_id_list: [{repr_array(self.category_id_list)}], '
            f'default_option_list: {{{repr(self.default_option_list)}}}, '
            f'file: "{self.file}", '
            f'handler_id: "{self.handler_id}", '
            f'has_options: {self.has_options}, '
            f'has_extended_options: {self.has_extended_options}, '
            f'has_packet_summary: {self.has_packet_summary}, '
            f'has_process_packets: {self.has_process_packets}, '
            f'has_summary_statistics: {self.has_summary_statistics}'
            f'is_adapter: {self.is_adapter}, '
            f'is_filter: {self.is_filter}, '
            f'name: "{self.name}", '
            f'publisher: "{self.publisher}", '
            f'version: "{self.version}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Plugin Info: '
            f'category_id_list=[{str_array(self.category_id_list)}], '
            f'default_option_list=[{str_array(self.default_option_list)}], '
            f'file="{self.file}", '
            f'Handler Id="{self.handler_id}", '
            f'Has options={self.has_options}, '
            f'Has Extended Options={self.has_extended_options}, '
            f'Has Packet Summary={self.has_packet_summary}, '
            f'Has Process Packets={self.has_process_packets}, '
            f'Has Summary Statistics={self.has_summary_statistics}, '
            f'Is Adapter={self.is_adapter}, '
            f'Is filter={self.is_filter} '
            f'name="{self.name}", '
            f'publisher="{self.publisher}", '
            f'version="{self.version}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _plugin_info_dict)

        if isinstance(props, dict):
            id_props = props.get(_json_category_id_list)
            self.category_id_list = create_object_list(id_props, OmniId)

            option_props = props.get(_json_default_option_list)
            self.default_option_list = create_object_list(option_props, OptionItem)

            features = props.get(_json_features)
            if isinstance(features, dict):
                load_native_props_from_dict(self, features, _plugin_features_dict)


class UserRights(object):
    """The UserRights class has the attributes of engine user rights."""

    policies = []
    """List of engine policies."""

    def __init__(self, props=None):
        self._load(props)

    def __repr__(self):
        return (
            f'UserRights({{'
            f'policies: [{repr_array(self.policies)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'User Rights: '
            f'policies=[{str_array(self.policies)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            policies = None
            if 'policies' in props:
                policies = props['policies']
            if isinstance(policies, list):
                self.policies = []
                for v in policies:
                    self.policies.append(v)


_json_activation_information = 'activationInfo'
_json_activation_information = 'activationInfo'
_json_administrator_default_list = 'adminDefaults'
_json_capability_list = 'capabilities'
_json_maximum_capture_count = 'maximumCaptureCount'
_json_packet_file_index_list = 'packetFileIndexes'
_json_performance = 'performance'
_json_performance_item_list = 'performanceItems'
_json_plugin_list = 'plugins'
_json_plugin_information_list = 'pluginsInfo'
_json_user_rights = 'userRights'
_json_policies = 'policies'


# Activation Information
# Don't include max capture count, it can be None
_capabilities_dict = {
    'capabilities': 'capabilities',
    'majorVersion': 'major_version',
    'minorVersion': 'minor_version',
    'product': 'product_id'
}


class Capabilities(object):
    """The Capabilities class has the attributes of engine capabilities."""

    capabilities = ''
    """Engine capabilities in bitmask form."""

    major_version = 0
    """Major engine version number."""

    maximum_capture_count = None
    """Maximum capture count."""

    minor_version = 0
    """Minor engine version number."""

    product_id = 0
    """Product id."""

    administrator_default_list = []
    """List of administrator defaults."""

    capability_list = []
    """List of capabilities ids."""

    packet_file_index_list = []
    """List of packet file indicies."""

    performance_item_list = []
    """List of Performance items."""

    plugin_id_list = []
    """List of Plugins ids."""

    plugin_information_list = []
    """Plugins information list."""

    policy_id_list = []
    """List of User rights policy ids."""

    def __init__(self, props=None):
        self.capabilities = Capabilities.capabilities
        self.major_version = Capabilities.major_version
        self.maximum_capture_count = Capabilities.maximum_capture_count
        self.minor_version = Capabilities. minor_version
        self.product_id = Capabilities.product_id
        self.administrator_default_list = Capabilities.administrator_default_list
        self.capability_list = Capabilities.capability_list
        self.packet_file_index_list = Capabilities.packet_file_index_list
        self.performance_item_list = Capabilities.performance_item_list
        self.plugin_id_list = Capabilities.plugin_id_list
        self.plugin_information_list = Capabilities.plugin_information_list
        self.policy_id_list = Capabilities.policy_id_list
        self._load(props)

    def __repr__(self):
        return (
            f'Capabilities({{'
            f'capabilities: {self.capabilities}, '
            f'maximum_capture_count: {self.maximum_capture_count}, '
            f'major_version: {self.major_version}, '
            f'minor_version: {self.minor_version}, '
            f'product_id: {self.product_id}, '
            f'administrator_default_list: [{repr_array(self.administrator_default_list)}], '
            f'capability_list: [{repr_array(self.capability_list)}], '
            f'packet_file_index_list: [{repr_array(self.packet_file_index_list)}], '
            f'performance_item_list: [{repr_array(self.performance_item_list)}], '
            f'plugin_id_list: [{repr_array(self.plugin_id_list)}], '
            f'plugin_infomation_list: [{repr_array(self.plugin_information_list)}], '
            f'policy_id_list: {{{repr(self.policy_id_list)}}}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Capabilities: '
            f'Capabilities={self.capabilities}, '
            f'Maximum Capture Count={self.maximum_capture_count}, '
            f'Major Version={self.major_version}, '
            f'Minor Version={self.minor_version}, '
            f'Product Id={self.product_id}, '
            f'Administrator Default List=[{str_array(self.administrator_default_list)}], '
            f'Capability List=[{str_array(self.capability_list)}], '
            f'Packet File Index List=[{str_array(self.packet_file_index_list)}], '
            f'Performance Item List=[{str_array(self.performance_item_list)}], '
            f'Plugin Id List=[{str_array(self.plugin_id_list)}], '
            f'Plugin Information List=[{str_array(self.plugin_information_list)}], '
            f'User Policy Id List={{{str(self.policy_id_list)}}}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            max_count = props.get(_json_maximum_capture_count)
            if isinstance(max_count, int):
                self.maximum_capture_count = max_count

            activation_props = props.get(_json_activation_information)
            load_native_props_from_dict(self, activation_props, _capabilities_dict)

            admin_props = props.get(_json_administrator_default_list)
            self.administrator_default_list = create_object_list(admin_props, AdministratorDefaults)

            cap_props = props.get(_json_capability_list)
            self.capability_list = create_object_list(cap_props, OmniId)

            index_props = props.get(_json_packet_file_index_list)
            self.packet_file_index_list = create_object_list(index_props, PacketFileIndex)

            perf_props = props.get(_json_performance)
            if isinstance(perf_props, dict):
                perf_item_props = perf_props.get(_json_performance_item_list)
                self.performance_item_list = create_object_list(perf_item_props, PerformanceItem)

            plugin_props = props.get(_json_plugin_list)
            self.plugin_id_list = create_object_list(plugin_props, OmniId)

            info_props = props.get(_json_plugin_information_list)
            self.plugin_information_list = create_object_list(info_props, PluginInformation)

            rights_props = props.get(_json_user_rights)
            if isinstance(rights_props, dict):
                policy_props = rights_props.get(_json_policies)
                self.policy_id_list = create_object_list(policy_props, OmniId)

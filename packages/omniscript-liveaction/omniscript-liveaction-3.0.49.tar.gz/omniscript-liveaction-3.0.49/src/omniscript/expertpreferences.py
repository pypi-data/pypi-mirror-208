"""ExpertPreferences class.
"""
# Copyright (c) LiveAction, Inc. 2023. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .invariant import (
    AuthenticationType, EncryptionProtocolType, ExpertProblemId, ExpertSensitivity, ExpertSeverity,
    ExpertSettingGroupId, ProtocolLayer, TimeUnit)
from .omniaddress import EthernetAddress
from .omniid import OmniId
from .helpers import (
    create_object_list, load_native_props_from_dict, load_native_props_from_list, str_array,
    repr_array)


_json_accept = 'accept'
_json_enabled = 'enabled'
_json_items = 'items'
_json_name = 'name'
_json_type = 'type'
_json_value = 'value'


class AuthenticaitonProtocol(object):
    """The AuthenticaitonProtocol class has an Authentication Protocol."""

    enabled = False
    """Whether enabled."""

    protocol = AuthenticationType.NONE
    """Expert policy authentication id."""

    def __init__(self, props):
        self.enabled = AuthenticaitonProtocol.enabled
        self.protocol = AuthenticaitonProtocol.protocol
        self._load(props)

    def __repr__(self):
        return (
            f'AuthenticaitonProtocol({{'
            f'enabled: {self.enabled}, '
            f'protocol: {self.protocol}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Authenticaiton Protocol: '
            f'enabled={self.enabled}, '
            f'protocol={self.protocol}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            enabled = props.get(_json_enabled)
            if isinstance(enabled, bool):
                self.enabled = bool(enabled)

            protocol = props.get(_json_type)
            if isinstance(protocol, int):
                self.protocol = (AuthenticationType(protocol)
                                 if protocol in AuthenticationType else AuthenticationType.NONE)


class EncryptionProtocol(object):
    """The EncryptionProtocol class has the attributes of an expert policy encryption item."""

    enabled = False
    """Whether this encryption policy is enabled."""

    protocol = EncryptionProtocolType.NONE
    """Encryption type."""

    def __init__(self, props):
        self.enabled = EncryptionProtocol.enabled
        self.protocol = EncryptionProtocol.protocol
        self._load(props)

    def __repr__(self):
        return (
            f'EncryptionProtocol({{'
            f'enabled: {self.enabled}, '
            f'protocol: {self.protocol}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Encryption Protocol: '
            f'enabled={self.enabled}, '
            f'protocol={self.protocol}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            enabled = props.get(_json_enabled)
            if isinstance(enabled, bool):
                self.enabled = bool(enabled)

            protocol = props.get(_json_type)
            if isinstance(protocol, int):
                self.protocol = (EncryptionProtocolType(protocol)
                                 if protocol in EncryptionProtocolType
                                 else EncryptionProtocolType.NONE)


_expert_description_dict = {
    'group': 'group',
    # 'guid': 'id',
    'hasConfigure': 'has_configure',
    'hasMinSamplePeriod': 'has_minimum_sample_period',
    'hasSensitivity': 'has_sensitivity',
    'hasValue': 'has_value',
    'hasValueAssist': 'has_value_assist',
    'valueAssistLogScale': 'has_value_assist_log_scale',
    'layer': 'layer',
    'message': 'message',
    'minSamplePeriodMax': 'minimum_sample_period_maximum',
    'minSamplePeriodMin': 'minimum_sample_period_minimum',
    'name': 'name',
    # 'problemId': 'problem_id',
    'subGroup': 'sub_group',
    'valueAssistLeft': 'value_assist_left',
    'valueAssistRight': 'value_assist_right',
    'valueDisplayFormat': 'value_display_format',
    'valueDisplayMultiplier': 'value_display_multiplier',
    'valueMax': 'value_maximum',
    'valueMin': 'value_minimum',
    'valueUnits': 'value_units'
}


class ExpertDescription(object):
    """The ExpertDescription class has the attributes of an expert description."""

    group = ''
    """Expert's group."""

    id = None
    """Expert's Id."""

    has_configure = False
    """Whether configuration is enabled."""

    has_minimum_sample_period = False
    """Whether minimum sample period is enabled."""

    has_sensitivity = False
    """Whether sensitivity is enabled."""

    has_value = False
    """Whether value is enabled."""

    has_value_assist = False
    """Whether value assist is enabled."""

    has_value_assist_log_scale = False
    """Whether value assist log scale."""

    layer = ProtocolLayer.UNKNOWN
    """Procol layer."""

    message = ''
    """Expert message."""

    minimum_sample_period_maximum = 0
    """Minimum sample period maximum."""

    minimum_sample_period_minimum = 0
    """Minimum sample period minimum."""

    minimum_sample_period_units = TimeUnit.NONE
    """Minimum sample period units."""

    name = ''
    """Expert name."""

    problem_id = ExpertProblemId.NONE
    """Expert problem type."""

    sub_group = ''
    """Expert sub group."""

    value_assist_left = 0
    """Left value assist."""

    value_assist_right = 0
    """Right value assist."""

    value_display_format = ''
    """Value display format."""

    value_display_multiplier = 0.0
    """Value display multiplier."""

    value_maximum = 0
    """Maximum value."""

    value_minimum = 0
    """Minimum value."""

    value_units = ''
    """Value units."""

    def __init__(self, props):
        self.group = ExpertDescription.group
        self.id = ExpertDescription.id
        self.has_configure = ExpertDescription.has_configure
        self.has_minimum_sample_period = ExpertDescription.has_minimum_sample_period
        self.has_sensitivity = ExpertDescription.has_sensitivity
        self.has_value = ExpertDescription.has_value
        self.has_value_assist = ExpertDescription.has_value_assist
        self.has_value_assist_log_scale = ExpertDescription.has_value_assist_log_scale
        self.layer = ExpertDescription.layer
        self.message = ExpertDescription.message
        self.minimum_sample_period_maximum = ExpertDescription.minimum_sample_period_maximum
        self.minimum_sample_period_minimum = ExpertDescription.minimum_sample_period_minimum
        self.minimum_sample_period_units = ExpertDescription.minimum_sample_period_units
        self.name = ExpertDescription.name
        self.problem_id = ExpertDescription.problem_id
        self.sub_group = ExpertDescription.sub_group
        self.value_assist_left = ExpertDescription.value_assist_left
        self.value_assist_right = ExpertDescription.value_assist_right
        self.value_display_format = ExpertDescription.value_display_format
        self.value_display_multiplier = ExpertDescription.value_display_multiplier
        self.value_maximum = ExpertDescription.value_maximum
        self.value_minimun = ExpertDescription.value_minimum
        self.value_units = ExpertDescription.value_units
        self._load(props)

    def __repr__(self):
        return (
            f'ExpertDescription({{'
            f'group: "{self.group}", '
            f'id: "{self.id}", '
            f'has_configure: {self.has_configure}, '
            f'has_minimum_sample_period: {self.has_minimum_sample_period}, '
            f'has_sensitivity: {self.has_sensitivity}, '
            f'has_value: {self.has_value}, '
            f'has_value_assist: {self.has_value_assist}, '
            f'has_value_assist_log_scale: {self.has_value_assist_log_scale}, '
            f'layer: {self.layer}, '
            f'message: "{self.message}", '
            f'minimum_sample_period_maximum: {self.minimum_sample_period_maximum}, '
            f'minimum_sample_period_minimum: {self.minimum_sample_period_minimum}, '
            f'minimum_sample_period_units: {self.minimum_sample_period_units}, '
            f'name: "{self.name}", '
            f'problem_id: {self.problem_id}, '
            f'sub_group: "{self.sub_group}", '
            f'value_assist_left: {self.value_assist_left}, '
            f'value_assist_right: {self.value_assist_right}, '
            f'value_display_format: "{self.value_display_format}", '
            f'value_display_multiplier: {self.value_display_multiplier}, '
            f'value_maximum: {self.value_maximum}, '
            f'value_minimun: {self.value_minimum}, '
            f'value_units: "{self.value_units}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Expert Description: '
            f'group="{self.group}", '
            f'id="{self.id}", '
            f'has_configure={self.has_configure}, '
            f'has_min_sample_period={self.has_minimum_sample_period}, '
            f'has_sensitivity={self.has_sensitivity}, '
            f'has_value={self.has_value}, '
            f'has_value_assist={self.has_value_assist}, '
            f'has_value_assist_log_scale={self.has_value_assist_log_scale}, '
            f'layer={self.layer}, '
            f'message="{self.message}", '
            f'min_sample_period_max={self.minimum_sample_period_maximum}, '
            f'min_sample_period_min={self.minimum_sample_period_minimum}, '
            f'min_sample_period_units={self.minimum_sample_period_units}, '
            f'name="{self.name}", '
            f'problem_id={self.problem_id}, '
            f'sub_group="{self.sub_group}", '
            f'value_assist_left={self.value_assist_left}, '
            f'value_assist_right={self.value_assist_right}, '
            f'value_display_format="{self.value_display_format}", '
            f'value_display_multiplier={self.value_display_multiplier}, '
            f'value_max={self.value_maximum}, '
            f'value_min={self.value_minimum}, '
            f'value_units="{self.value_units}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _expert_description_dict)

        if isinstance(props, dict):
            id = props.get('guid')
            if isinstance(id, six.string_types):
                self.id = OmniId(id)

            layer = props.get('layer')
            if isinstance(layer, int):
                self.layer = (ProtocolLayer(layer) if layer in ProtocolLayer
                              else ProtocolLayer.UNKNOWN)

            units = props.get('minSamplePeriodUnits')
            if isinstance(units, int):
                self.minSamplePeriodUnits = TimeUnit(units) if units in TimeUnit else TimeUnit.NONE

            id = props.get('problemId')
            if isinstance(id, int):
                self.problem_id = (ExpertProblemId(id)
                                   if id in ExpertProblemId else ExpertProblemId.NONE)


class ExpertEvent(object):
    """The ExpertEvent class has the attributes of an expert string table."""

    name = ''
    """Name of the event"""

    default = None
    """Default value of the event."""

    label_map = {}
    """Dictionary of event value to its label. dict{value#: 'label'}
    """

    def __init__(self, props):
        self.name = ExpertEvent.name
        self.default = ExpertEvent.default
        self.label_map = ExpertEvent.label_map
        self._load(props)

    def __repr__(self):
        return (
            f'ExpertEvent({{'
            f'name: "{self.name}", '
            f'default: {{{repr(self.default)}}}, '
            f'label_map: [{repr_array(self.label_map)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Expert Event: '
            f'name="{self.name}", '
            f'default={{{str(self.default)}}}, '
            f'label_map=[{str_array(self.label_map)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            name = props.get('id')
            if isinstance(name, six.string_types):
                self.name = str(name) if name else ''

            default = props.get('defaultValue')
            if isinstance(default, dict):
                k = default.get('id')
                v = default.get(_json_value)
                self.default = {k: v}

            values = props.get('values')
            if isinstance(values, list):
                self.label_map = {}
                for i in values:
                    if isinstance(i, dict):
                        k = i.get('id')
                        v = i.get(_json_value)
                        self.label_map[k] = v


class ExpertProblem(object):
    """The ExpertProblem class has the attributes of an expert problem."""

    enabled = False
    """Whether problem is enabled."""

    id = ExpertProblemId.NONE
    """Problem Id."""

    minimum_sample = None
    """Minimum sample."""

    sensitivity = ExpertSensitivity.NONE
    """Sensitivity."""

    setting_group_id = ExpertSettingGroupId.CURRENT
    """Group ID."""

    severity = ExpertSeverity.NONE
    """Severity."""

    value = None
    """Value."""

    def __init__(self, props):
        self.enabled = ExpertProblem.enabled
        self.id = ExpertProblem.id
        self.minimum_sample = ExpertProblem.minimum_sample
        self.sensitivity = ExpertProblem.sensitivity
        self.setting_group_id = ExpertProblem.setting_group_id
        self.severity = ExpertProblem.severity
        self.value = ExpertProblem.value
        self._load(props)

    def __repr__(self):
        return (
            f'ExpertProblem({{'
            f'enabled: {self.enabled}, '
            f'id: {self.id}, '
            f'minimum_sample: {self.minimum_sample}, '
            f'sensitivity: {self.sensitivity}, '
            f'setting_group_id: {self.setting_group_id}, '
            f'severity: {self.severity}, '
            f'value: {self.value}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Expert Problem: '
            f'enabled={self.enabled}, '
            f'id={self.id}, '
            f'minimum_sample={self.minimum_sample}, '
            f'sensitivity={self.sensitivity}, '
            f'setting_group_id={self.setting_group_id}, '
            f'severity={self.severity}, '
            f'value={self.value}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            enabled = props.get(_json_enabled)
            if enabled is not None:
                self.enabled = bool(enabled)

            id = props.get('id')
            if isinstance(id, int):
                self.id = ExpertProblem(id) if id in ExpertProblemId else ExpertProblemId.NONE

            minimum = props.get('minimumSample')
            if isinstance(minimum, int):
                self.minimum_sample = int(minimum)

            sensitivity = props.get('sensitivity')
            if isinstance(sensitivity, int):
                self.sensitivity = (ExpertSensitivity(sensitivity)
                                    if sensitivity in ExpertSensitivity else None)

            group_id = props.get('settingGroupId')
            if isinstance(group_id, int):
                self.settingGroupId = (
                    ExpertSettingGroupId(group_id) if group_id in ExpertSettingGroupId
                    else ExpertSettingGroupId.CURRENT)

            severity = props.get('severity')
            if isinstance(severity, int):
                self.severity = (ExpertSeverity(severity)
                                 if severity in ExpertSeverity else ExpertSeverity.NONE)

            value = props.get(_json_value)
            if isinstance(value, int):
                self.value = int(value)


class ExpertSettings(object):
    """The ExpertSettings class has the attributes of an expert settings."""

    maximum_stream_count = 0
    """Maximum stream count."""

    wireless_policy = None
    """Policy."""

    problem_list = []
    """List of problems."""

    def __init__(self, props):
        self.maximum_stream_count = ExpertSettings.maximum_stream_count
        self.wireless_policy = ExpertSettings.wireless_policy
        self.problem_list = ExpertSettings.problem_list
        self._load(props)

    def __repr__(self):
        return (
            f'ExpertSettings({{'
            f'maximum_stream_count: {self.maximum_stream_count}, '
            f'wireless_policy: {{{repr(self.wireless_policy)}}}, '
            f'problem_list: [{repr_array(self.problem_list)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Expert Settings: '
            f'maximum_stream_count={self.maximum_stream_count}, '
            f'wireless_policy={{{str(self.wireless_policy)}}}, '
            f'problem_list=[{str_array(self.problem_list)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            max = props.get('maxStreamCount')
            if isinstance(max, int):
                self.maxStreamCount = int(max)

            policy = props.get('policy')
            if isinstance(policy, dict):
                self.wireless_policy = WirelessPolicy(policy)

            problems = props.get('problems')
            if isinstance(problems, list):
                self.problems = create_object_list(problems, ExpertProblem)


class ESSID(object):
    """The ESSID class has the attributes of an expert policy ESSID."""

    enabled = False
    """Whether ESSID policy enabled."""

    name = ''
    """Name of the ESSID."""

    def __init__(self, props):
        self.enabled = ESSID.enabled
        self.name = ESSID.name
        self._load(props)

    def __repr__(self):
        return (
            f'ESSID({{'
            f'enabled: {self.enabled}, '
            f'name: "{self.name}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'ESSID: '
            f'enabled={self.enabled}, '
            f'name="{self.name}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            enabled = props.get(_json_enabled)
            if isinstance(enabled, bool):
                self.enabled = bool(enabled)

            name = props.get('value')
            if isinstance(name, six.string_types):
                self.name = str(name)


class ProtocolName(object):
    """The ProtocolName class has the attributes of an expert protocol.
    """

    id = ProtocolLayer.UNKNOWN
    """Protocol Layer Id."""

    name = ''
    """Layer name."""

    def __init__(self, props):
        self.id = ProtocolName.id
        self.name = ProtocolName.name
        self._load(props)

    def __repr__(self):
        return (
            f'ProtocolLayerMap({{'
            f'id: {self.id}, '
            f'name: "{self.name}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Layer Mapping: '
            f'id={self.id}, '
            f'name="{self.name}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            id = props.get('id')
            if isinstance(id, int):
                self.id = id if id in ProtocolLayer else ProtocolLayer.UNKNOWN

            name = props.get('layer')
            if isinstance(name, six.string_types):
                self.name = str(name) if name else ''


vendor_id_dict = {
    'accessPoint': 'is_access',
    'client': 'is_client',
    'value': 'address'
}


class VendorId(object):
    """The VendorId class has the attributes of an expert policy Vendor item."""

    address = None
    """Vendor's Ethernet Address."""

    is_access_point = False
    """Whether access point."""

    is_client = False
    """Whether client."""

    def __init__(self, props):
        self.address = VendorId.address
        self.is_access_point = VendorId.is_access_point
        self.is_client = VendorId.is_client
        self._load(props)

    def __repr__(self):
        return (
            f'VendorId({{'
            f'address: {self.address}, '
            f'is_access_point: {self.is_access_point}, '
            f'is_access_client: "{self.is_access_client}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Vendor Id: '
            f'address={self.address}, '
            f'is_access_point={self.is_access_point}, '
            f'is_client={self.is_client}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            address = props.get(_json_value)
            if isinstance(address, six.string_types):
                self.address = EthernetAddress(address)

            ap = props.get('accessPoint')
            if isinstance(ap, bool):
                self.is_access_point = bool(ap)

            client = props.get('client')
            if isinstance(client, bool):
                self.is_client = bool(client)


_wireless_channel_attributes = (
    'band',
    'channel',
    _json_enabled,
    'frequency'
)


class WirelessChannel(object):
    """The WirelessChannel class has the attributes of a wireless channel."""

    band = 0
    """Channel band."""

    channel = 0
    """Channel number."""

    enabled = False
    """Whether channel policy enabled."""

    frequency = 0
    """Channel frequency."""

    def __init__(self, props):
        self.band = WirelessChannel.band
        self.channel = WirelessChannel.channel
        self.enabled = WirelessChannel.enabled
        self.frequency = WirelessChannel.frequency
        self._load(props)

    def __repr__(self):
        return (
            f'WirelessChannel({{'
            f'band: {self.band}, '
            f'channel: {self.channel}, '
            f'enabled: {self.enabled}, '
            f'frequency: {self.frequency}'
            f'}})'
        )

    def __str__(self):
        return (
            f'WirelessChannel: '
            f'band={self.band}, '
            f'channel={self.channel}, '
            f'enabled={self.enabled}, '
            f'frequency={self.frequency}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_list(self, props, _wireless_channel_attributes)


class WirelessPolicy(object):
    """The WirelessPolicy class has the attributes of an expert policy."""

    accept_authentication_list = False
    """Accept the Authentication List."""

    accept_channel_family_list = False
    """Accept the Channel List."""

    accept_encryption_protocol_list = False
    """Accept the Encryption Protocol List."""

    accept_essid_name_list = []
    """Accept the ESS Name List."""

    authentication_protocol_list = None
    """Authentication policy list."""

    encryption_protocol_list = []
    """Encryption protocol list."""

    essid_name_list = []
    """ESSID Name list."""

    vendor_id_list = []
    """Vendor ID policy."""

    channel_family_list = []
    """Channel policy."""

    def __init__(self, props):
        self.accept_authentication_list = WirelessPolicy.accept_authentication_list
        self.accept_channel_family_list = WirelessPolicy.accept_channel_family_list
        self.accept_encryption_protocol_list = WirelessPolicy.accept_encryption_protocol_list
        self.accept_essid_name_list = WirelessPolicy.accept_essid_name_list
        self.authentication_protocol_list = WirelessPolicy.authentication_protocol_list
        self.channel_family_list = WirelessPolicy.channel_family_list
        self.encryption_protocol_list = WirelessPolicy.encryption_protocol_list
        self.essid_name_list = WirelessPolicy.essid_name_list
        self.vendor_id_list = WirelessPolicy.vendor_id_list
        self._load(props)

    def __repr__(self):
        return (
            f'WirelessPolicy({{'
            f'authentication_protocol_list: {{{repr(self.authentication_protocol_list)}}}, '
            f'channel_family_list: {{{repr(self.channel_family_list)}}}, '
            f'encryption: {{{repr(self.encryption_protocol_list)}}}, '
            f'esessid_name_lists_id: {{{repr(self.essid_name_list)}}}, '
            f'vendor_id_list: {{{repr(self.vendor_id_list)}}}'
            f'}})'
        )

    def __str__(self):
        return (
            f'WirelessPolicy Policy: '
            f'authentication_protocol_list={{{str(self.authentication_protocol_list)}}}, '
            f'channel_family_list={{{str(self.channel_family_list)}}}, '
            f'encryption={{{str(self.encryption_protocol_list)}}}, '
            f'essid_name_list={{{str(self.essid_name_list)}}}, '
            f'vendor_id_list={{{str(self.vendor_id_list)}}}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            authentication = props.get('authentication')
            if isinstance(authentication, dict):
                accept = authentication.get(_json_accept)
                if isinstance(accept, bool):
                    self.accept_authentication_list = bool(accept)
                protocols = authentication.get(_json_items)
                if isinstance(protocols, list):
                    self.authentication_protocol_list = create_object_list(protocols,
                                                                           AuthenticaitonProtocol)

            channel = props.get('channel')
            if isinstance(channel, dict):
                accept = channel.get(_json_accept)
                if isinstance(accept, bool):
                    self.accept_channel_list = bool(accept)

                band = channel.get('channelBand')
                if isinstance(band, six.string_types):
                    self.channel_band = str(band)

                family = channel.get('channelFamily')
                if isinstance(family, list):
                    for f in family:
                        if isinstance(f, dict):
                            channel_list = f.get(_json_items)
                            if isinstance(channel_list, list):
                                self.channel_family_list.append(
                                    create_object_list(channel_list, WirelessChannel))

            encryption = props.get('encryption')
            if isinstance(encryption, dict):
                accept = encryption.get(_json_accept)
                if isinstance(accept, bool):
                    self.accept_encryption = bool(accept)

                protocols = encryption.get(_json_items)
                if isinstance(protocols, list):
                    self.encryption_protocol_list = create_object_list(protocols,
                                                                       EncryptionProtocol)

            ess_id = props.get('essId')
            if isinstance(ess_id, dict):
                accept = ess_id.get(_json_accept)
                if isinstance(accept, bool):
                    self.accept_essid_name_list = bool(accept)

                names = ess_id.get(_json_items)
                if isinstance(names, list):
                    self.essid_name_list = create_object_list(names, ESSID)

            vendor = props.get('vendorId')
            if isinstance(vendor, dict):
                accept = vendor.get(_json_accept)
                if isinstance(accept, bool):
                    self.accept_vendor_id_list = bool(accept)

                items = vendor.get(_json_items)
                if isinstance(items, list):
                    self.vendor_id_list = create_object_list(items, VendorId)


class ExpertPreferences(object):
    """The ExpertPreferences class has the attributes expert preferences."""

    default_settings = None
    """Default Expert settings."""

    description_list = []
    """List of descriptions."""

    protocol_name_list = []
    """List of ProtocolNames."""

    settings = None
    """Expert settings."""

    event_label_list = []
    """List of ExpertEvent."""

    def __init__(self, props):
        self.default_settings_list = ExpertPreferences.default_settings
        self.description_list = ExpertPreferences.description_list
        self.protocol_name_list = ExpertPreferences.protocol_name_list
        self.settings_list = ExpertPreferences.settings
        self.event_label_list = ExpertPreferences.event_label_list
        self._load(props)

    def __repr__(self):
        return (
            f'ExpertPreferences: '
            f'default_settings: {{{repr(self.default_settings)}}}, '
            f'description_list: [{repr_array(self.description_list)}], '
            f'protocol_name_list: [{repr_array(self.protocol_name_list)}], '
            f'settings: {{{repr(self.settings)}}}, '
            f'event_label_list: [{repr_array(self.event_label_list)}]'
        )

    def __str__(self):
        return (
            f'Expert Preferences: '
            f'default_settings_list={{{str(self.default_settings)}}}, '
            f'description_list=[{str_array(self.description_list)}], '
            f'protocol_name_list=[{str_array(self.protocol_name_list)}], '
            f'settings_list={{{str(self.settings)}}}, '
            f'event_label_list=[{str_array(self.event_label_list)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            descriptions = props.get('descriptions')
            if isinstance(descriptions, list):
                self.description_list = create_object_list(descriptions, ExpertDescription)

            protocols = props.get('layers')
            if isinstance(protocols, list):
                self.protocol_name_list = create_object_list(protocols, ProtocolName)

            settings = props['settings']
            if isinstance(settings, dict):
                current = settings.get('current')
                if isinstance(current, dict):
                    self.settings = ExpertSettings(current)

                default = settings.get('_default')
                if isinstance(default, dict):
                    self.default_settings = ExpertSettings(default)

            events = props.get('stringTable')
            if isinstance(events, list):
                self.event_label_list = create_object_list(events, ExpertEvent)

"""LiveFlow class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import json
from typing import Union

from .invariant import EngineOperation
from .omnierror import OmniError
from .helpers import load_props_from_dict, OmniScriptEncoder, repr_array, str_array


_ipfix_wan_mac_list_item_dict = {
    'ifidx': 'ifidx',
    'ifname': 'ifname',
    'mac': 'mac'
}


class LiveFlowConfigurationPreferencesIpfixWanMacListItem(object):
    """The LiveFlowConfigurationPreferencesIpfixWanMacListItem class has the attributes of a
    LiveFlow router map entry.
    """

    ifidx = 1
    """Represents the ifindex of an adapter."""

    ifname = ''
    """Represents the interface name of an adapter."""

    mac = ''
    """Represents the MAC address of an adapter."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowConfigurationPreferencesIpfixWanMacListItem({{'
            f'ifidx: {self.ifidx}, '
            f'ifname: "{self.ifname}", '
            f'mac: "{self.mac}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow Router Map Entry: '
            f'ifidx={self.ifidx}, '
            f'ifname="{self.ifname}", '
            f'mac="{self.mac}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _ipfix_wan_mac_list_item_dict)


_liveflow_configuration_preferences_ipfix_dict = {
    'active_flow_refresh_interval': 'active_flow_refresh_interval',
    'avc_enabled': 'avc_enabled',
    'flowdir_enabled': 'flowdir_enabled',
    'fnf_enabled': 'fnf_enabled',
    'max_payload': 'max_payload',
    'medianet_enabled': 'medianet_enabled',
    'options_template_refresh_interval': 'options_template_refresh_interval',
    'signaling_dn_enabled': 'signaling_dn_enabled',
    'template_refresh_interval': 'template_refresh_interval',
    'target_address': 'target_address'
}


class LiveFlowConfigurationPreferencesIpfix(object):
    """The LiveFlowConfigurationPreferencesIpfix class has the attributes of LiveFlow IPFIX
    preferences.
    """

    active_flow_refresh_interval = 60
    """Indicates the time interval (in seconds) in which LiveFlow generates data records."""

    avc_enabled = True
    """Whether LiveFlow should generate AVC IPFIX records."""

    flowdir_enabled = True
    """Indicates whether the flowDirection key is sent in unidirectional IPFIX records indicating
    the flow direction: 0 = ingress, 1 = egress.
    """

    fnf_enabled = True
    """Whether LiveFlow should generate FNF IPFIX records."""

    max_payload = 1500
    """The MTU of IPFIX packets."""

    medianet_enabled = True
    """Whether LiveFlow should generate MediaNet IPFIX records."""

    options_template_refresh_interval = 600
    """Indicates the time interval (in seconds) in which LiveFlow generates IPFIX option template
    records.
    """

    signaling_dn_enabled = True
    """Whether LiveFlow should generate Signaling DN IPFIX records."""

    template_refresh_interval = 600
    """Indicates the time interval (in seconds) in which LiveFlow generates IPFIX template
    records."""

    target_address = '127.0.0.1'
    """Indicates the location of the server instance receiving IPFIX records from LiveFlow:
    Option #1: An IP address,
    Option #2: An IP address and port in the following form: ip_address:port.
    """

    wan_mac_list = []
    """The LiveFlow router mappings."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowConfigurationPreferencesIpfix({{'
            f'active_flow_refresh_interval: {self.active_flow_refresh_interval}, '
            f'avc_enabled: {self.avc_enabled}, '
            f'flowdir_enabled: {self.flowdir_enabled}, '
            f'fnf_enabled: {self.fnf_enabled}, '
            f'max_payload: {self.max_payload}, '
            f'medianet_enabled: {self.medianet_enabled}, '
            f'options_template_refresh_interval: {self.options_template_refresh_interval}, '
            f'signaling_dn_enabled: {self.signaling_dn_enabled}, '
            f'template_refresh_interval: {self.template_refresh_interval}, '
            f'target_address: "{self.target_address}", '
            f'wan_mac_list: [{repr_array(self.wan_mac_list)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowConfigurationPreferencesIpfix: '
            f'active_flow_refresh_interval={self.active_flow_refresh_interval}, '
            f'avc_enabled={self.avc_enabled}, '
            f'flowdir_enabled={self.flowdir_enabled}, '
            f'fnf_enabled={self.fnf_enabled}, '
            f'max_payload={self.max_payload}, '
            f'medianet_enabled={self.medianet_enabled}, '
            f'options_template_refresh_interval={self.options_template_refresh_interval}, '
            f'signaling_dn_enabled={self.signaling_dn_enabled}, '
            f'template_refresh_interval={self.template_refresh_interval}, '
            f'target_address="{self.target_address}", '
            f'wan_mac_list=[{str_array(self.wan_mac_list)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_configuration_preferences_ipfix_dict)

        if isinstance(props, dict):
            wan_mac_list = None
            if 'wan_mac_list' in props:
                wan_mac_list = props['wan_mac_list']
            if isinstance(wan_mac_list, list):
                self.wan_mac_list = []
                for v in wan_mac_list:
                    self.wan_mac_list.append(LiveFlowConfigurationPreferencesIpfixWanMacListItem(v))


_liveflow_configuration_preferences_dict = {
    'config_check_interval': 'config_check_interval',
    'debug_logging': 'debug_logging',
    'decryption_enabled': 'decryption_enabled',
    'enforce_tcp_3way_handshake': 'enforce_tcp_3way_handshake',
    'flow_time_ipfix': 'flow_time_ipfix',
    'hashtable_size': 'hashtable_size',
    'hostname_analysis': 'hostname_analysis',
    'https_port': 'https_port',
    'latency_enabled': 'latency_enabled',
    'quality_enabled': 'quality_enabled',
    'retransmissions_enabled': 'retransmissions_enabled',
    'rtp_enabled': 'rtp_enabled',
    'rtp_packets_disabled': 'rtp_packets_disabled',
    'signaling_packet_window': 'signaling_packet_window',
    'tcp_handshake_timeout': 'tcp_handshake_timeout',
    'tcp_orphan_timeout': 'tcp_orphan_timeout',
    'tcp_packets_disabled': 'tcp_packets_disabled',
    'tcp_post_close_timeout': 'tcp_post_close_timeout',
    'tcp_wait_timeout': 'tcp_wait_timeout',
    'tls_analysis': 'tls_analysis',
    'tls_packet_window': 'tls_packet_window',
    'udp_packets_disabled': 'udp_packets_disabled',
    'udp_wait_timeout': 'udp_wait_timeout',
    'vlan_enabled': 'vlan_enabled',
    'voip_quality_percent': 'voip_quality_percent',
    'web_enabled': 'web_enabled'
}


class LiveFlowConfigurationPreferences(object):
    """The LiveFlowConfigurationPreferences class has the attributes of LiveFlow preferences."""

    config_check_interval = 1000
    """The time interval (in milliseconds) at which LiveFlow should check for updates in the
    configuration file.
    """

    debug_logging = 0
    """Indicates how much debug logging to display in the log files:
    0 = None, 1 = Low, 2 = Medium, 3 = High, 4 = Verbose.
    """

    decryption_enabled = False
    """Whether LiveFlow performs decryption for HTTPS packets."""

    enforce_tcp_3way_handshake = False
    """Whether LiveFlow requires a 3-way handshake (SYN, SYN-ACK, ACK) for a TCP flow in order for
    it to be included in processing and analyzing.
    """

    flow_time_ipfix = True
    """Whether IPFIX flow time is relative to IPFIX intervals (True) or flow packets (False)."""

    hashtable_size = 0
    """Indicates the total number of active flows expected at any one time per stream
    (a value of 0 indicates that LiveFlow will auto-determine the correct value).
    """

    hostname_analysis = True
    """Whether LiveFlow performs hostname analysis."""

    https_port = 443
    """The HTTPS port."""

    ipfix = None
    """IPFIX preferences."""

    latency_enabled = True
    """Whether LiveFlow performs latency analysis."""

    quality_enabled = True
    """Whether LiveFlow performs TCP quality analysis."""

    retransmissions_enabled = True
    """Whether LiveFlow performs TCP retransmission analysis."""

    rtp_enabled = True
    """Whether LiveFlow performs RTP analysis."""

    rtp_packets_disabled = False
    """Whether LiveFlow ignores RTP packets."""

    signaling_packet_window = 0
    """Indicates how many packets per SIP flow should be run through the SIP analysis; LiveFlow
    will analyze the first number of indicated packets and then ignore the rest that follow
    (0 = unlimited).
    """

    tcp_handshake_timeout = 2000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a TCP
    flow while waiting for a 3-Way handshake to complete before considering the current flow
    complete and starting a new flow (ignored if enforce_tcp_3way_handshake key is false).
    """

    tcp_orphan_timeout = 60000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a TCP
    flow after receiving a 3-Way handshake (if the enforce_tcp_3way_handshake key is true) and
    before the flow has begun to close (before a FIN is seen) before considering the current
    flow complete and starting a new flow.
    """

    tcp_packets_disabled = False
    """Whether LiveFlow ignores TCP packets."""

    tcp_post_close_timeout = 1000
    """Indicates the maximum amount of time (in milliseconds) to keep a flow in the hash table
    after it has been completed.
    """

    tcp_wait_timeout = 3000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a TCP
    flow while waiting for the flow to close (after the first FIN is seen) before considering
    the current flow complete and starting a new flow.
    """

    tls_analysis = True
    """Whether LiveFlow performs TLS analysis."""

    tls_packet_window = 16
    """Indicates how many packets per HTTPS flow should be looked at for TLS information."""

    udp_packets_disabled = False
    """Whether LiveFlow ignores UDP packets."""

    udp_wait_timeout = 3000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a UDP
    flow before considering the current flow complete and starting a new flow.
    """

    vlan_enabled = True
    """Whether LiveFlow performs VLAN/VXLAN/MPLS analysis."""

    voip_quality_percent = 25
    """Represents a percentage indicating how strongly to weight the average VoIP quality score vs
    the worst VoIP quality score when computing the MOS score (0 means the score is based
    completely on the worst score, and 100 means that the score is based completely on the
    average).
    """

    web_enabled = False
    """Whether LiveFlow performs web analysis."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowConfigurationPreferences({{'
            f'config_check_interval: {self.config_check_interval}, '
            f'debug_logging: {self.debug_logging}, '
            f'decryption_enabled: {self.decryption_enabled}, '
            f'enforce_tcp_3way_handshake: {self.enforce_tcp_3way_handshake}, '
            f'flow_time_ipfix: {self.flow_time_ipfix}, '
            f'hashtable_size: {self.hashtable_size}, '
            f'hostname_analysis: {self.hostname_analysis}, '
            f'https_port: {self.https_port}, '
            f'ipfix: {{{repr(self.ipfix)}}}, '
            f'latency_enabled: {self.latency_enabled}, '
            f'quality_enabled: {self.quality_enabled}, '
            f'retransmissions_enabled: {self.retransmissions_enabled}, '
            f'rtp_enabled: {self.rtp_enabled}, '
            f'rtp_packets_disabled: {self.rtp_packets_disabled}, '
            f'signaling_packet_window: {self.signaling_packet_window}, '
            f'tcp_handshake_timeout: {self.tcp_handshake_timeout}, '
            f'tcp_orphan_timeout: {self.tcp_orphan_timeout}, '
            f'tcp_packets_disabled: {self.tcp_packets_disabled}, '
            f'tcp_post_close_timeout: {self.tcp_post_close_timeout}, '
            f'tcp_wait_timeout: {self.tcp_wait_timeout}, '
            f'tls_analysis: {self.tls_analysis}, '
            f'tls_packet_window: {self.tls_packet_window}, '
            f'udp_packets_disabled: {self.udp_packets_disabled}, '
            f'udp_wait_timeout: {self.udp_wait_timeout}, '
            f'vlan_enabled: {self.vlan_enabled}, '
            f'voip_quality_percent: {self.voip_quality_percent}, '
            f'web_enabled: {self.web_enabled}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowConfigurationPreferences: '
            f'config_check_interval={self.config_check_interval}, '
            f'debug_logging={self.debug_logging}, '
            f'decryption_enabled={self.decryption_enabled}, '
            f'enforce_tcp_3way_handshake={self.enforce_tcp_3way_handshake}, '
            f'flow_time_ipfix={self.flow_time_ipfix}, '
            f'hashtable_size={self.hashtable_size}, '
            f'hostname_analysis={self.hostname_analysis}, '
            f'https_port={self.https_port}, '
            f'ipfix={{{str(self.ipfix)}}}, '
            f'latency_enabled={self.latency_enabled}, '
            f'quality_enabled={self.quality_enabled}, '
            f'retransmissions_enabled={self.retransmissions_enabled}, '
            f'rtp_enabled={self.rtp_enabled}, '
            f'rtp_packets_disabled={self.rtp_packets_disabled}, '
            f'signaling_packet_window={self.signaling_packet_window}, '
            f'tcp_handshake_timeout={self.tcp_handshake_timeout}, '
            f'tcp_orphan_timeout={self.tcp_orphan_timeout}, '
            f'tcp_packets_disabled={self.tcp_packets_disabled}, '
            f'tcp_post_close_timeout={self.tcp_post_close_timeout}, '
            f'tcp_wait_timeout={self.tcp_wait_timeout}, '
            f'tls_analysis={self.tls_analysis}, '
            f'tls_packet_window={self.tls_packet_window}, '
            f'udp_packets_disabled={self.udp_packets_disabled}, '
            f'udp_wait_timeout={self.udp_wait_timeout}, '
            f'vlan_enabled={self.vlan_enabled}, '
            f'voip_quality_percent={self.voip_quality_percent}, '
            f'web_enabled={self.web_enabled}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_configuration_preferences_dict)

        if isinstance(props, dict):
            ipfix = None
            if 'ipfix' in props:
                ipfix = props['ipfix']
            if isinstance(ipfix, dict):
                self.ipfix = LiveFlowConfigurationPreferencesIpfix(ipfix)


_liveflow_service_dict = {
    'nid': 'nid',
    'sni': 'sni'
}


class LiveFlowService(object):
    """The LiveFlowService class has the attributes of a LiveFlow service."""

    nid = ''
    """The capture engine application id."""

    sni = ''
    """The server name indication."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowService({{'
            f'nid: "{self.nid}", '
            f'sni: "{self.sni}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow Service: '
            f'nid="{self.nid}", '
            f'sni="{self.sni}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_service_dict)


_liveflow_configuration_dict = {
    'version': 'version'
}


class LiveFlowConfiguration(object):
    """The LiveFlowConfiguration class has the attributes of LiveFlow configuration."""

    preferences = None
    """LiveFlow preferences."""

    services = []
    """List of LiveFlow services."""

    version = 0
    """LiveFlow configuration version."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowConfiguration({{'
            f'preferences: {{{repr(self.preferences)}}}, '
            f'services: [{repr_array(self.services)}], '
            f'version: {self.version}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowConfiguration: '
            f'preferences={{{str(self.preferences)}}}, '
            f'services=[{str_array(self.services)}], '
            f'version={self.version}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_configuration_dict)

        if isinstance(props, dict):
            preferences = None
            if 'preferences' in props:
                preferences = props['preferences']
            if isinstance(preferences, dict):
                self.preferences = LiveFlowConfigurationPreferences(preferences)

            services = None
            if 'services' in props:
                services = props['services']
            if isinstance(services, list):
                self.services = []
                for v in services:
                    self.services.append(LiveFlowService(v))


_liveflow_configuration_response_dict = {
    'rebootRequired': 'rebootRequired'
}


class LiveFlowConfigurationResponse(object):
    """The LiveFlowConfigurationResponse class has the attributes of LiveFlow
    configuration response.
    """

    rebootRequired = False
    """Whether a reboot is required."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowConfigurationResponse({{'
            f'rebootRequired: {self.rebootRequired}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowConfigurationResponse: '
            f'rebootRequired={self.rebootRequired}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_configuration_response_dict)


_liveflow_license_dict = {
    'activeFlowCountLimit': 'activeFlowCountLimit',
    'liveFlowEnabled': 'liveFlowEnabled'
}


class LiveFlowLicense(object):
    """The LiveFlowLicense class has the attributes of LiveFlow licenses."""

    activeFlowCountLimit = 0
    """The number of active flows that can be tracked at one time for a LiveFlow capture
    (0 = unlimited).
    """

    liveFlowEnabled = True
    """Whether the Capture Engine supports LiveFlow."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowLicense({{'
            f'activeFlowCountLimit: {self.activeFlowCountLimit}, '
            f'liveFlowEnabled: {self.liveFlowEnabled}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow License: '
            f'activeFlowCountLimit={self.activeFlowCountLimit}, '
            f'liveFlowEnabled={self.liveFlowEnabled}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_license_dict)


_liveflow_context_dict = {
    'hostnameAnalysis': 'hostnameAnalysis',
    'ipfixAVCOutput': 'ipfixAVCOutput',
    'ipfixFNFOutput': 'ipfixFNFOutput',
    'ipfixMediaNetOutput': 'ipfixMediaNetOutput',
    'ipfixSignalingDNOutput': 'ipfixSignalingDNOutput',
    'latencyAnalysis': 'latencyAnalysis',
    'rtpAnalysis': 'rtpAnalysis',
    'tcp3WayHandshakeEnforcement': 'tcp3WayHandshakeEnforcement',
    'tcpQualityAnalysis': 'tcpQualityAnalysis',
    'tcpRetransmissionsAnalysis': 'tcpRetransmissionsAnalysis',
    'tlsAnalysis': 'tlsAnalysis',
    'tlsDecryption': 'tlsDecryption',
    'vlanVxlanMplsAnalysis': 'vlanVxlanMplsAnalysis',
    'webAnalysis': 'webAnalysis'
}


class LiveFlowContext(object):
    """The LiveFlowContext class has the attributes of a LiveFlow context."""

    hostnameAnalysis = True
    """Whether LiveFlow performs hostname analysis."""

    ipfixAVCOutput = True
    """Whether LiveFlow generates IPFIX AVC records."""

    ipfixFNFOutput = True
    """Whether LiveFlow generates IPFIX FNF records."""

    ipfixMediaNetOutput = True
    """Whether LiveFlow generates IPFIX MediaNet records."""

    ipfixSignalingDNOutput = True
    """Whether LiveFlow generates IPFIX Signaling DN records."""

    latencyAnalysis = True
    """Whether LiveFlow performs latency analysis."""

    license = None
    """LiveFlow license."""

    rtpAnalysis = True
    """Whether LiveFlow performs RTP analysis."""

    tcp3WayHandshakeEnforcement = True
    """Whether LiveFlow requires TCP flows to have a 3-way handshake."""

    tcpQualityAnalysis = True
    """Whether LiveFlow performs TCP quality analysis."""

    tcpRetransmissionsAnalysis = True
    """Whether LiveFlow performs TCP retransmissions analysis."""

    tlsAnalysis = True
    """Whether LiveFlow performs TLS analysis."""

    tlsDecryption = True
    """Whether LiveFlow performs TLS (<= v1.2) Decryption."""

    vlanVxlanMplsAnalysis = True
    """Whether LiveFlow performs VLAN/VXLAN/MPLS analysis."""

    webAnalysis = True
    """Whether LiveFlow performs HTTP/1.N web analysis."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowContext({{'
            f'hostnameAnalysis: {self.hostnameAnalysis}, '
            f'ipfixAVCOutput: {self.ipfixAVCOutput}, '
            f'ipfixFNFOutput: {self.ipfixFNFOutput}, '
            f'ipfixMediaNetOutput: {self.ipfixMediaNetOutput}, '
            f'ipfixSignalingDNOutput: {self.ipfixSignalingDNOutput}, '
            f'latencyAnalysis: {self.latencyAnalysis}, '
            f'license: {{{repr(self.license)}}}, '
            f'rtpAnalysis: {self.rtpAnalysis}, '
            f'tcp3WayHandshakeEnforcement: {self.tcp3WayHandshakeEnforcement}, '
            f'tcpQualityAnalysis: {self.tcpQualityAnalysis}, '
            f'tcpRetransmissionsAnalysis: {self.tcpRetransmissionsAnalysis}, '
            f'tlsAnalysis: {self.tlsAnalysis}, '
            f'tlsDecryption: {self.tlsDecryption}, '
            f'vlanVxlanMplsAnalysis: {self.vlanVxlanMplsAnalysis}, '
            f'webAnalysis: {self.webAnalysis}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowContext: '
            f'hostnameAnalysis={self.hostnameAnalysis}, '
            f'ipfixAVCOutput={self.ipfixAVCOutput}, '
            f'ipfixFNFOutput={self.ipfixFNFOutput}, '
            f'ipfixMediaNetOutput={self.ipfixMediaNetOutput}, '
            f'ipfixSignalingDNOutput={self.ipfixSignalingDNOutput}, '
            f'latencyAnalysis={self.latencyAnalysis}, '
            f'license={{{str(self.license)}}}, '
            f'rtpAnalysis={self.rtpAnalysis}, '
            f'tcp3WayHandshakeEnforcement={self.tcp3WayHandshakeEnforcement}, '
            f'tcpQualityAnalysis={self.tcpQualityAnalysis}, '
            f'tcpRetransmissionsAnalysis={self.tcpRetransmissionsAnalysis}, '
            f'tlsAnalysis={self.tlsAnalysis}, '
            f'tlsDecryption={self.tlsDecryption}, '
            f'vlanVxlanMplsAnalysis={self.vlanVxlanMplsAnalysis}, '
            f'webAnalysis={self.webAnalysis}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_context_dict)

        if isinstance(props, dict):
            license = None
            if 'license' in props:
                license = props['license']
            if isinstance(license, dict):
                self.license = LiveFlowLicense(license)


_liveflow_status_hash_tables_dict = {
    'activeFlowCountLimit': 'activeFlowCountLimit',
    'capacity': 'capacity',
    'collisions': 'collisions',
    'deletions': 'deletions',
    'droppedInsertions': 'droppedInsertions',
    'id': 'id',
    'insertions': 'insertions',
    'maxContiguousFilledBuckets': 'maxContiguousFilledBuckets',
    'rtpInsertions': 'rtpInsertions',
    'size': 'size'
}


class LiveFlowStatusHashTables(object):
    """The LiveFlowStatusHashTables class has the attributes of a LiveFlow hash table."""

    activeFlowCountLimit = 0
    """The number of active flows that are currently being tracked by the hash table."""

    capacity = 0
    """The capacity of the hash table."""

    collisions = 0
    """The number of collisions for the hash table."""

    deletions = 0
    """The number of deletions for the hash table."""

    droppedInsertions = 0
    """The number of dropped insertions for the hash table."""

    id = 0
    """The id for the hash table."""

    insertions = 0
    """The number of insertions for the hash table."""

    maxContiguousFilledBuckets = 0
    """The number of max contiguous filled buckets for the hash table."""

    rtpInsertions = 0
    """The number of RTP insertions for the hash table."""

    size = 0
    """The size of the hash table."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowStatusHashTables({{'
            f'activeFlowCountLimit: {self.activeFlowCountLimit}, '
            f'capacity: {self.capacity}, '
            f'collisions: {self.collisions}, '
            f'deletions: {self.deletions}, '
            f'droppedInsertions: {self.droppedInsertions}, '
            f'id: {self.id}, '
            f'insertions: {self.insertions}, '
            f'maxContiguousFilledBuckets: {self.maxContiguousFilledBuckets}, '
            f'rtpInsertions: {self.rtpInsertions}, '
            f'size: {self.size}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow Status Hash Tables: '
            f'activeFlowCountLimit={self.activeFlowCountLimit}, '
            f'capacity={self.capacity}, '
            f'collisions={self.collisions}, '
            f'deletions={self.deletions}, '
            f'droppedInsertions={self.droppedInsertions}, '
            f'id={self.id}, '
            f'insertions={self.insertions}, '
            f'maxContiguousFilledBuckets={self.maxContiguousFilledBuckets}, '
            f'rtpInsertions={self.rtpInsertions}, '
            f'size={self.size}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_status_hash_tables_dict)


_liveflow_status_records_sent_dict = {
    'ipfixAVCCount': 'ipfixAVCCount',
    'ipfixFNFCount': 'ipfixFNFCount',
    'ipfixMediaNetCount': 'ipfixMediaNetCount',
    'ipfixSignalingDNIPv4Count': 'ipfixSignalingDNIPv4Count',
    'ipfixSignalingDNIPv6Count': 'ipfixSignalingDNIPv6Count'
}


class LiveFlowStatusRecordsSent(object):
    """The LiveFlowStatusRecordsSent class has the attributes of LiveFlow records."""

    ipfixAVCCount = 0
    """The number of IPFIX AVC records sent."""

    ipfixFNFCount = 0
    """The number of IPFIX FNF records sent."""

    ipfixMediaNetCount = 0
    """The number of IPFIX MediaNet records sent."""

    ipfixSignalingDNIPv4Count = 0
    """The number of IPFIX Signaling DN IPv4 records sent."""

    ipfixSignalingDNIPv6Count = 0
    """The number of IPFIX Signaling DN IPv6 records sent."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowStatusRecordsSent({{'
            f'ipfixAVCCount: {self.ipfixAVCCount}, '
            f'ipfixFNFCount: {self.ipfixFNFCount}, '
            f'ipfixMediaNetCount: {self.ipfixMediaNetCount}, '
            f'ipfixSignalingDNIPv4Count: {self.ipfixSignalingDNIPv4Count}, '
            f'ipfixSignalingDNIPv6Count: {self.ipfixSignalingDNIPv6Count}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow Status Records Sent: '
            f'ipfixAVCCount={self.ipfixAVCCount}, '
            f'ipfixFNFCount={self.ipfixFNFCount}, '
            f'ipfixMediaNetCount={self.ipfixMediaNetCount}, '
            f'ipfixSignalingDNIPv4Count={self.ipfixSignalingDNIPv4Count}, '
            f'ipfixSignalingDNIPv6Count={self.ipfixSignalingDNIPv6Count}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_status_records_sent_dict)


_liveflow_status_dict = {
    'activeFlowCount': 'activeFlowCount',
    'captureStartTime': 'captureStartTime',
    'flowsRejected': 'flowsRejected',
    'flowsRTPZeroPacket': 'flowsRTPZeroPacket',
    'flowsSeen': 'flowsSeen',
    'packetsAccepted': 'packetsAccepted',
    'packetsRejected': 'packetsRejected',
    'packetsSeen': 'packetsSeen'
}


class LiveFlowStatus(object):
    """The LiveFlowStatus class has the attributes of LiveFlow status."""

    activeFlowCount = 0
    """The number of active flows that are currently being tracked by LiveFlow."""

    captureStartTime = ''
    """In ISO 8601 format: CCYY-MM-DDThh:mm:ss.sssssssssZ. Will be null if the
    capture has never been started.
    """

    flowsRejected = 0
    """The number of flows rejected by LiveFlow due to the active flow count limit."""

    flowsRTPZeroPacket = 0
    """The number of RTP zero packet flows detected by LiveFlow."""

    flowsSeen = 0
    """The number of flows seen by LiveFlow."""

    hashTable = []
    """The LiveFlow hash table status"""

    recordsSent = None
    """The number of records sent by LiveFlow."""

    packetsAccepted = 0
    """The number of packets accepted and analyzed by LiveFlow."""

    packetsRejected = 0
    """The number of packets rejected by LiveFlow."""

    packetsSeen = 0
    """The number of packets seen by LiveFlow."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowStatus({{'
            f'activeFlowCount: {self.activeFlowCount}, '
            f'captureStartTime: "{self.captureStartTime}", '
            f'flowsRejected: {self.flowsRejected}, '
            f'flowsRTPZeroPacket: {self.flowsRTPZeroPacket}, '
            f'flowsSeen: {self.flowsSeen}, '
            f'hashTable: [{repr_array(self.hashTable)}], '
            f'recordsSent: {{{repr(self.recordsSent)}}}, '
            f'packetsAccepted: {self.packetsAccepted}, '
            f'packetsRejected: {self.packetsRejected}, '
            f'packetsSeen: {self.packetsSeen}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowStatus: '
            f'activeFlowCount={self.activeFlowCount}, '
            f'captureStartTime="{self.captureStartTime}", '
            f'flowsRejected={self.flowsRejected}, '
            f'flowsRTPZeroPacket={self.flowsRTPZeroPacket}, '
            f'flowsSeen={self.flowsSeen}, '
            f'hashTable=[{str_array(self.hashTable)}], '
            f'recordsSent={{{str(self.recordsSent)}}}, '
            f'packetsAccepted={self.packetsAccepted}, '
            f'packetsRejected={self.packetsRejected}, '
            f'packetsSeen={self.packetsSeen}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_status_dict)

        if isinstance(props, dict):
            hashTable = None
            if 'hashTable' in props:
                hashTable = props['hashTable']
            if isinstance(hashTable, list):
                self.hashTable = []
                for v in hashTable:
                    self.hashTable.append(LiveFlowStatusHashTables(v))

            recordsSent = None
            if 'recordsSent' in props:
                recordsSent = props['recordsSent']
            if isinstance(recordsSent, dict):
                self.recordsSent = LiveFlowStatusRecordsSent(recordsSent)


class LiveFlow(object):
    """The LiveFlow class is an interface into LiveFlow operations."""

    engine = None
    """OmniEngine interface."""

    def __init__(self, engine):
        self.engine = engine

    def __repr__(self):
        return f'LiveFlow({repr(self.engine)})'

    def __str__(self):
        return 'LiveFlow'

    def get_liveflow_configuration(self) -> Union[LiveFlowConfiguration, None]:
        """Gets the LiveFlow configuration"""
        if self.engine is not None:
            command = 'liveflow/configuration/'
            pr = self.engine.perf('get_liveflow_configuration')
            resp = self.engine._issue_command(command, pr, EngineOperation.GET)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get LiveFlow configuration.')
            return LiveFlowConfiguration(resp)
        return None

    def set_liveflow_configuration(self, config: LiveFlowConfiguration) -> (
            Union[LiveFlowConfigurationResponse, None]):
        """Sets the LiveFlow configuration"""
        if self.engine is not None:
            command = 'liveflow/configuration/'
            pr = self.engine.perf('set_liveflow_configuration')
            resp = self.engine._issue_command(command, pr, EngineOperation.POST,
                                              data=json.dumps(config, cls=OmniScriptEncoder))
            if not isinstance(resp, dict):
                raise OmniError('Failed to set LiveFlow context.')
            return LiveFlowConfigurationResponse(resp)
        return None

    def get_liveflow_context(self) -> Union[LiveFlowContext, None]:
        """Gets the LiveFlow context"""
        if self.engine is not None:
            command = 'liveflow/context/'
            pr = self.engine.perf('get_liveflow_context')
            resp = self.engine._issue_command(command, pr, EngineOperation.GET)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get LiveFlow context.')
            return LiveFlowContext(resp)
        return None

    def get_liveflow_status(self) -> Union[LiveFlowStatus, None]:
        """Gets the LiveFlow status"""
        if self.engine is not None:
            command = 'liveflow/status/'
            pr = self.engine.perf('get_liveflow_status')
            resp = self.engine._issue_command(command, pr, EngineOperation.GET)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get LiveFlow status.')
            return LiveFlowStatus(resp)
        return None

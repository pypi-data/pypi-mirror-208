"""EngineSettings
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
from typing import Union

try:
    from omniengine import OmniEngine
except ImportError:
    import sys
    OmniEngine = sys.modules[__package__ + '.omniengine']

from .helpers import (
    create_object_list, load_native_props_from_dict, load_native_props_from_list,
    load_props_from_dict, repr_array, str_array)
from .invariant import AuthenticationServerType, PeekResult
from .omniid import OmniId
from .user import User
from .omniaddress import parse_ip_address
from .omniport import OmniPort

_json_address = 'ip'
_json_host_address = 'host'
_json_command_list = 'commands'
_json_id = 'id'
_json_is_allowed = 'allow'
_json_is_enabled = 'use'
_json_maximum = 'maximum'
_json_name = 'name'
_json_policy_list = 'policies'
_json_port = 'port'
_json_user = 'user'
_json_user_list = 'users'


_network_settings_dict = {
    'agentName': 'agent_name',
    'autoRestart': 'is_auto_restart',
    'connectionCapacity': 'connection_capacity',
    'connectionTimeout': 'connection_timeout',
    'dataRootPath': 'data_root_path',
    'ipSelected': 'ip_selected',
    'logRecordsAdjustment': 'log_records_adjustment',
    'logRecordsMaximum': 'log_records_maximum',
    'port': 'port',
    'securityAlertRecordsAdjustment': 'security_alert_records_adjustment',
    'securityAlertRecordsMaximum': 'security_alert_records_maximum',
    'securityEventRecordsAdjustment': 'security_event_records_adjustment',
    'securityEventRecordsMaximum': 'security_event_records_maximum',
    'udpDiscovery': 'udp_discovery'
}


class NetworkSettings(object):
    """The NetworkSettings class has the attributes of engine network settings."""

    agent_name = ''
    """Agent name."""

    connection_capacity = 0
    """Connection capacity."""

    connection_timeout = 0
    """Connection timeout."""

    data_root_path = ''
    """Data root path."""

    ip_available = []
    """IPs available."""

    ip_selected = ''
    """IP selected."""

    log_records_adjustment = 0
    """Log records adjustment."""

    log_records_maximum = 0
    """Maximum log records."""

    port = 0
    """Port."""

    security_alert_records_adjustment = 0
    """Security alert records adjustment."""

    security_alert_records_maximum = 0
    """Maximum security alert records."""

    security_event_records_adjustment = 0
    """Security event records adjustment."""

    security_event_records_maximum = 0
    """Maximum security event records."""

    is_auto_restart = False
    """Whether auto restart."""

    is_udp_discovery = False
    """Whether UDP discovery is enabled."""

    def __init__(self, props=None):
        self.agent_name = NetworkSettings.agent_name
        self.connection_capacity = NetworkSettings.connection_capacity
        self.connection_timeout = NetworkSettings.connection_timeout
        self.data_root_path = NetworkSettings.data_root_path
        self.ip_available = NetworkSettings.ip_available
        self.ip_selected = NetworkSettings.ip_selected
        self.log_records_adjustment = NetworkSettings.log_records_adjustment
        self.log_records_maximum = NetworkSettings.log_records_maximum
        self.port = NetworkSettings.port
        self.security_alert_records_adjustment = NetworkSettings.security_alert_records_adjustment
        self.security_alert_records_maximum = NetworkSettings.security_alert_records_maximum
        self.security_event_records_adjustment = NetworkSettings.security_event_records_adjustment
        self.security_event_records_maximum = NetworkSettings.security_event_records_maximum
        self.is_auto_restart = NetworkSettings.is_auto_restart
        self.is_udp_discovery = NetworkSettings.is_udp_discovery
        self._load(props)

    def __repr__(self):
        return (
            f'EngineSettingsNetwork({{'
            f'agent_name: "{self.agent_name}", '
            f'connection_capacity: {self.connection_capacity}, '
            f'connection_timeout: {self.connection_timeout}, '
            f'data_root_path: "{self.data_root_path}", '
            f'ip_available: [{repr_array(self.ip_available)}], '
            f'ip_selected: "{self.ip_selected}", '
            f'log_records_adjustment: {self.log_records_adjustment}, '
            f'log_records_maximum: {self.log_records_maximum}, '
            f'port: {self.port}, '
            f'security_alert_records_adjustment: {self.security_alert_records_adjustment}, '
            f'security_alert_records_maximum: {self.security_alert_records_maximum}, '
            f'security_event_records_adjustment: {self.security_event_records_adjustment}, '
            f'security_event_records_maximum: {self.security_event_records_maximum}, '
            f'is_auto_restart: {self.is_auto_restart}, '
            f'is_udp_discovery: {self.is_udp_discovery}, '
            f'}})'
        )

    def __str__(self):
        return (
            f'Engine Settings Network: '
            f'agent_name="{self.agent_name}", '
            f'connection_capacity={self.connection_capacity}, '
            f'connection_timeout={self.connection_timeout}, '
            f'data_root_path="{self.data_root_path}", '
            f'ip_available=[{str_array(self.ip_available)}], '
            f'ip_selected="{self.ip_selected}", '
            f'log_records_adjustment={self.log_records_adjustment}, '
            f'log_records_maximum={self.log_records_maximum}, '
            f'port={self.port}, '
            f'security_alert_records_adjustment={self.security_alert_records_adjustment}, '
            f'security_alert_records_maximum={self.security_alert_records_maximum}, '
            f'security_event_records_adjustment={self.security_event_records_adjustment}, '
            f'security_event_records_maximum={self.security_event_records_maximum}, '
            f'is_auto_restart={self.is_auto_restart}, '
            f'is_udp_discovery={self.is_udp_discovery}, '
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _network_settings_dict)

        if isinstance(props, dict):
            ips = props.get('ipAvailable')
            if isinstance(ips, list):
                self.ip_available = []
                for v in ips:
                    self.ip_available.append(parse_ip_address(v))


class AccessControlPolicy(object):
    """The AccessControlPolicy class has the attributes of an engine ACL policy."""

    command_list = []
    """ACL policy commands."""

    id = None
    """ACL policy id."""

    user_list = []
    """ACL policy users."""

    def __init__(self, props=None):
        self.command_list = AccessControlPolicy.command_list
        self.id = AccessControlPolicy.id
        self.user_list = AccessControlPolicy.user_list
        self._load(props)

    def __repr__(self):
        return (
            f'AccessControlPolicy({{'
            f'command_list: [{repr_array(self.command_list)}], '
            f'id: "{self.id}", '
            f'user_list: [{repr_array(self.user_list)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Access Control Policy: '
            f'command_list=[{str_array(self.command_list)}], '
            f'id="{self.id}", '
            f'user_list=[{str_array(self.user_list)}]'
        )

    def _load(self, props):
        if isinstance(props, dict):
            commands = props.get(_json_command_list)
            if isinstance(commands, list):
                self.command_list = create_object_list(commands, dict)

            id = props.get(_json_id)
            if id:
                self.id = OmniId(id)

            users = props.get(_json_user_list)
            if isinstance(users, list):
                self.user_list = create_object_list(users, User)


class AccessControlList(object):
    """The AccessControlList class has the attributes of engine ACL."""

    is_enabled = False
    """Whether ACL is enabled."""

    policy_list = []
    """ACL policies."""

    def __init__(self, props=None):
        self.is_enabled = AccessControlList.is_enabled
        self.policy_list = AccessControlList.policy_list
        self._load(props)

    def __repr__(self):
        return (
            f'AccessControlList({{'
            f'policy_list: [{repr_array(self.policy_list)}], '
            f'enabled: "{self.is_enabled}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'AccessControlList: '
            f'policy_list=[{str_array(self.policy_list)}], '
            f'is_enabled="{self.is_enabled}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            enabled = props.get(_json_is_enabled)
            self.is_enabled = bool(enabled)

            policies = props[_json_policy_list]
            if isinstance(policies, list):
                self.policy_list = create_object_list(policies, AccessControlPolicy)


_engine_user_dict = {
    'account': 'account',
    'description': 'description',
    'domain': 'domain',
    'sid': 'sid'
}


class EngineUser(object):
    """The EngineUser class has the attributes of an engine user."""

    account = ''
    """User account."""

    description = ''
    """User description."""

    domain = ''
    """User domain."""

    sid = ''
    """User sid."""

    def __init__(self, props=None):
        self._load(props)

    def __repr__(self):
        return (
            f'EngineUser({{'
            f'account: "{self.account}", '
            f'description: "{self.description}", '
            f'domain: "{self.domain}", '
            f'sid: "{self.sid}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Engine User: '
            f'account="{self.account}", '
            f'description="{self.description}", '
            f'domain="{self.domain}", '
            f'sid="{self.sid}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _engine_user_dict)


class RuntimeLock(object):
    """The RuntimeLock class has the attributes
    of engine settings runtime lock.
    """

    id = None
    """id."""

    user = None
    """User."""

    def __init__(self, props=None):
        self.id = RuntimeLock.id
        self.user = RuntimeLock.user
        self._load(props)

    def __repr__(self):
        return (
            f'RuntimeLock({{'
            f'id: "{self.id}", '
            f'user: {repr(self.user)}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Runtime Lock: '
            f'id="{self.id}", '
            f'user={str(self.user)}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            self.id = OmniId(props.get(_json_id))
            lock = props.get('lock')
            if isinstance(lock, dict):
                self.user = User(lock)


# _engine_settings_runtime_lock_capture_lock_dict = {
#     'id': 'id'
# }


# class EngineSettingsRuntimeLockCaptureLock(object):
#     """The EngineSettingsRuntimeLockCaptureLock class has the
#     attributes of engine settings runtime lock capture lock.
#     """

#     id = ''
#     """id."""

#     lock = None
#     """Lock."""

#     def __init__(self, props=None):
#         self._load(props)

#     def __repr__(self):
#         return (
#             f'EngineSettingsRuntimeLockCaptureLock({{'
#             f'id: "{self.id}", '
#             f'lock: {{{repr(self.lock)}}}'
#             f'}})'
#         )

#     def __str__(self):
#         return (
#             f'Engine Settings Runtime Lock Capture Lock: '
#             f'id="{self.id}", '
#             f'lock={{{str(self.lock)}}}'
#         )

#     def _load(self, props):
#         """Set attributes from a dictionary."""
#         load_props_from_dict(self, props,
#                              _engine_settings_runtime_lock_capture_lock_dict)

#         if isinstance(props, dict):
#             lock = None
#             if 'lock' in props:
#                 lock = props['lock']
#             if isinstance(lock, dict):
#                 self.lock = EngineUser(lock)


class SessionLock(object):
    """The SessionLock class has the attributes of engine settings runtime
    lock session lock."""

    maximum = 0
    """Maximum."""

    user = None
    """User."""

    def __init__(self, props=None):
        self.maximum = SessionLock.maximum
        self.user = SessionLock.user
        self._load(props)

    def __repr__(self):
        return (
            f'SessionLock({{'
            f'maximum: {self.maximum}, '
            f'user: "{self.user.name}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Session Lock: '
            f'maximum={self.maximum}, '
            f'user="{self.user.name}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            max = props.get(_json_maximum)
            if max is not None:
                self.maximum = int(max)
            user = props.get(_json_user)
            if isinstance(user, six.string_types):
                prop_user = {'name': user}
                self.user = User(prop_user)


class EngineLock(object):
    """The EngineLock class has the attributes of engine settings runtime lock."""

    adapter_lock_list = []
    """Adapter locks."""

    capture_lock_list = []
    """Capture locks."""

    filters_lock = None
    """Filter lock."""

    session_lock_list = []
    """Session locks."""

    def __init__(self, props=None):
        self.adapter_lock_list = EngineLock.adapter_lock_list
        self.capture_lock_list = EngineLock.capture_lock_list
        self.filters_lock = EngineLock.filters_lock
        self.session_lock_list = EngineLock.session_lock_list
        self._load(props)

    def __repr__(self):
        return (
            f'EngineLock({{'
            f'adapter_lock_list: [{repr_array(self.adapter_lock_list)}], '
            f'capture_lock_list: [{repr_array(self.capture_lock_list)}], '
            f'filters_lock: {{{repr(self.filters_lock)}}}, '
            f'session_lock_list: [{repr_array(self.session_lock_list)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'EngineLock: '
            f'adapter_lock_list=[{str_array(self.adapter_lock_list)}], '
            f'capture_lock_list=[{str_array(self.capture_lock_list)}], '
            f'filters_lock={{{str(self.filters_lock)}}}, '
            f'session_lock_list=[{str_array(self.session_lock_list)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            adapter_locks = props.get('adapterLocks')
            if isinstance(adapter_locks, list):
                self.adapter_lock_list = create_object_list(adapter_locks, RuntimeLock)

            capture_locks = props.get('captureLocks')
            if isinstance(capture_locks, list):
                self.capture_lock_list = create_object_list(capture_locks, RuntimeLock)

            filters_lock = props.get('filtersLock')
            if isinstance(filters_lock, dict):
                self.filters_lock = User(filters_lock)

            session_locks = props.get('sessionLocks')
            if isinstance(session_locks, list):
                self.session_lock_list = create_object_list(session_locks, SessionLock)


_security_authentication_dict = {
    'disableGuest': 'is_guest_disabled',
    'package': 'package',
    'provider': 'provider'
}


class SecurityAuthentication(object):
    """The EngineSettingsSecurityAuthentication class has the attributes
    of engine settings security authentication.
    """

    package = ''
    """Package."""

    provider = ''
    """Provider."""

    is_guest_disabled = False
    """Whether guest account is disabled."""

    def __init__(self, props=None):
        self.package = SecurityAuthentication.package
        self.provider = SecurityAuthentication.provider
        self.is_guest_disabled = SecurityAuthentication.is_guest_disabled
        self._load(props)

    def __repr__(self):
        return (
            f'SecurityAuthentication({{'
            f'is_guest_disabled: {self.is_guest_disabled}, '
            f'package: "{self.package}", '
            f'provider: "{self.provider}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Security Authentication: '
            f'is guest disabled={self.is_guest_disabled}, '
            f'package="{self.package}", '
            f'provider="{self.provider}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _security_authentication_dict)


_authenticatioin_server_dict = {
    _json_name: 'name',
    _json_is_enabled: 'is_enabled'
}


class AuthenticationServer(object):
    """The AuthenticationServer class has the attributes of a basic
    engine settings authentication server.
    """

    is_enabled = False
    """Whether the authentication server is in enabled and in-use."""

    name = ''
    """Name of authentication server."""

    server_type = AuthenticationServerType.UNKNOWN
    """Type of authentication server."""

    def __init__(self, server_type: AuthenticationServerType):
        self.is_enabled = AuthenticationServer.is_enabled
        self.server_type = server_type
        self.name = AuthenticationServer.name

    def __repr__(self):
        return (
            f'AuthenticationServer({{'
            f'is_enabled: {self.is_enabled}, '
            f'name: "{self.name}", '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Authentication Server: '
            f'is_enabled={self.is_enabled}, '
            f'name="{self.name}", '
            f'server_type={self.server_type}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _authenticatioin_server_dict)
        if isinstance(props, dict):
            server_type = props.get('authenticationType')
            if server_type is not None:
                self.server_type = (AuthenticationServerType(server_type)
                                    if server_type in AuthenticationServerType
                                    else AuthenticationServerType.UNKNOWN)


class ActiveDirectoryServer(AuthenticationServer):
    """The ActiveDirectoryServer is a subclass of the
    :class:`AuthenticationServer <omniscript.enginesettings.AuthenticationServer>`
    class. It contains the additional attributes of an Active Directory
    Authentication Server.
    """

    address = ''
    """Host Address."""

    port = 0
    """Host Port."""

    def __init__(self, props=None):
        super(ActiveDirectoryServer, self).__init__(AuthenticationServerType.ACTIVE_DIRECTORY)
        self.address = ActiveDirectoryServer.address
        self.port = ActiveDirectoryServer.port
        self._load(props)

    def __repr__(self):
        return (
            f'Active Directory Server({{'
            f'address: {self.address}, '
            f'is_enabled: {self.is_enabled}, '
            f'name: "{self.name}", '
            f'port: {self.port}, '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Active Directory: '
            f'address="{self.address}:{self.port}", '
            f'is_enabled={self.is_enabled}, '
            f'name="{self.name}", '
            f'server_type={self.server_type}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        super(ActiveDirectoryServer, self)._load(props)
        if isinstance(props, dict):
            address = props.get(_json_host_address)
            if address is not None:
                self.address = parse_ip_address(address)
            port = props.get(_json_port)
            if port is not None:
                self.port = OmniPort(port)


_kerberos_list = ('kdc', 'realm')


class KerberosServer(AuthenticationServer):
    """The KerberosServer class is a subclass of the
    :class:`AuthenticationServer <omniscript.enginesettings.AuthenticationServer>`
    class. It contains the additional attributes of a KerberosServer
    Authentication Server.
    """

    kdc = ''
    """KDC."""

    realm = ''
    """Realm."""

    def __init__(self, props):
        super(KerberosServer, self).__init__(AuthenticationServerType.KERBEROS)
        self.kdc = KerberosServer.kdc
        self.realm = KerberosServer.realm
        self._load(props)

    def __repr__(self):
        return (
            f'KerberosServer({{'
            f'is_enabled: {self.is_enabled}, '
            f'kdc: "{self.kdc}", '
            f'name: "{self.name}", '
            f'realm: "{self.realm}", '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Kerberos Server: '
            f'is_enabled={self.is_enabled}, '
            f'kdc="{self.kdc}", '
            f'name="{self.name}", '
            f'realm="{self.realm}", '
            f'server_type={self.server_type}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        super(KerberosServer, self)._load(props)
        load_native_props_from_list(self, props, _kerberos_list)


class LocalAuthenticationServer(AuthenticationServer):
    """The LocalAuthenticationServer class is a subclass of the
    :class:`AuthenticationServer <omniscript.enginesettings.AuthenticationServer>`
    class. It does not contain any additional attributes.
    """

    def __init__(self, props: Union[dict, None] = None):
        super(LocalAuthenticationServer, self).__init__(AuthenticationServerType.LOCAL)
        super(LocalAuthenticationServer, self)._load(props)

    def __repr__(self):
        return (
            f'LocalAuthenticationServer({{'
            f'is_enabled: {self.is_enabled}, '
            f'name: "{self.name}", '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Local Authentication Server: '
            f'is_enabled={self.is_enabled}, '
            f'name="{self.name}", '
            f'server_type={self.server_type}'
        )


class RadiusServer(AuthenticationServer):
    """The RadiusServer class is a subclass of the
    :class:`AuthenticationServer <omniscript.enginesettings.AuthenticationServer>`
    class. It contains the additional attributes of an RadiusServer
    Authentication Server.
    """

    address = ''
    """Host Address."""

    port = 0
    """Host Port."""

    secret = ''
    """Secret."""

    def __init__(self, props: Union[dict, None] = None):
        super(RadiusServer, self).__init__(AuthenticationServerType.RADIUS)
        self.address = RadiusServer.address
        self.port = RadiusServer.port
        self.secret = RadiusServer.secret
        self._load(props)

    def __repr__(self):
        return (
            f'RadiusServer({{'
            f'address: "{self.address}", '
            f'is_enabled: {self.is_enabled}, '
            f'name: "{self.name}", '
            f'port: {self.port}, '
            f'secret: "{self.secret}", '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Radius Server: '
            f'address="{self.address}:{self.port}", '
            f'is_enabled={self.is_enabled}, '
            f'name="{self.name}", '
            f'secret="{self.secret}", '
            f'server_type={self.server_type}'
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        super(RadiusServer, self)._load(props)
        if isinstance(props, dict):
            address = props.get(_json_host_address)
            if address is not None:
                self.address = parse_ip_address(address)
            port = props.get(_json_port)
            if port is not None:
                self.port = OmniPort(port)
            secret = props.get('secret')
            if secret is not None:
                self.secret = str(secret)


class TacasPlusServer(AuthenticationServer):
    """The TacasPlusServer class is a subclass of the
    :class:`AuthenticationServer <omniscript.enginesettings.AuthenticationServer>`
    class. It contains the additional attributes of an Tacas
    Authentication Server.
    """

    address = None
    """Host address."""

    port = None
    """Host Port."""

    secret = ''
    """Secret."""

    def __init__(self, props: Union[dict, None] = None):
        super(TacasPlusServer, self).__init__(AuthenticationServerType.TACACS_PLUS)
        self.address = TacasPlusServer.address
        self.port = TacasPlusServer.port
        self.secret = TacasPlusServer.secret
        self._load(props)

    def __repr__(self):
        return (
            f'TacasPlusServer({{'
            f'address: {self.address}, '
            f'is_enabled: {self.is_enabled}, '
            f'name: "{self.name}", '
            f'port: {self.port}, '
            f'secret: "{self.secret}", '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Tacas Plus Server: '
            f'address={self.address}:{self.port}, '
            f'is_enabled={self.is_enabled}, '
            f'name="{self.name}", '
            f'secret="{self.secret}", '
            f'server_type={self.server_type}'
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        super(TacasPlusServer, self)._load(props)
        if isinstance(props, dict):
            address = props.get(_json_host_address)
            if address is not None:
                self.address = parse_ip_address(address)
            port = props.get(_json_port)
            if port is not None:
                self.port = OmniPort(port)
            secret = props.get('secret')
            if secret is not None:
                self.secret = str(secret) if secret else ''


class UnknownAuthenticationServer(AuthenticationServer):
    """The UnknownAuthenticationServer class is a subclass of the
    :class:`AuthenticationServer <omniscript.enginesettings.AuthenticationServer>`
    class. It does not contain any additional attributes.
    """

    def __init__(self, props: Union[dict, None] = None):
        super(UnknownAuthenticationServer, self).__init__(AuthenticationServerType.UNKNOWN)
        super(UnknownAuthenticationServer, self)._load(props)

    def __repr__(self):
        return (
            f'UnknownAuthenticationServer({{'
            f'is_enabled: {self.is_enabled}, '
            f'name: "{self.name}", '
            f'server_type: {self.server_type}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Unknown Authentication Server: '
            f'is_enabled={self.is_enabled}, '
            f'name="{self.name}", '
            f'server_type={self.server_type}'
        )


_authentication_config_dict = {
    _json_is_allowed: 'is_allowed',
    'secret': 'secret'
}


class AuthenticationConfig(object):
    """The AuthenticationConfig class has the
    attributes of engine settings security authentication configuration.
    """

    is_allowed = False
    """Whether allowed."""

    address = None
    """IP address."""

    port = None
    """Port."""

    secret = ''
    """Secret."""

    def __init__(self, props: Union[dict, None] = None):
        self.is_allowed = AuthenticationConfig.is_allowed
        self.address = AuthenticationConfig.address
        self.port = AuthenticationConfig.port
        self.secret = AuthenticationConfig.secret
        self._load(props)

    def __repr__(self):
        return (
            f'AuthenticationConfig({{'
            f'is_allowed: {self.is_allowed}, '
            f'address: "{self.address}", '
            f'port: {self.port}, '
            f'secret: "{self.secret}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Authentication Config: '
            f'is_allowed={self.is_allowed}, '
            f'address="{self.address}:{self.port}", '
            f'secret="{self.secret}"'
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _authentication_config_dict)
        if isinstance(props, dict):
            address = props.get(_json_address)
            if address is not None:
                self.address = parse_ip_address(address)
            port = props.get('port')
            if port is not None:
                self.port = OmniPort(port)


_ssl_certificate_dict = {
    'serialNumber': 'serial_number',
    'storeLocation': 'store_location',
    'storeName': 'store_name',
    'subject': 'subject'
}


class SSLCertificate(object):
    """The SSLCertificate class has the attributes of engine settings
    security SSL certificate."""

    serial_number = ''
    """Serial number."""

    store_location = ''
    """Store location."""

    store_name = ''
    """Store name."""

    subject = ''
    """Subject."""

    def __init__(self, props: Union[dict, None] = None):
        self.serial_number = SSLCertificate.serial_number
        self.store_location = SSLCertificate.store_location
        self.store_name = SSLCertificate.store_name
        self.subject = SSLCertificate.subject
        self._load(props)

    def __repr__(self):
        return (
            f'SSLCertificate({{'
            f'serial_number: "{self.serial_number}", '
            f'store_location: "{self.store_location}", '
            f'store_name: "{self.store_name}", '
            f'subject: "{self.subject}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'SSL Certificate: '
            f'serial_number="{self.serial_number}", '
            f'store_location="{self.store_location}", '
            f'store_name="{self.store_name}", '
            f'subject="{self.subject}"'
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _ssl_certificate_dict)


_engine_settings_security_dict = {
    'adminPassword': 'admin_password',
    'auditing': 'is_auditing',
    'auditingSyslog': 'is_auditing_syslog',
    'auditingSyslogDestination': 'auditing_syslog_destination',
    'compressionThreshold': 'compression_threshold',
    'encrypted': 'is_encrypted',
    'useCompression': 'is_compression',
    'useEncryption': 'use_encryption',
    'useImpersonation': 'use_impersonation',
    'userPassword': 'user_password',
    'useSSL': 'is_ssl'
}


class SecuritySettings(object):
    """The SecuritySettings class has the attributes of engine security settings."""

    admin_password = ''
    """Admin password."""

    auditing_syslog_destination = ''
    """Auditing syslog destination."""

    authentication = None
    """Authentication."""

    authentication_server_list = None
    """Authentication server list."""

    compression_threshold = 0
    """Compression threshold."""

    radius = None
    """Radius information."""

    ssl_certificate = None
    """SSL certificate information."""

    tacas_plus = None
    """TACACS+ information."""

    user_password = ''
    """User password."""

    is_auditing = False
    """Whether auditing is enabled."""

    is_auditing_syslog = False
    """Whether auditing syslog is enabled."""

    is_authentication_servers = False
    """Is the authentication server list enabled."""

    is_compression = False
    """Whether compression is enabled."""

    is_encrypted = False
    """Whether encrypted."""

    is_ssl = False
    """Whether SSL is enabled."""

    use_encryption = False
    """Whether encryption is enabled."""

    use_impersonation = False
    """Whether impersonation is enabled."""

    def __init__(self, props: Union[dict, None] = None):
        self.admin_password = SecuritySettings.admin_password
        self.auditing_syslog_destination = SecuritySettings.auditing_syslog_destination
        self.authentication = SecuritySettings.authentication
        self.authentication_server_list = SecuritySettings.authentication_server_list
        self.compression_threshold = SecuritySettings.compression_threshold
        self.radius = SecuritySettings.radius
        self.ssl_certificate = SecuritySettings.ssl_certificate
        self.tacas_plus = SecuritySettings.tacas_plus
        self.user_password = SecuritySettings.user_password
        self.is_auditing = SecuritySettings.is_auditing
        self.is_auditing_syslog = SecuritySettings.is_auditing_syslog
        self.is_authentication_servers = SecuritySettings.is_authentication_servers
        self.is_compression = SecuritySettings.is_compression
        self.is_encrypted = SecuritySettings.is_encrypted
        self.is_ssl = SecuritySettings.is_ssl
        self.use_encryption = SecuritySettings.use_encryption
        self.use_impersonation = SecuritySettings.use_impersonation
        self._load(props)

    def __repr__(self):
        return (
            f'SecuritySettings({{'
            f'admin_password: "{self.admin_password}", '
            f'auditing_syslog_destination: {self.auditing_syslog_destination}, '
            f'authentication: {self.authentication}, '
            f'authentication_server_list: ["{repr_array(self.authentication_server_list)}"], '
            f'compression_threshold: {{{repr(self.compression_threshold)}}}", '
            f'radius: {{{repr(self.radius)}}}", '
            f'ssl_certificate: {self.ssl_certificate}, '
            f'tacas_plus: {self.tacas_plus}, '
            f'user_password: {{{repr(self.user_password)}}}", '
            f'is_auditing: {{{repr(self.is_auditing)}}}", '
            f'is_auditing_syslog: {{{repr(self.is_auditing_syslog)}}}", '
            f'is_authentication_servers: {self.is_authentication_servers}, '
            f'is_compression: {self.is_compression}, '
            f'is_encrypted: {self.is_encrypted}, '
            f'is_ssl: {self.is_ssl}, '
            f'use_encryption: {self.use_encryption}, '
            f'use_impersonation: {self.use_impersonation}, '
            f'}})'
        )

    def __str__(self):
        return (
            f'Security Settings: '
            f'admin_password="{self.admin_password}", '
            f'auditing_syslog_destination={self.auditing_syslog_destination}, '
            f'authentication={self.authentication}, '
            f'authentication_server_list=["{str_array(self.authentication_server_list)}"], '
            f'compression_threshold={{{str(self.compression_threshold)}}}, '
            f'radius={{{str(self.radius)}}}, '
            f'ssl_certificate={self.ssl_certificate}, '
            f'tacas_plus={self.tacas_plus}, '
            f'user_password={{{str(self.user_password)}}}, '
            f'is_auditing={{{str(self.is_auditing)}}}, '
            f'is_auditing_syslog={{{str(self.is_auditing_syslog)}}}, '
            f'is_authentication_servers={self.is_authentication_servers}, '
            f'is_compression={self.is_compression}, '
            f'is_encrypted={self.is_encrypted}, '
            f'is_ssl={self.is_ssl}, '
            f'use_encryption={self.use_encryption}, '
            f'use_impersonation={self.use_impersonation}, '
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _engine_settings_security_dict)

        if isinstance(props, dict):
            authentication = props.get('authentication')
            if isinstance(authentication, dict):
                self.authentication = SecurityAuthentication(authentication)

            servers = props.get('authenticationServers')
            if isinstance(servers, dict):
                self.is_authentication_servers = bool(servers.get(_json_is_enabled))
                server_list = servers.get('servers')
                if isinstance(server_list, list):
                    self.authentication_server_list = []
                    for v in server_list:
                        if isinstance(v, dict):
                            auth = v.get('authenticationType')
                            auth_type = (AuthenticationServerType(auth)
                                         if auth in AuthenticationServerType
                                         else AuthenticationServerType.UNKNOWN)
                            if auth_type == AuthenticationServerType.ACTIVE_DIRECTORY:
                                self.authentication_server_list.append(ActiveDirectoryServer(v))
                            elif auth_type == AuthenticationServerType.KERBEROS:
                                self.authentication_server_list.append(KerberosServer(v))
                            elif auth_type == AuthenticationServerType.RADIUS:
                                self.authentication_server_list.append(RadiusServer(v))
                            elif auth_type == AuthenticationServerType.TACACS_PLUS:
                                self.authentication_server_list.append(TacasPlusServer(v))
                            elif auth_type == AuthenticationServerType.LOCAL:
                                self.authentication_server_list.append(
                                    LocalAuthenticationServer(v))
                            else:
                                self.authentication_server_list.append(
                                    UnknownAuthenticationServer(v))
            radius = props.get('radius')
            if isinstance(radius, dict):
                self.radius = AuthenticationConfig(radius)

            ssl = props.get('sslCertificate')
            if isinstance(ssl, dict):
                self.ssl_certificate = SSLCertificate(ssl)

            tacas = props.get('tacasPlus')
            if isinstance(tacas, dict):
                self.tacas_plus = AuthenticationConfig(tacas)


_engine_settings_dict = {
    'engineType': 'engine_type',
    'version': 'version'
}

_json_acl = 'acl'
_json_capabilities = 'capabilities'
_json_network = 'network'
_json_runtime_lock = 'runtimeLock'
_json_security = 'security'


class EngineSettings(object):
    """The EngineSettings class has the attributes of engine settings."""

    acl = None
    """ACL settings."""

    capabilities = []
    """Engine capability OmniIds."""

    engine_type = ''
    """Engine type."""

    network = None
    """Network settings."""

    runtime_locks = None
    """Runtime lock settings."""

    security = None
    """Security settings."""

    version = ''
    """Version."""

    is_acl_enabled = False
    """Is the Acess Control List enabled?"""

    def __init__(self, props: Union[dict, None] = None):
        self.acl = EngineSettings.acl
        self.capabilities = EngineSettings.capabilities
        self.engine_type = EngineSettings.engine_type
        self.network = EngineSettings.network
        self.runtime_locks = EngineSettings.runtime_locks
        self.security = EngineSettings.security
        self.version = EngineSettings.version
        self.is_acl_enabled = EngineSettings.is_acl_enabled
        self._load(props)

    def __repr__(self):
        return (
            f'EngineSettings({{'
            f'acl: {{{repr(self.acl)}}}, '
            f'capabilities: [{repr_array(self.capabilities)}], '
            f'engine_type: "{self.engine_type}", '
            f'network: {{{repr(self.network)}}}, '
            f'runtime_locks: {{{repr(self.runtime_locks)}}}, '
            f'security: {{{repr(self.security)}}}, '
            f'version: "{self.version}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Engine Settings: '
            f'acl={{{str(self.acl)}}}, '
            f'capabilities=[{str_array(self.capabilities)}], '
            f'engine_type="{self.engine_type}", '
            f'network={{{str(self.network)}}}, '
            f'runtime_locks={{{str(self.runtime_locks)}}}, '
            f'security={{{str(self.security)}}}, '
            f'version="{self.version}"'
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _engine_settings_dict)

        if isinstance(props, dict):
            acl = props.get(_json_acl)
            if isinstance(acl, dict):
                self.is_acl_enabled = bool(acl.get(_json_is_enabled))
                policies = acl.get(_json_policy_list)
                if isinstance(policies, list):
                    self.acl = create_object_list(policies, AccessControlPolicy)

            capabilities = props.get(_json_capabilities)
            if isinstance(capabilities, list):
                self.capabilities = create_object_list(capabilities, OmniId)

            network = props.get(_json_network)
            if isinstance(network, dict):
                self.network = NetworkSettings(network)

            runtime_lock = props.get(_json_runtime_lock)
            if isinstance(runtime_lock, dict):
                self.runtime_locks = EngineLock(runtime_lock)

            security = props.get(_json_security)
            if isinstance(security, dict):
                self.security = SecuritySettings(security)

    @classmethod
    def get(cls, engine: OmniEngine):
        pr = engine.perf('settings')
        command = 'settings/'
        resp = engine._issue_command(command, pr)
        return EngineSettings(resp)


class SetSettingsResponse(object):
    """The SetSettingsResponse class has the attributes of a set settings response."""

    result = PeekResult.OK
    """Result."""

    def __init__(self, props=None):
        self._load(props)

    def __repr__(self):
        return (
            f'SetSettingsResponse({{'
            f'result: {self.result}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Set Settings Response: '
            f'result={self.result}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            result = props.get('result')
            if isinstance(result, int):
                self.result = result if result in PeekResult else PeekResult.OK

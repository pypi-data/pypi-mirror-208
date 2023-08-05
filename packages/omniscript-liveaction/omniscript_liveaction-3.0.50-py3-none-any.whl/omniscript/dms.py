"""DMS class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import json
import six
from typing import Union

from .invariant import (
    DMSAutenticaionType, DMSLicenseType, DMSTSRSeverity, EngineOperation as EO,
    DMS_IP_ASSIGNMENT, DMS_IP_ASSIGNMENT_DHCP, DMS_BACKUP_STATUS, DMS_BACKUP_STATUS_SUCCESS,
    DMS_RESTORE_STATUS, DMS_RESTORE_STATUS_IDLE, DMS_RESTORE_SETTINGS_APPLICATION)
from .omnierror import OmniError
from .helpers import load_props_from_dict, OmniScriptEncoder, repr_array, str_array


_dms_static_address_dict = {
    'gateway': 'gateway',
    'ipAddress': 'ipAddress',
    'netmask': 'netmask'
}


class DMSStaticAddress(object):
    """The DMSStaticAddress class has the attributes of a DMS static address."""

    dnsServers = []
    """List of DNS servers."""

    gateway = ''
    """Static address gateway."""

    ipAddress = ''
    """Static address IP address."""

    netmask = ''
    """Static address netmask."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSStaticAddress({{'
            f'dnsServers: [{repr_array(self.dnsServers)}], '
            f'gateway: "{self.gateway}", '
            f'ipAddress: "{self.ipAddress}", '
            f'netmask: "{self.netmask}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Static Address: '
            f'dnsServers=[{str_array(self.dnsServers)}], '
            f'gateway="{self.gateway}", '
            f'ipAddress="{self.ipAddress}", '
            f'netmask="{self.netmask}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_static_address_dict)

        if isinstance(props, dict):
            dnsServers = None
            if 'dnsServers' in props:
                dnsServers = props['dnsServers']
            if isinstance(dnsServers, list):
                self.dnsServers = []
                for v in dnsServers:
                    self.dnsServers.append(v)


class DMSAddress(object):
    """The DMSAddress class has the attributes of a DMS Address."""

    ipAssignment = DMS_IP_ASSIGNMENT_DHCP
    """Whether the address is DHCP or static."""

    staticAddress = None
    """Static address."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAddress({{'
            f'ipAssignment: "{self.ipAssignment}", '
            f'staticAddress: {{{repr(self.staticAddress)}}}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Address: '
            f'ipAssignment="{self.ipAssignment}", '
            f'staticAddress={{{str(self.staticAddress)}}}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            ipAssignment = None
            if 'ipAssignment' in props:
                ipAssignment = props['ipAssignment']
            if isinstance(ipAssignment, six.string_types):
                self.ipAssignment = (ipAssignment if DMS_IP_ASSIGNMENT.count(ipAssignment) != 0
                                     else DMS_IP_ASSIGNMENT_DHCP)

            staticAddress = None
            if 'staticAddress' in props:
                staticAddress = props['staticAddress']
            if isinstance(staticAddress, dict):
                self.staticAddress = DMSStaticAddress(staticAddress)


_dms_backup_dict = {
    'backupFileNamePrefix': 'backupFileNamePrefix',
    'enabled': 'enabled',
    'encrypt': 'encrypt',
    'intervalDate': 'intervalDate',
    'intervalDays': 'intervalDays',
    'password': 'password',
    'retentionLimit': 'retentionLimit'
}


class DMSBackup(object):
    """The DMSBackup class has the attributes of DMS backup."""

    backupFileNamePrefix = ''
    """The prefix for backup files."""

    enabled = False
    """Whether the backup operation should be performed."""

    encrypt = False
    """Whether the backups should be encrypted."""

    intervalDate = ''
    """The date at which the backup operation should begin - in ISO 8601 format:
    CCYY-MM-DDThh:mm:ss.sssssssssZ (optional 'T')."""

    intervalDays = 1
    """The interval (in days) on which the backup operation should be performed."""

    password = ''
    """The password used to encrypt the backup files."""

    retentionLimit = 1
    """The number of backup files to keep."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSBackup({{'
            f'backupFileNamePrefix: "{self.backupFileNamePrefix}", '
            f'enabled: {self.enabled}, '
            f'encrypt: {self.encrypt}, '
            f'intervalDate: "{self.intervalDate}", '
            f'intervalDays: {self.intervalDays}, '
            f'password: "{self.password}", '
            f'retentionLimit: {self.retentionLimit}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Backup: '
            f'backupFileNamePrefix="{self.backupFileNamePrefix}", '
            f'enabled={self.enabled}, '
            f'encrypt={self.encrypt}, '
            f'intervalDate="{self.intervalDate}", '
            f'intervalDays={self.intervalDays}, '
            f'password="{self.password}", '
            f'retentionLimit={self.retentionLimit}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_backup_dict)


_dms_backup_history_item_dict = {
    'finished': 'finished',
    'location': 'location',
    'started': 'started'
}


class DMSBackupHistoryItem(object):
    """The DMSBackupHistoryItem class has the attributes of a DMS backup operation."""

    finished = ''
    """When the backup operation finished - in ISO 8601 format:
    CCYY-MM-DDThh:mm:ss.sssssssssZ (optional 'T')."""

    location = ''
    """Location of the backup file."""

    started = ''
    """When the backup operation started - in ISO 8601 format:
    CCYY-MM-DDThh:mm:ss.sssssssssZ (optional 'T')."""

    status = DMS_BACKUP_STATUS_SUCCESS
    """Status of the backup operation."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSBackupHistoryItem({{'
            f'finished: "{self.finished}", '
            f'location: "{self.location}", '
            f'started: "{self.started}", '
            f'status: "{self.status}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Backup History Item: '
            f'finished="{self.finished}", '
            f'location="{self.location}", '
            f'started="{self.started}", '
            f'status="{self.status}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_backup_history_item_dict)

        if isinstance(props, dict):
            status = None
            if 'status' in props:
                status = props['status']
            if isinstance(status, six.string_types):
                self.status = (status if DMS_BACKUP_STATUS.count(status) != 0
                               else DMS_BACKUP_STATUS_SUCCESS)


class DMSBackupList(object):
    """The DMSBackupList class has the attributes of a DMS backup list."""

    files = []
    """List of backup files."""

    history = []
    """History of backup operations."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSBackupList({{'
            f'files: [{repr_array(self.files)}], '
            f'history: [{repr_array(self.history)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Backup List: '
            f'files=[{str_array(self.files)}], '
            f'history=[{str_array(self.history)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            files = None
            if 'files' in props:
                files = props['files']
            if isinstance(files, list):
                self.files = []
                for v in files:
                    self.files.append(v)

            history = None
            if 'history' in props:
                history = props['history']
            if isinstance(history, list):
                self.history = []
                for v in history:
                    self.history.append(DMSBackupHistoryItem(v))


class DMSRestoreStatus(object):
    """The DMSRestoreStatus class has the attributes of DMS backup."""

    status = DMS_RESTORE_STATUS_IDLE
    """Status of any restore operation."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSRestoreStatus({{'
            f'status: "{self.status}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Restore Status: '
            f'status="{self.status}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            status = None
            if 'status' in props:
                status = props['status']
            if isinstance(status, six.string_types):
                self.status = (status if DMS_RESTORE_STATUS.count(status) != 0
                               else DMS_RESTORE_STATUS_IDLE)


_dms_restore_dict = {
    'backupFile': 'backupFile',
    'password': 'password',
    'settings': 'settings'
}


class DMSRestore(object):
    """The DMSRestore class has the attributes of a DMS restore operation."""

    backupFile = ''
    """Location of the backup file."""

    password = ''
    """Encryption password for backup file."""

    settings = DMS_RESTORE_SETTINGS_APPLICATION
    """Type of backup operation to perform."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSRestore({{'
            f'backupFile: "{self.backupFile}", '
            f'password: "{self.password}", '
            f'settings: "{self.settings}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Restore: '
            f'backupFile="{self.backupFile}", '
            f'password="{self.password}", '
            f'settings="{self.settings}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_restore_dict)


_dms_backup_restore_sftp_dict = {
    'directory': 'directory',
    'enabled': 'enabled',
    'password': 'password',
    'port': 'port',
    'server': 'server',
    'username': 'username'
}


class DMSBackupRestoreSFTP(object):
    """The DMSBackupRestoreSFTP class has the attributes of SFTP settings for DMS backup/restore."""

    directory = ''
    """Directory to store backup files."""

    enabled = False
    """Whether SFTP settings exist."""

    password = ''
    """Password for SFTP server."""

    port = 0
    """Port for SFTP server."""

    server = ''
    """Address for SFTP server."""

    username = ''
    """Username for SFTP server."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSBackupRestoreSFTP({{'
            f'directory: "{self.directory}", '
            f'enabled: {self.enabled}, '
            f'password: "{self.password}", '
            f'port: {self.port}, '
            f'server: "{self.server}", '
            f'username: "{self.username}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Backup/Restore SFTP: '
            f'directory="{self.directory}", '
            f'enabled={self.enabled}, '
            f'password="{self.password}", '
            f'port={self.port}, '
            f'server="{self.server}", '
            f'username="{self.username}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_backup_restore_sftp_dict)


class DMSBackupRestore(object):
    """The DMSBackupRestore class has the attributes of DMS backup/restore."""

    backup = None
    """Backup information."""

    restore = None
    """Restore information."""

    sftp = None
    """SFTP information."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSBackupRestore({{'
            f'backup: {{{repr(self.backup)}}}, '
            f'restore: {{{repr(self.restore)}}}, '
            f'sftp: {{{repr(self.sftp)}}}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Backup Restore: '
            f'backup={{{str(self.backup)}}}, '
            f'restore={{{str(self.restore)}}}, '
            f'sftp={{{str(self.sftp)}}}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            backup = None
            if 'backup' in props:
                backup = props['backup']
            if isinstance(backup, dict):
                self.backup = DMSBackup(backup)

            restore = None
            if 'restore' in props:
                restore = props['restore']
            if isinstance(restore, dict):
                self.restore = DMSRestore(restore)

            sftp = None
            if 'sftp' in props:
                sftp = props['sftp']
            if isinstance(sftp, dict):
                self.sftp = DMSBackupRestoreSFTP(sftp)


_dms_change_password_dict = {
    'oldPassword': 'oldPassword',
    'password': 'password',
    'username': 'username'
}


class DMSChangePassword(object):
    """The DMSChangePassword class has the attributes of DMS password changing."""

    oldPassword = ''
    """Current password for user."""

    password = ''
    """New password for user."""

    username = ''
    """Username for which to change the password."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSChangePassword({{'
            f'oldPassword: "{self.oldPassword}", '
            f'password: "{self.password}", '
            f'username: "{self.username}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Backup/Restore SFTP: '
            f'oldPassword="{self.oldPassword}", '
            f'password="{self.password}", '
            f'username="{self.username}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_change_password_dict)


_dms_device_name_dict = {
    'deviceName': 'deviceName'
}


class DMSDeviceName(object):
    """The DMSDeviceName class has the attributes of DMS device name changing."""

    deviceName = ''
    """Device name."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSDeviceName({{'
            f'deviceName: "{self.deviceName}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Device Name: '
            f'deviceName="{self.deviceName}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_device_name_dict)


_dms_dhcp_dict = {
    'timeout': 'timeout'
}


class DMSDHCP(object):
    """The DMSDHCP class has the attributes of DMS DHCP settings changing."""

    timeout = 45
    """DHCP timeout."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSDHCP({{'
            f'timeout: {self.timeout}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS DHCP: '
            f'timeout={self.timeout}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_dhcp_dict)


_dms_authentication_server_active_directory_dict = {
    'host': 'host',
    'name': 'name',
    'port': 'port',
    'use': 'use'
}


class DMSAuthenticationServerActiveDirectory(object):
    """The DMSAuthenticationServerActiveDirectory class has the attributes of a DMS authentication
    server for active directory."""

    authentiationType = DMSAutenticaionType.UNKNOWN
    """Type of authentication server."""

    host = ''
    """Host."""

    name = ''
    """Name of authentication server."""

    port = 0
    """Port."""

    use = False
    """Whether the authentication server is in use."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAuthenticationServerActiveDirectory({{'
            f'authenticationType: "{self.authenticationType}", '
            f'host: "{self.host}", '
            f'name: "{self.name}", '
            f'port: {self.port}, '
            f'use: {self.use}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Authentication Server Active Directory: '
            f'authenticationType="{self.authenticationType}", '
            f'host="{self.host}", '
            f'name="{self.name}", '
            f'port={self.port}, '
            f'use={self.use}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_authentication_server_active_directory_dict)

        if isinstance(props, dict):
            auth = props.get('authenticationType')
            if isinstance(auth, int):
                self.authenticationType = (auth if auth in DMSAutenticaionType
                                           else DMSAutenticaionType.UNKNOWN)


_dms_authentication_server_kerberos_dict = {
    'kdc': 'kdc',
    'name': 'name',
    'realm': 'realm',
    'use': 'use'
}


class DMSAuthenticationServerKerberos(object):
    """The DMSAuthenticationServerKerberos class has the attributes of a DMS authentication server
    for Kerberos."""

    authentiationType = DMSAutenticaionType.UNKNOWN
    """Type of authentication server."""

    kdc = ''
    """KDC."""

    name = ''
    """Name of authentication server."""

    realm = ''
    """Realm."""

    use = False
    """Whether the authentication server is in use."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAuthenticationServerKerberos({{'
            f'authenticationType: "{self.authenticationType}", '
            f'kdc: "{self.kdc}", '
            f'name: "{self.name}", '
            f'realm: "{self.realm}", '
            f'use: {self.use}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Authentication Server Kerberos: '
            f'authenticationType="{self.authenticationType}", '
            f'kdc="{self.kdc}", '
            f'name="{self.name}", '
            f'realm="{self.realm}", '
            f'use={self.use}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_authentication_server_kerberos_dict)

        if isinstance(props, dict):
            auth = props.get('authenticationType')
            if isinstance(auth, int):
                self.authenticationType = (auth if auth in DMSAutenticaionType
                                           else DMSAutenticaionType.UNKNOWN)


_dms_authentication_server_local_unknown_dict = {
    'name': 'name',
    'use': 'use'
}


class DMSAuthenticationServerLocalUnknown(object):
    """The DMSAuthenticationServerLocalUnknown class has the attributes of a DMS authentication
    server for local/unknown."""

    authentiationType = DMSAutenticaionType.UNKNOWN
    """Type of authentication server."""

    name = ''
    """Name of authentication server."""

    use = False
    """Whether the authentication server is in use."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAuthenticationServerLocalUnknown({{'
            f'authenticationType: "{self.authenticationType}", '
            f'name: "{self.name}", '
            f'use: {self.use}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Authentication Server Local/Unknown: '
            f'authenticationType="{self.authenticationType}", '
            f'name="{self.name}", '
            f'use={self.use}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_authentication_server_local_unknown_dict)

        if isinstance(props, dict):
            auth = props.get('authenticationType')
            if isinstance(auth, int):
                self.authenticationType = (auth if auth in DMSAutenticaionType
                                           else DMSAutenticaionType.UNKNOWN)


_dms_authentication_server_radius_tacacs_dict = {
    'host': 'host',
    'name': 'name',
    'port': 'port',
    'secret': 'secret',
    'use': 'use'
}


class DMSAuthenticationServerRadiusTacacs(object):
    """The DMSAuthenticationServerRadiusTacacs class has the attributes of a DMS authentication
    server for Radius/Tacacs."""

    authentiationType = DMSAutenticaionType.UNKNOWN
    """Type of authentication server."""

    host = ''
    """Host."""

    name = ''
    """Name of authentication server."""

    port = 0
    """Port."""

    secret = ''
    """Secret."""

    use = False
    """Whether the authentication server is in use."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAuthenticationServerRadiusTacacs({{'
            f'authenticationType: "{self.authenticationType}", '
            f'host: "{self.host}", '
            f'name: "{self.name}", '
            f'port: {self.port}, '
            f'secret: "{self.secret}", '
            f'use: {self.use}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Authentication Server Radius/Tacacs: '
            f'authenticationType="{self.authenticationType}", '
            f'host="{self.host}", '
            f'name="{self.name}", '
            f'port={self.port}, '
            f'secret="{self.secret}", '
            f'use={self.use}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_authentication_server_radius_tacacs_dict)

        if isinstance(props, dict):
            auth = props.get('authenticationType')
            if isinstance(auth, int):
                self.authenticationType = (auth if auth in DMSAutenticaionType
                                           else DMSAutenticaionType.UNKNOWN)


_dms_authentication_servers_dict = {
    'use': 'use'
}


class DMSAuthenticationServers(object):
    """The DMSAuthenticationServers class has the attributes of DMS authentication servers."""

    servers = []
    """List of authentication servers."""

    use = False
    """Whether the 3rd party authentication is in use."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAuthenticationServers({{'
            f'servers: [{repr_array(self.servers)}], '
            f'use: {self.use}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Authentication Servers: '
            f'servers=[{str_array(self.servers)}], '
            f'use={self.use}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_authentication_servers_dict)

        if isinstance(props, dict):
            servers = None
            if 'servers' in props:
                servers = props['servers']
            if isinstance(servers, list):
                self.servers = []
                for v in servers:
                    if isinstance(v, dict):
                        auth = v.get('authenticationType')
                        if isinstance(auth, int):
                            authType = (auth if auth in DMSAutenticaionType
                                        else DMSAutenticaionType.UNKNOWN)

                        if authType == DMSAutenticaionType.ACTIVE_DIRECTORY:
                            self.servers.append(DMSAuthenticationServerActiveDirectory(v))
                        elif authType == DMSAutenticaionType.KERBEROS:
                            self.servers.append(DMSAuthenticationServerKerberos(v))
                        elif (authType == DMSAutenticaionType.LOCAL
                              or authType == DMSAutenticaionType.UNKNOWN):
                            self.servers.append(DMSAuthenticationServerLocalUnknown(v))
                        elif (authType == DMSAutenticaionType.RADIUS
                              or authType == DMSAutenticaionType.TACACS_PLUS):
                            self.servers.append(DMSAuthenticationServerRadiusTacacs(v))


class DMSEngineSettings(object):
    """The DMSEngineSettings class has the attributes of DMS engine settings."""

    authenticationServers = None
    """Authentication servers."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSEngineSettings({{'
            f'authenticationServers: [{repr(self.authenticationServers)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Authentication Server: '
            f'authenticationServers=[{str(self.authenticationServers)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            authenticationServers = None
            if 'authenticationServers' in props:
                authenticationServers = props['authenticationServers']
            if isinstance(authenticationServers, dict):
                self.authenticationServers = DMSAuthenticationServers(authenticationServers)


_dms_hostname_dict = {
    'hostName': 'hostName'
}


class DMSHostname(object):
    """The DMSHostname class has the attributes of DMS hostname."""

    hostName = ''
    """Hostname."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSHostname({{'
            f'hostName: "{self.hostName}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Hostname: '
            f'hostName="{self.hostName}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_hostname_dict)


_dms_license_dict = {
    'expirationDate': 'expirationDate',
    'expired': 'expired',
    'liveFlow': 'liveFlow',
    'liveFlowLimit': 'liveFlowLimit',
    'valid': 'valid'
}


class DMSLicense(object):
    """The DMSLicense class has the attributes of DMS licnese information."""

    expirationDate = ''
    """The expiration date for the license - in ISO 8601 format:
    CCYY-MM-DDThh:mm:ss.sssssssssZ (optional 'T')."""

    expired = False
    """Whether the license is expired."""

    liveFlow = False
    """Whether the Capture Engine supports LiveFlow."""

    liveFlowLimit = 0
    """The number of active flows that can be tracked at one time for LiveFlow
    captures (0 = unlimited).
    """

    type = DMSLicenseType.UNKNOWN
    """Type of license."""

    valid = True
    """Whether the license is valid."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSLicense({{'
            f'expirationDate: "{self.expirationDate}", '
            f'expired: {self.expired}, '
            f'liveFlow: {self.liveFlow}, '
            f'liveFlowLimit: {self.liveFlowLimit}, '
            f'type: "{self.type}", '
            f'valid: {self.valid}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS License: '
            f'expirationDate="{self.expirationDate}", '
            f'expired={self.expired}, '
            f'liveFlow={self.liveFlow}, '
            f'liveFlowLimit={self.liveFlowLimit}, '
            f'type="{self.type}", '
            f'valid={self.valid}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_license_dict)

        if isinstance(props, dict):
            license = props['type']
            if isinstance(license, int):
                self.type = license if license in DMSLicenseType else DMSLicenseType.UNKNOWN


_dms_timezone_dict = {
    'long': 'long',
    'short': 'short'
}


class DMSTimezone(object):
    """The DMSTimezone class has the attributes of DMS timezone information."""

    long = ''
    """The timezone long name."""

    short = ''
    """The timezone short name."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSTimezone({{'
            f'long: "{self.long}", '
            f'short: "{self.short}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Timezone: '
            f'long="{self.long}", '
            f'short="{self.short}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_timezone_dict)


_dms_register_dict = {
    'engineType': 'engineType',
    'engineVersion': 'engineVersion',
    'licenseFile': 'licenseFile',
    'licenseId': 'licenseId',
    'productKey': 'productKey',
    'secret': 'secret',
    'serialNumber': 'serialNumber'
}


class DMSRegister(object):
    """The DMSRegister class has the attributes of a DMS register operation."""

    engineType = ''
    """Engine type."""

    engineVersion = ''
    """Engine version."""

    license = None
    """License information."""

    licenseFile = ''
    """License file data contents."""

    licenseId = ''
    """License ID."""

    productKey = ''
    """Product key."""

    secret = ''
    """MAC address of engine."""

    serialNumber = ''
    """Serial number of engine."""

    timeSettings = []
    """List of timezones."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSRegister({{'
            f'engineType: "{self.engineType}", '
            f'engineVersion: "{self.engineVersion}", '
            f'license: {{{repr(self.license)}}}, '
            f'licenseFile: "{self.licenseFile}", '
            f'licenseId: "{self.licenseId}", '
            f'productKey: "{self.productKey}", '
            f'secret: "{self.secret}", '
            f'serialNumber: "{self.serialNumber}", '
            f'timeSettings: [{repr_array(self.timeSettings)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Register: '
            f'engineType="{self.engineType}", '
            f'engineVersion="{self.engineVersion}", '
            f'license={{{str(self.license)}}}, '
            f'licenseFile="{self.licenseFile}", '
            f'licenseId="{self.licenseId}", '
            f'productKey="{self.productKey}", '
            f'secret="{self.secret}", '
            f'serialNumber="{self.serialNumber}", '
            f'timeSettings=[{str_array(self.timeSettings)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_register_dict)

        if isinstance(props, dict):
            license = None
            if 'license' in props:
                license = props['license']
            if isinstance(license, dict):
                self.license = DMSLicense(license)

            timeSettings = None
            if 'timeSettings' in props:
                timeSettings = props['timeSettings']
            if isinstance(timeSettings, list):
                self.timeSettings = []
                for v in timeSettings:
                    self.timeSettings.append(DMSTimezone(v))


_dms_status_dict = {
    'enabled': 'enabled'
}


class DMSStatus(object):
    """The DMSStatus class has the attributes of DMS status."""

    enabled = False
    """Whether DMS is enabled."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSStatus({{'
            f'enabled: {self.enabled}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Status: '
            f'enabled={self.enabled}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_status_dict)


class DMSGetTimeSettings(object):
    """The DMSGetTimeSettings class has the attributes of getting DMS time settings."""

    currentNtpServers = []
    """List of NTP servers."""

    currentTimeSetting = None
    """Current time zone."""

    timeSettings = []
    """List of timezones."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSGetTimeSettings({{'
            f'currentNtpServers: [{repr_array(self.currentNtpServers)}], '
            f'currentTimeSetting: {{{repr(self.currentTimeSetting)}}}, '
            f'timeSettings: [{repr_array(self.timeSettings)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Get Time Settings: '
            f'currentNtpServers=[{str_array(self.currentNtpServers)}], '
            f'currentTimeSetting={{{str(self.currentTimeSetting)}}}, '
            f'timeSettings=[{str_array(self.timeSettings)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            currentNtpServers = None
            if 'currentNtpServers' in props:
                currentNtpServers = props['currentNtpServers']
            if isinstance(currentNtpServers, list):
                self.currentNtpServers = []
                for v in currentNtpServers:
                    self.currentNtpServers.append(v)

            currentTimeSetting = None
            if 'currentTimeSetting' in props:
                currentTimeSetting = props['currentTimeSetting']
            if isinstance(currentTimeSetting, dict):
                self.currentTimeSetting = DMSTimezone(v)

            timeSettings = None
            if 'timeSettings' in props:
                timeSettings = props['timeSettings']
            if isinstance(timeSettings, list):
                self.timeSettings = []
                for v in timeSettings:
                    self.timeSettings.append(DMSTimezone(v))


class DMSSetTimeSettings(object):
    """The DMSSetTimeSettings class has the attributes of setting DMS time settings."""

    ntpServers = []
    """List of NTP servers."""

    timezone = []
    """List of timezones."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSSetTimeSettings({{'
            f'ntpServers: [{repr_array(self.ntpServers)}], '
            f'timezone: [{repr_array(self.timezone)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Set Time Settings: '
            f'ntpServers=[{str_array(self.ntpServers)}], '
            f'timezone=[{str_array(self.timezone)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            ntpServers = None
            if 'ntpServers' in props:
                ntpServers = props['ntpServers']
            if isinstance(ntpServers, list):
                self.ntpServers = []
                for v in ntpServers:
                    self.ntpServers.append(v)

            timezone = None
            if 'timezone' in props:
                timezone = props['timezone']
            if isinstance(timezone, list):
                self.timezone = []
                for v in timezone:
                    self.timezone.append(v)


_dms_token_dict = {
    'accessToken': 'accessToken',
    'expiresInSeconds': 'expiresInSeconds',
    'notifyInterval': 'notifyInterval',
    'tokenType': 'tokenType'
}


class DMSToken(object):
    """The DMSToken class has the attributes of a DMS token operation."""

    accessToken = ''
    """Access token."""

    expiresInSeconds = 0
    """Time duration of when the token expires (in seconds)."""

    notifyInterval = 0
    """Time duration at which to retry a notify operation."""

    tokenType = ''
    """Token type."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSToken({{'
            f'accessToken: "{self.accessToken}", '
            f'expiresInSeconds: {self.expiresInSeconds}, '
            f'notifyInterval: {self.notifyInterval}, '
            f'tokenType: "{self.tokenType}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Token: '
            f'accessToken="{self.accessToken}", '
            f'expiresInSeconds={self.expiresInSeconds}, '
            f'notifyInterval={self.notifyInterval}, '
            f'tokenType="{self.tokenType}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_token_dict)


_dms_tsr_dict = {
    'message': 'message',
    'tsrFile': 'tsrFile'
}


class DMSTSR(object):
    """The DMSTSR class has the attributes of DMS TSR information."""

    message = ''
    """TSR message."""

    severity = DMSTSRSeverity.WARNING
    """TSR severity."""

    tsrFile = ''
    """TSR log file."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSTSR({{'
            f'message: "{self.message}", '
            f'severity: "{self.severity}", '
            f'tsrFile: "{self.tsrFile}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS TSR: '
            f'message="{self.message}", '
            f'severity="{self.severity}", '
            f'tsrFile="{self.tsrFile}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_tsr_dict)

        if isinstance(props, dict):
            severity = props.get('severity')
            if isinstance(severity, int):
                self.severity = severity if severity in DMSTSRSeverity else DMSTSRSeverity.WARNING


class DMSUpdate(object):
    """The DMSUpdate class has the attributes of DMS update information."""

    updateFiles = []
    """Update files."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSUpdate({{'
            f'updateFiles: [{repr_array(self.updateFiles)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Update: '
            f'updateFiles=[{str_array(self.updateFiles)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            updateFiles = None
            if 'updateFiles' in props:
                updateFiles = props['updateFiles']
            if isinstance(updateFiles, list):
                self.updateFiles = []
                for v in updateFiles:
                    self.updateFiles.append(v)


_dms_engine_version_dict = {
    'engineVersion': 'engineVersion'
}


class DMSEngineVersion(object):
    """The DMSEngineVersion class has the attributes of DMS engine version."""

    engineVersion = ''
    """Engine version."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSEngineVersion({{'
            f'engineVersion: "{self.engineVersion}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Engine Version: '
            f'engineVersion="{self.engineVersion}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_engine_version_dict)


_dms_notify_request_dict = {
    'accessToken': 'accessToken',
    'tokenType': 'tokenType'
}


class DMSNotifyRequest(object):
    """The DMSNotifyRequest class has the attributes of a DMS notification request."""

    accessToken = ''
    """Access token."""

    tokenType = ''
    """Token type."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSNotifyRequest({{'
            f'accessToken: "{self.accessToken}", '
            f'tokenType: "{self.tokenType}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Notify Request: '
            f'accessToken="{self.accessToken}", '
            f'tokenType="{self.tokenType}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_notify_request_dict)


_dms_action_dict = {
    'factoryReset': 'factoryReset',
    'hostName': 'hostName',
    'name': 'name',
    'powerOff': 'powerOff',
    'reboot': 'reboot',
    'status': 'status'
}


class DMSAction(object):
    """The DMSAction class has the attributes of a DMS notification response."""

    address = None
    """The DMS address."""

    backupRestore = None
    """Backup/restore information."""

    changePassword = None
    """Information to change the password."""

    dhcpSettings = None
    """DHCP settings."""

    engineSettings = None
    """Engine settings."""

    factoryReset = False
    """Whether to perform a factory reset."""

    hostName = ''
    """Hostname."""

    name = ''
    """Name."""

    powerOff = False
    """Whether to power off."""

    reboot = False
    """Whether to reboot."""

    status = False
    """Whether to enable DMS."""

    timeSettings = None
    """Time settings."""

    update = None
    """Update information."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAction({{'
            f'address: {{{repr(self.address)}}}, '
            f'backupRestore: {{{repr(self.backupRestore)}}}, '
            f'changePassword: {{{repr(self.changePassword)}}}, '
            f'dhcpSettings: {{{repr(self.dhcpSettings)}}}, '
            f'engineSettings: {{{repr(self.engineSettings)}}}, '
            f'factoryReset: {self.factoryReset}, '
            f'hostName: "{self.hostName}", '
            f'name: "{self.name}", '
            f'powerOff: {self.powerOff}, '
            f'reboot: {self.reboot}, '
            f'status: {self.status}, '
            f'timeSettings: {{{repr(self.timeSettings)}}}, '
            f'update: {{{repr(self.update)}}}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Notify Response: '
            f'address={{{str(self.address)}}}, '
            f'backupRestore={{{str(self.backupRestore)}}}, '
            f'changePassword={{{str(self.changePassword)}}}, '
            f'dhcpSettings={{{str(self.dhcpSettings)}}}, '
            f'engineSettings={{{str(self.engineSettings)}}}, '
            f'factoryReset={self.factoryReset}, '
            f'hostName="{self.hostName}", '
            f'name="{self.name}", '
            f'powerOff={self.powerOff}, '
            f'reboot={self.reboot}, '
            f'status={self.status}, '
            f'timeSettings={{{str(self.timeSettings)}}}, '
            f'update={{{str(self.update)}}}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_action_dict)

        if isinstance(props, dict):
            address = None
            if 'address' in props:
                address = props['address']
            if isinstance(address, dict):
                self.address = DMSAddress(address)

            backupRestore = None
            if 'backupRestore' in props:
                backupRestore = props['backupRestore']
            if isinstance(backupRestore, dict):
                self.backupRestore = DMSBackupRestore(backupRestore)

            changePassword = None
            if 'changePassword' in props:
                changePassword = props['changePassword']
            if isinstance(changePassword, dict):
                self.changePassword = DMSChangePassword(changePassword)

            dhcpSettings = None
            if 'dhcpSettings' in props:
                dhcpSettings = props['dhcpSettings']
            if isinstance(dhcpSettings, dict):
                self.dhcpSettings = DMSDHCP(dhcpSettings)

            engineSettings = None
            if 'engineSettings' in props:
                engineSettings = props['engineSettings']
            if isinstance(engineSettings, dict):
                self.engineSettings = DMSEngineSettings(engineSettings)

            timeSettings = None
            if 'timeSettings' in props:
                timeSettings = props['timeSettings']
            if isinstance(timeSettings, dict):
                self.timeSettings = DMSSetTimeSettings(timeSettings)

            update = None
            if 'update' in props:
                update = props['update']
            if isinstance(update, dict):
                self.update = DMSUpdate(update)


_dms_response_dict = {
    'error': 'error',
    'ok': 'ok'
}


class DMSResponse(object):
    """The DMSResponse class has the attributes of a DMS response."""

    error = ''
    """Error if operation failed."""

    ok = False
    """Whether the operation succeeded."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSResponse({{'
            f'error: "{self.error}", '
            f'ok: {self.ok}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Response: '
            f'error="{self.error}", '
            f'ok={self.ok}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _dms_response_dict)


class DMSActionResponse(object):
    """The DMSActionResponse class has the attributes of a DMS action response."""

    address = None
    """Action response for address operation."""

    backupRestore = None
    """Action response for backup/restore operation."""

    changePassword = None
    """Action response for change password operation."""

    dhcpSettings = None
    """Action response for DHCP settings operation."""

    engineSettings = None
    """Action response for engine settings operation."""

    factoryReset = None
    """Action response for factory reset operation."""

    hostName = None
    """Action response for hostname operation."""

    name = None
    """Action response for name operation."""

    powerOff = None
    """Action response for power off operation."""

    reboot = None
    """Action response for reboot operation."""

    status = None
    """Action response for status operation."""

    timeSettings = None
    """Action response for time settings operation."""

    update = None
    """Action response for update operation."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'DMSAction({{'
            f'address: {{{repr(self.address)}}}, '
            f'backupRestore: {{{repr(self.backupRestore)}}}, '
            f'changePassword: {{{repr(self.changePassword)}}}, '
            f'dhcpSettings: {{{repr(self.dhcpSettings)}}}, '
            f'engineSettings: {{{repr(self.engineSettings)}}}, '
            f'factoryReset: {{{repr(self.factoryReset)}}}, '
            f'hostName: {{{repr(self.hostName)}}}, '
            f'name: {{{repr(self.name)}}}, '
            f'powerOff: {{{repr(self.powerOff)}}}, '
            f'reboot: {{{repr(self.reboot)}}}, '
            f'status: {{{repr(self.status)}}}, '
            f'timeSettings: {{{repr(self.timeSettings)}}}, '
            f'update: {{{repr(self.update)}}}'
            f'}})'
        )

    def __str__(self):
        return (
            f'DMS Notify Response: '
            f'address={{{str(self.address)}}}, '
            f'backupRestore={{{str(self.backupRestore)}}}, '
            f'changePassword={{{str(self.changePassword)}}}, '
            f'dhcpSettings={{{str(self.dhcpSettings)}}}, '
            f'engineSettings={{{str(self.engineSettings)}}}, '
            f'factoryReset={{{str(self.factoryReset)}}}, '
            f'hostName={{{str(self.hostName)}}}, '
            f'name={{{str(self.name)}}}, '
            f'powerOff={{{str(self.powerOff)}}}, '
            f'reboot={{{str(self.reboot)}}}, '
            f'status={{{str(self.status)}}}, '
            f'timeSettings={{{str(self.timeSettings)}}}, '
            f'update={{{str(self.update)}}}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            address = None
            if 'address' in props:
                address = props['address']
            if isinstance(address, dict):
                self.address = DMSResponse(address)

            backupRestore = None
            if 'backupRestore' in props:
                backupRestore = props['backupRestore']
            if isinstance(backupRestore, dict):
                self.backupRestore = DMSResponse(backupRestore)

            changePassword = None
            if 'changePassword' in props:
                changePassword = props['changePassword']
            if isinstance(changePassword, dict):
                self.changePassword = DMSResponse(changePassword)

            dhcpSettings = None
            if 'dhcpSettings' in props:
                dhcpSettings = props['dhcpSettings']
            if isinstance(dhcpSettings, dict):
                self.dhcpSettings = DMSResponse(dhcpSettings)

            engineSettings = None
            if 'engineSettings' in props:
                engineSettings = props['engineSettings']
            if isinstance(engineSettings, dict):
                self.engineSettings = DMSResponse(engineSettings)

            factoryReset = None
            if 'factoryReset' in props:
                factoryReset = props['factoryReset']
            if isinstance(factoryReset, dict):
                self.factoryReset = DMSResponse(factoryReset)

            hostName = None
            if 'hostName' in props:
                hostName = props['hostName']
            if isinstance(hostName, dict):
                self.hostName = DMSResponse(hostName)

            name = None
            if 'name' in props:
                name = props['name']
            if isinstance(name, dict):
                self.name = DMSResponse(name)

            powerOff = None
            if 'powerOff' in props:
                powerOff = props['powerOff']
            if isinstance(powerOff, dict):
                self.powerOff = DMSResponse(powerOff)

            reboot = None
            if 'reboot' in props:
                reboot = props['reboot']
            if isinstance(reboot, dict):
                self.reboot = DMSResponse(reboot)

            status = None
            if 'status' in props:
                status = props['status']
            if isinstance(status, dict):
                self.status = DMSResponse(status)

            timeSettings = None
            if 'timeSettings' in props:
                timeSettings = props['timeSettings']
            if isinstance(timeSettings, dict):
                self.timeSettings = DMSResponse(timeSettings)

            update = None
            if 'update' in props:
                update = props['update']
            if isinstance(update, dict):
                self.update = DMSResponse(update)


class DMS(object):
    """The DMS class is an interface into DMS operations."""

    engine = None
    """OmniEngine interface."""

    def __init__(self, engine):
        self.engine = engine

    def __repr__(self):
        return f'DMS({repr(self.engine)})'

    def __str__(self):
        return 'DMS'

    def dms(self, dms: DMSAction) -> Union[DMSActionResponse, None]:
        """Performs a DMS action"""
        if self.engine is not None:
            command = 'dms/'
            pr = self.engine.perf('dms')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(dms, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform DMS action.')
            return DMSActionResponse(resp)
        return None

    def get_dms_address(self) -> Union[DMSAddress, None]:
        """Gets the engine address information"""
        if self.engine is not None:
            command = 'dms/address/'
            pr = self.engine.perf('get_dms_address')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get engine address information.')
            return DMSAddress(resp)
        return None

    def set_dms_address(self, address: DMSAddress) -> Union[dict, None]:
        """Sets the engine address information"""
        if self.engine is not None:
            command = 'dms/address/'
            pr = self.engine.perf('set_dms_address')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(address, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set engine address information.')
            return resp
        return None

    def get_dms_backup(self) -> Union[DMSBackup, None]:
        """Gets the DMS backup settings"""
        if self.engine is not None:
            command = 'dms/backup-restore/backup/'
            pr = self.engine.perf('get_dms_backup')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DMS backup settings.')
            return DMSBackup(resp)
        return None

    def set_dms_backup(self, backup: DMSBackup) -> Union[dict, None]:
        """Sets the DMS backup settings"""
        if self.engine is not None:
            command = 'dms/backup-restore/backup/'
            pr = self.engine.perf('set_dms_backup')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(backup, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set DMS backup settings.')
            return resp
        return None

    def get_dms_backup_list(self) -> Union[DMSBackupList, None]:
        """Gets the DMS backup list"""
        if self.engine is not None:
            command = 'dms/backup-restore/backup-list/'
            pr = self.engine.perf('get_dms_backup_list')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DMS backup list.')
            return DMSBackupList(resp)
        return None

    def get_dms_restore_status(self) -> Union[DMSRestoreStatus, None]:
        """Gets the DMS restore status"""
        if self.engine is not None:
            command = 'dms/backup-restore/restore/'
            pr = self.engine.perf('get_dms_restore_status')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DMS restore status.')
            return DMSRestoreStatus(resp)
        return None

    def dms_restore(self, restore: DMSRestore) -> Union[dict, None]:
        """Performs a DMS restore"""
        if self.engine is not None:
            command = 'dms/backup-restore/restore/'
            pr = self.engine.perf('dms_restore')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(restore, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform DMS restore.')
            return resp
        return None

    def get_dms_backup_restore_sftp(self) -> Union[DMSBackupRestoreSFTP, None]:
        """Gets the DMS backup/restore SFTP settings"""
        if self.engine is not None:
            command = 'dms/backup-restore/sftp/'
            pr = self.engine.perf('get_dms_backup_restore_sftp')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DMS backup/restore SFTP settings.')
            return DMSBackupRestoreSFTP(resp)
        return None

    def set_dms_backup_restore_sftp(self, sftp: DMSBackupRestoreSFTP) -> Union[dict, None]:
        """Sets the DMS backup/restore SFTP settings"""
        if self.engine is not None:
            command = 'dms/backup-restore/sftp/'
            pr = self.engine.perf('set_dms_backup_restore_sftp')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(sftp, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set DMS backup/restore SFTP settings.')
            return resp
        return None

    def dms_change_password(self, password: DMSChangePassword) -> Union[dict, None]:
        """Changes the password for the given username"""
        if self.engine is not None:
            command = 'dms/change-password/'
            pr = self.engine.perf('dms_change_password')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(password, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to change password.')
            return resp
        return None

    def get_dms_device_name(self) -> Union[DMSDeviceName, None]:
        """Gets the device name"""
        if self.engine is not None:
            command = 'dms/device-name/'
            pr = self.engine.perf('get_dms_device_name')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get device name.')
            return DMSDeviceName(resp)
        return None

    def set_dms_device_name(self, deviceName: DMSDeviceName) -> Union[dict, None]:
        """Sets the device name"""
        if self.engine is not None:
            command = 'dms/device-name/'
            pr = self.engine.perf('set_dms_device_name')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(deviceName, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set device name.')
            return resp
        return None

    def get_dms_dhcp(self) -> Union[DMSDHCP, None]:
        """Gets the DHCP settings"""
        if self.engine is not None:
            command = 'dms/dhcp/'
            pr = self.engine.perf('get_dms_dhcp')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DHCP settings.')
            return DMSDHCP(resp)
        return None

    def set_dms_dhcp(self, dhcp: DMSDHCP) -> Union[dict, None]:
        """Sets the DHCP settings"""
        if self.engine is not None:
            command = 'dms/dhcp/'
            pr = self.engine.perf('set_dms_dhcp')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(dhcp, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set DHCP settings.')
            return resp
        return None

    def get_dms_engine_settings(self) -> Union[DMSEngineSettings, None]:
        """Gets the engine settings"""
        if self.engine is not None:
            command = 'dms/engine-settings/'
            pr = self.engine.perf('get_dms_engine_settings')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get engine settings.')
            return DMSEngineSettings(resp)
        return None

    def set_dms_engine_settings(self, settings: DMSEngineSettings) -> Union[dict, None]:
        """Sets the engine settings"""
        if self.engine is not None:
            command = 'dms/engine-settings/'
            pr = self.engine.perf('set_dms_engine_settings')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(settings, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set engine settings.')
            return resp
        return None

    def dms_factory_reset(self) -> Union[dict, None]:
        """Performs a factory reset"""
        if self.engine is not None:
            command = 'dms/factory-reset/'
            pr = self.engine.perf('dms_factory_reset')
            resp = self.engine._issue_command(command, pr, EO.POST, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform factory reset.')
            return resp
        return None

    def get_dms_hostname(self) -> Union[DMSHostname, None]:
        """Gets the hostname"""
        if self.engine is not None:
            command = 'dms/host-name/'
            pr = self.engine.perf('get_dms_hostname')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get hostname.')
            return DMSHostname(resp)
        return None

    def set_dms_hostname(self, hostname: DMSHostname) -> Union[dict, None]:
        """Sets the hostname"""
        if self.engine is not None:
            command = 'dms/host-name/'
            pr = self.engine.perf('set_dms_hostname')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(hostname, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set hostname.')
            return resp
        return None

    def dms_notify(self, notify: DMSToken) -> Union[DMSAction, None]:
        """Performs a DMS notification action"""
        if self.engine is not None:
            command = 'dms/notify/'
            pr = self.engine.perf('dms_notify')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(notify, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform DMS notification action.')
            return DMSAction(resp)
        return None

    def dms_power_off(self) -> Union[dict, None]:
        """Powers off the engine"""
        if self.engine is not None:
            command = 'dms/power-off/'
            pr = self.engine.perf('dms_power_off')
            resp = self.engine._issue_command(command, pr, EO.POST, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform power off.')
            return resp
        return None

    def dms_reboot(self) -> Union[dict, None]:
        """Reboots the engine"""
        if self.engine is not None:
            command = 'dms/reboot/'
            pr = self.engine.perf('dms_reboot')
            resp = self.engine._issue_command(command, pr, EO.POST, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform reboot.')
            return resp
        return None

    def dms_register(self) -> Union[DMSRegister, None]:
        """Performs a DMS registration action"""
        if self.engine is not None:
            command = 'dms/register/'
            pr = self.engine.perf('dms_register')
            resp = self.engine._issue_command(command, pr, EO.POST, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform DMS register action.')
            return DMSRegister(resp)
        return None

    def get_dms_status(self) -> Union[DMSStatus, None]:
        """Gets the DMS status"""
        if self.engine is not None:
            command = 'dms/status/'
            pr = self.engine.perf('get_dms_status')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DMS status.')
            return DMSStatus(resp)
        return None

    def dms_enable(self) -> Union[dict, None]:
        """Enables DMS"""
        if self.engine is not None:
            command = 'dms/status/'
            pr = self.engine.perf('dms_enable')
            resp = self.engine._issue_command(command, pr, EO.POST, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to enable DMS.')
            return resp
        return None

    def dms_disable(self) -> Union[dict, None]:
        """Disables DMS"""
        if self.engine is not None:
            command = 'dms/status/'
            pr = self.engine.perf('dms_disable')
            resp = self.engine._issue_command(command, pr, EO.DELETE, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to disable DMS.')
            return resp
        return None

    def get_dms_time_settings(self) -> Union[DMSGetTimeSettings, None]:
        """Gets the DMS time settings"""
        if self.engine is not None:
            command = 'dms/time-settings/'
            pr = self.engine.perf('get_dms_time_settings')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get DMS time settings.')
            return DMSGetTimeSettings(resp)
        return None

    def set_dms_time_settings(self, timeSettings: DMSSetTimeSettings) -> Union[dict, None]:
        """Sets the DMS time settings"""
        if self.engine is not None:
            command = 'dms/time-settings/'
            pr = self.engine.perf('set_dms_time_settings')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(timeSettings, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to set DMS time settings.')
            return resp
        return None

    def dms_token(self) -> Union[DMSToken, None]:
        """Performs a DMS token action"""
        if self.engine is not None:
            command = 'dms/token/'
            pr = self.engine.perf('dms_token')
            resp = self.engine._issue_command(command, pr, EO.POST, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to perform DMS token action.')
            return DMSToken(resp)
        return None

    def dms_tsr(self, tsr: DMSTSR) -> Union[dict, None]:
        """Sends TSR information to DMS"""
        if self.engine is not None:
            command = 'dms/tsr/'
            pr = self.engine.perf('dms_tsr')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(tsr, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to send TSR information to DMS.')
            return resp
        return None

    def dms_update(self, update: DMSUpdate) -> Union[dict, None]:
        """Updates the engine"""
        if self.engine is not None:
            command = 'dms/update/'
            pr = self.engine.perf('dms_update')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(update, cls=OmniScriptEncoder),
                                              dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to update the engine.')
            return resp
        return None

    def get_dms_version(self) -> Union[DMSEngineVersion, None]:
        """Gets the engine version"""
        if self.engine is not None:
            command = 'dms/version/'
            pr = self.engine.perf('dms_version')
            resp = self.engine._issue_command(command, pr, EO.GET, dms=True)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get engine version.')
            return DMSEngineVersion(resp)
        return None

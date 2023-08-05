"""EngineStatus class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .omniid import OmniId
from .peektime import PeekTime


_engine_prop_dict = {
    'adapterCount': 'adapter_count',
    'address': 'address',
    'alarmCount': 'alarm_count',
    'alarmsModificationTime': 'alarm_modification_time',
    'captureInfo': 'capture_info_list',
    'captures': 'capture_count',
    'captureSessionCount': 'capture_session_count',
    'cpuCount': 'cpu_count',
    'cpuType': 'cpu_type',
    'customSettings': 'custom_settings',
    'dataDriveFormat': 'data_drive_format',
    'dataFolder': 'data_directory',
    'decryptionKeyCount': 'decryption_key_count',
    'diskReservedSpace': 'disk_reserved_space',
    'enginesModificationTime': 'modification_time',
    'engineType': 'engine_type',
    'fileCount': 'file_count',
    'fileVersion': 'file_version',
    'filterCount': 'filter_count',
    'filtersModificationTime': 'filters_modification_time',
    'forensicSearches': 'forensic_search_count',
    'forensicSearchReservedSpace': 'forensic_search_reserved_space',
    'graphCount': 'graph_count',
    'hardwareProfileCount': 'hardware_profile_count',
    'hardwareType': 'hardware_type',
    'hostName': 'host',
    'ipmiAddr': 'ipmi_address',
    'licensed': 'is_licensed',
    'licenseExpirationDate': 'license_expiration_date',
    'licenseExpired': 'is_license_expired',
    'licenseType': 'license_type',
    'logTotalCount': 'log_total_count',
    'memoryAvailablePhysical': 'memory_available_physical',
    'memoryTotalPhysical': 'memory_total_physical',
    'name': 'name',
    'nameCount': 'name_table_count',
    'namesModificationTime': 'names_modification_time',
    'nativeProtospecsEnabled': 'is_native_protospecs_enabled',
    'notificationCount': 'notification_count',
    'notificationsModificationTime': 'notifications_modification_time',
    'operatingSystem': 'operating_system',
    'os': 'os',
    'platform': 'platform',
    'productVersion': 'product_version',
    'protocolTranslationCount': 'protocol_translation_count',
    'protospecsVersion': 'protospecs_version',
    'securityEventsTotalCount': 'security_events_total_count',
    'serialNumber': 'serial_number',
    'storageTotal': 'storage_total',
    'storageUsed': 'storage_used',
    'time': 'time',
    'timeZoneBias': 'time_zone_bias',
    'uptime': 'uptime',
    'userDomain': 'user_domain',
    'userId': 'user_id',
    'userName': 'user_name'
}


# def _ parse _ prop (a, v):
#     result = None
#     if a == 'storage_free_space':
#         result = []
#         for i in v.split(';'):
#             k, v = i.strip(' ').split(' ', 1)
#             # 69.4 GB -> 74,517,053,440 bytes
#             cnt, unt, fs = v.split(' ', 2)
#             cnt = float(cnt) * BYTES_PER_KILOBYTE       # 1.23 -> 1230.0
#             cnt = int(cnt)                              # -> 1230 kB
#             if unt == 'MB':
#                 cnt = cnt * KILOBYTES_PER_MEGABYTE
#             elif unt == 'GB':
#                 cnt = cnt * KILOBYTES_PER_GIGABYTE
#             elif unt == 'TB':
#                 cnt = cnt * KILOBYTES_PER_TERABYTE
#             result.append([k, cnt, fs])
#     return result


class CaptureInfo(object):
    """Information about a Capture object.
    object.
    """

    id = None
    """Capture Id of the Capture."""

    allocated = 0
    """Number of bytes of storage allocated for the capture."""

    used = 0
    """Number of bytes of the allocated storage used."""

    def __init__(self, props=None):
        self._load(props)

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            value = props.get('value')
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == 'id':
                        setattr(self, k, OmniId(v))
                    elif k == 'allocated':
                        setattr(self, k, v)
                    elif k == 'used':
                        setattr(self, k, v)


class EngineStatus(object):
    """The Status of an
    :class:`OmniEngine <omniscript.omniengine.OmniEngine>`
    object.
    """

    adapter_count = 0
    """The number of adapters on the system."""

    address = None
    """The OmniEngine's IP Address or host name."""

    alarm_count = 0
    """The number of alarms configured on the OmniEngine."""

    alarm_modification_time = None
    """The time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    of the last modification to the alarms."""

    capture_info_list = []
    """Information about the captures on the Engine."""

    capture_count = 0
    """The number of Captures created on the OmniEngine."""

    capture_session_count = 0
    """The number of Capture Session on the OmniEngine."""

    cpu_count = 0
    """The number of CPUs on the OmniEngine."""

    cpu_type = ''
    """The model of CPU on the OmniEngine."""

    custom_settings = 0
    """The number of custom settings."""

    data_drive_format = ''
    """The format of the data drive."""

    data_directory = ''
    """The default data directory of the OmniEngine."""

    decryption_key_count = 0
    """The number of decryption keys."""

    disk_reserved_space = 0
    """The amount of space, in bytes, reserved for the
    Operation System.
    """

    engine_type = ''
    """The type of OmniEngine: OmniEngine Enterprise..."""

    file_count = 0
    """The number of Packet files in the OmniEngine's database."""

    file_version = ''
    """The File Version property of the OmniEngine."""

    filter_count = 0
    """The number of Filters on the OmniEngine."""

    filters_modification_time = None
    """The last time, as a
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    the Filters where modified."""

    forensic_search_count = 0
    """The number of Forensic Searches on the OmniEngine."""

    forensic_search_reserved_space = 0
    """The amount of disk space, in bytes, reserved for
    Forensice Searches.
    """

    graph_count = 0
    """The number of Graphs on the OmniEngine."""

    hardware_profile_count = 0
    """The number of hardware profiles on the OmniEngine."""

    hardware_type = ''
    """The hardware type name."""

    host = ''
    """The IP Address or name of the OmniEngine's host system."""

    ipmi_address = ''
    """The IPMI IP Address."""

    is_license_expired = True
    """Has the OmniEngine's license xpired?"""

    is_licensed = False
    """Is the engine licensed?"""

    is_native_protospecs_enabled = False
    """Are the Native Protospecs Enabled?"""

    license_expiration_date = None
    """The date, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    the OmniEngine's license expires."""

    license_type = 0
    """The index of the OmniEngines license type."""

    log_total_count = 0
    """The total number of Log entires in the OmniEngine Event Log."""

    memory_available_physical = 0
    """The amount of physical memory in bytes available on
    the system.
    """

    memory_total_physical = 0
    """The amount of physical memory in bytes on the system."""

    modification_time = None
    """The last time the OmniEngine was modified"""

    name = ''
    """The name of the OmniEngine."""

    name_table_count = 0
    """The number of Name Table entires (need to confirm) on the
    OmniEngine."""

    name_table_modification_time = None
    """The time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    the Names Table was modified."""

    notification_count = 0
    """The number of Notifications on the OmniEngine."""

    notifications_modification_time = None
    """The last time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    the Notifications were modified."""

    operating_system = ''
    """The full name of the Operating System that the OmniEngine is
    running on.
    """

    os = ''
    """The short name of the Operating System that the OmniEngine is
    running on: Windows or Linux.
    """

    platform = 'localhost'
    """The platform of the system, Windows only: x64, win32."""

    port = 0
    """The TCP Port of the connection to the host system."""

    product_version = ''
    """The Product Version property of the OmniEngine."""

    protocol_translation_count = 0
    """The number of Protocol Translations."""

    protospecs_version = ''
    """The OmniEngine's version as a dotted string of numbers."""

    security_events_total_count = 0
    """The total number of Events in the Security Log."""

    serial_number = ""
    """The OmniEngine's Serial Number as a string."""

    storage_available = 0
    """The amount of disk storage in bytes available on the system."""

    storage_total = 0
    """The total amount of disk storage in bytes on the system."""

    storage_used = 0
    """The amount of disk storage in bytes used on the system."""

    time = None
    """The current time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    of day in UTC on the system."""

    time_zone_bias = 0
    """The time zone bias, in minutes, of the system."""

    uptime = 0
    """The number of nanoseconds the OmniEngine has been running."""

    user_domain = ''
    """The Domain of the User's account."""

    user_id = ''
    """The User's Id."""

    user_name = ''
    """The User's account name."""

    def __init__(self, engine, props=None):
        self._engine = engine
        self.logger = engine.logger

        self.adapter_count = EngineStatus.adapter_count
        self.address = EngineStatus.address
        self.alarm_count = EngineStatus.alarm_count
        self.alarm_modification_time = EngineStatus.alarm_modification_time
        self.capture_count = EngineStatus.capture_count
        self.capture_info_list = EngineStatus.capture_info_list
        self.capture_session_count = EngineStatus.capture_session_count
        self.cpu_count = EngineStatus.cpu_count
        self.cpu_type = EngineStatus.cpu_type
        self.data_directory = EngineStatus.data_directory
        self.data_drive_format = EngineStatus.data_drive_format
        self.decryption_key_count = EngineStatus.decryption_key_count
        self.disk_reserved_space = EngineStatus.disk_reserved_space
        self.engine_type = EngineStatus.engine_type
        self.file_count = EngineStatus.file_count
        self.file_version = EngineStatus.file_version
        self.filter_count = EngineStatus.filter_count
        self.filters_modification_time = EngineStatus.filters_modification_time
        self.forensic_search_count = EngineStatus.forensic_search_count
        self.forensic_search_reserved_space = EngineStatus.forensic_search_reserved_space
        self.graph_count = EngineStatus.graph_count
        self.hardware_profile_count = EngineStatus.hardware_profile_count
        self.hardware_type = EngineStatus.hardware_type
        self.host = EngineStatus.host
        self.ipmi_address = EngineStatus.ipmi_address
        self.is_license_expired = EngineStatus.is_license_expired
        self.is_licensed = EngineStatus.is_licensed
        self.is_native_protospecs_enabled = EngineStatus.is_native_protospecs_enabled
        self.license_expiration_date = EngineStatus.license_expiration_date
        self.license_type = EngineStatus.license_type
        self.log_total_count = EngineStatus.log_total_count
        self.memory_available_physical = EngineStatus.memory_available_physical
        self.memory_total_physical = EngineStatus.memory_total_physical
        self.modification_time = EngineStatus.modification_time
        self.name = EngineStatus.name
        self.name_table_count = EngineStatus.name_table_count
        self.name_table_modification_time = EngineStatus.name_table_modification_time
        self.notification_count = EngineStatus.notification_count
        self.notifications_modification_time = EngineStatus.notifications_modification_time
        self.operating_system = EngineStatus.operating_system
        self.os = EngineStatus.os
        self.platform = EngineStatus.platform
        self.port = EngineStatus.port
        self.product_version = EngineStatus.product_version
        self.protocol_translation_count = EngineStatus.protocol_translation_count
        self.protospecs_version = EngineStatus.protospecs_version
        self.security_events_total_count = EngineStatus.security_events_total_count
        self.serial_number = EngineStatus.serial_number
        self.storage_total = EngineStatus.storage_total
        self.storage_used = EngineStatus.storage_used
        self.time = EngineStatus.time
        self.time_zone_bias = EngineStatus.time_zone_bias
        self.uptime = EngineStatus.uptime
        self.user_domain = EngineStatus.user_domain
        self.user_id = EngineStatus.user_id
        self.user_name = EngineStatus.user_name

        # Initialize calculated values
        self.storage_available = EngineStatus.storage_available

        # Set provided values
        self.host = engine.host
        self.port = engine.port
        # Parse the dictionary.
        self._load(props)

    def __str__(self):
        return f'EngineStatus: {self.name}'

    def _create_capture_info_list(self, props):
        """Return a list of CaptureInfo objects."""
        lst = []
        if isinstance(props, dict):
            capture_list = props.get('properties')
            if isinstance(capture_list, list):
                for ci in capture_list:
                    lst.append(CaptureInfo(ci))
        return lst

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = _engine_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if isinstance(getattr(self, a), six.string_types):
                        setattr(self, a, v if v else '')
                    elif isinstance(getattr(self, a), int):
                        setattr(self, a, int(v) if v else 0)
                    elif isinstance(getattr(self, a), list):
                        if a in ('capture_info_list'):
                            setattr(self, a, self._create_capture_info_list(v))
                    elif isinstance(getattr(self, a), dict):
                        setattr(self, a, v)
                    elif getattr(self, a) is None:
                        if a in ('address'):
                            setattr(self, a, v)
                        elif a in ('alarm_modification_time', 'filters_modification_time',
                                   'modification_time', 'license_expiration_date',
                                   'notifications_modification_time', 'time'):
                            setattr(self, a, PeekTime(v))
                        else:
                            setattr(self, a, v)
                    else:
                        setattr(self, a, v)
            self.cpu_type = ' '.join(self.cpu_type.split())
            self.storage_available = (self.storage_total - self.storage_used
                                      if self.storage_total > self.storage_used else 0)

    def refresh(self):
        """Refresh the attributes of this object."""
        props = self._engine._issue_command("status/")
        if props:
            self.__init__(self._engine, props)
            return True
        return False

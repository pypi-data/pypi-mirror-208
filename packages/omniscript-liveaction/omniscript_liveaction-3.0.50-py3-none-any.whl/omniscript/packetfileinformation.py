"""PacketFileInformation class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .omniid import OmniId
from .peektime import PeekTime


class PacketFileInformation(object):
    """Information about a Packet File.
    """

    """The name of the Adapter the packets where captured on."""
    adapter_name = ''

    """The name of the address the packets where captured on."""
    adapter_address = ''

    """The OmniId of the capture the packets are from."""
    capture_id = None

    """The name of the capture the packets are from."""
    capture_name = ''

    """The index of the file."""
    file_index = 0

    """The link Speed of the adapter where the packets where captured."""
    link_speed = 0

    """The Media Type of the Adapter."""
    media_type = 0

    """The Media Sub Type of the Adapter."""
    media_sub_type = 0

    """The name of the file."""
    name = ''

    """The account name of the file's owner."""
    owner = ''

    """The number of packets in the file."""
    packet_count = 0

    """The fully qualifed path and file name of the file."""
    path = ''

    """The start time of the capture session."""
    session_start_time = None

    """The end time of the capture session."""
    session_end_time = None

    """the size in bytes of the file."""
    size = 0

    """The Status of the file."""
    status = 0

    """The time zone bias of the session times."""
    time_zone_bias = 0

    # Tags
    _json_adapter_address = 'AdapterAddr'
    _json_adapter_name = 'AdapterName'
    _json_capture_id = 'CaptureID'
    _json_capture_name = 'CaptureName'
    _json_file_index = 'FileIndex'
    _json_link_speed = 'LinkSpeed'
    _json_media_type = 'MediaType'
    _json_media_sub_type = 'MediaSubType'
    _json_owner = 'Owner'
    _json_name = 'FileName'
    _json_packet_count = 'PacketCount'
    _json_path = 'PartialPath'
    _json_session_start_time = 'SessionStartTime'
    _json_session_end_time = 'SessionEndTime'
    _json_size = 'FileSize'
    _json_status = 'Status'
    _json_time_zone_bias = 'TimeZoneBias'

    _tag_adapter_name = 'adapter_name'
    _tag_adapter_address = 'adapter_address'
    _tag_capture_id = 'capture_id'
    _tag_capture_name = 'capture_name'
    _tag_file_index = 'file_index'
    _tag_link_speed = 'link_speed'
    _tag_media_type = 'media_type'
    _tag_media_sub_type = 'media_sub_type'
    _tag_name = 'name'
    _tag_owner = 'owner'
    _tag_packet_count = 'packet_count'
    _tag_path = 'path'
    _tag_session_start_time = 'session_start_time'
    _tag_session_end_time = 'session_end_time'
    _tag_size = 'size'
    _tag_status = 'status'
    _tag_time_zone_bias = 'time_zone_bias'

    _pfi_prop_dict = {
        _json_adapter_name: _tag_adapter_name,
        _json_adapter_address: _tag_adapter_address,
        _json_capture_id: _tag_capture_id,
        _json_capture_name: _tag_capture_name,
        _json_file_index: _tag_file_index,
        _json_link_speed: _tag_link_speed,
        _json_media_type: _tag_media_type,
        _json_media_sub_type: _tag_media_sub_type,
        _json_name: _tag_name,
        _json_owner: _tag_owner,
        _json_packet_count: _tag_packet_count,
        _json_path: _tag_path,
        _json_session_start_time: _tag_session_start_time,
        _json_session_end_time: _tag_session_end_time,
        _json_size: _tag_size,
        _json_status: _tag_status,
        _json_time_zone_bias: _tag_time_zone_bias
    }

    def __init__(self, props=None):
        self.adapter_address = PacketFileInformation.adapter_name
        self.adapter_name = PacketFileInformation.adapter_address
        self.capture_id = PacketFileInformation.capture_id
        self.capture_name = PacketFileInformation.capture_name
        self.file_index = PacketFileInformation.file_index
        self.name = PacketFileInformation.name
        self.link_speed = PacketFileInformation.link_speed
        self.media_type = PacketFileInformation.media_type
        self.media_sub_type = PacketFileInformation.media_sub_type
        self.owner = PacketFileInformation.owner
        self.packet_count = PacketFileInformation.packet_count
        self.path = PacketFileInformation.path
        self.session_start_time = PacketFileInformation.session_start_time
        self.session_end_time = PacketFileInformation.session_end_time
        self.size = PacketFileInformation.size
        self.status = PacketFileInformation.status
        self.time_zone_bias = PacketFileInformation.time_zone_bias
        self._load(props)

    def _load(self, props):
        """Load the File Informaiont from a dictionary."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = PacketFileInformation._pfi_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if a == PacketFileInformation._tag_adapter_address:
                        self.adapter_address = v
                    elif a == PacketFileInformation._tag_adapter_name:
                        self.adapter_name = v
                    elif a == PacketFileInformation._tag_capture_id:
                        self.capture_id = OmniId(v)
                    elif a == PacketFileInformation._tag_capture_name:
                        self.capture_name = v
                    elif a == PacketFileInformation._tag_file_index:
                        self.file_index = int(v)
                    elif a == PacketFileInformation._tag_link_speed:
                        self.link_speed = int(v)
                    elif a == PacketFileInformation._tag_media_type:
                        self.media_type = int(v)
                    elif a == PacketFileInformation._tag_media_sub_type:
                        self.media_sub_type = int(v)
                    elif a == PacketFileInformation._tag_name:
                        self.name = v
                    elif a == PacketFileInformation._tag_owner:
                        self.owner = v
                    elif a == PacketFileInformation._tag_packet_count:
                        self.packet_count = int(v)
                    elif a == PacketFileInformation._tag_path:
                        self.path = v
                    elif a == PacketFileInformation._tag_session_start_time:
                        self.session_start_time = PeekTime(v)
                    elif a == PacketFileInformation._tag_session_end_time:
                        self.session_end_time = PeekTime(v)
                    elif a == PacketFileInformation._tag_size:
                        self.size = int(v)
                    elif a == PacketFileInformation._tag_status:
                        self.status = int(v)
                    elif a == PacketFileInformation._tag_time_zone_bias:
                        self.time_zone_bias = int(v)

    def __str__(self):
        return f'PacketFileInformation: {self.name}'


def _create_packet_file_information_list(props):
    lst = []
    if isinstance(props, dict):
        rows = props['rows']
        if isinstance(rows, list):
            for row in rows:
                lst.append(PacketFileInformation(props=row))
    return lst


def file_information_list_to_file_list(fil):
    """Transform a list of
    :class:`PacketFileInformation <omniscript.packetfileinformation.PacketFileInformation>`
    into a list of strings of fully qualified file names.
    """
    fl = []
    path = ''
    for f in fil:
        if f.is_directory():
            path = f.name
        else:
            fl.append(path + f.name)
    return fl

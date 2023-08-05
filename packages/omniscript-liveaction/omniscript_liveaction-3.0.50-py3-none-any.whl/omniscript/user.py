"""User class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

# import json
# import six
from typing import List, Union

try:
    from omniengine import OmniEngine
except ImportError:
    import sys
    OmniEngine = sys.modules[__package__ + '.omniengine']

from .omniport import OmniPort
from .peektime import PeekTime

from .omniaddress import parse_ip_address

_json_account = 'account'
_json_address = 'ipAddress'
_json_description = 'description'
_json_domain = 'domain'
_json_end_time = 'endTime'
_json_name = 'name'
_json_port = 'port'
_json_security_id = 'sid'
_json_start_time = 'startTime'


class User(object):
    """The User class has the attributes of an engine connected user."""

    address = None
    """IP address from which user connected."""

    description = ''
    """Description of the user."""

    domain = ''
    """Domain of the user."""

    end_time = None
    """Last time the user connected."""

    name = ''
    """User name."""

    port = None
    """Port over which user connected."""

    security_id = ''
    """The User's security id."""

    start_time = None
    """First time the user connected."""

    is_connected = None
    """Is this User Account connected to the engine."""

    def __init__(self, props=None, connected: Union[bool, None] = None):
        self.address = User.address
        self.description = User.description
        self.domain = User.domain
        self.end_time = User.end_time
        self.name = User.name
        self.port = User.port
        self.security_id = User.security_id
        self.start_time = User.start_time
        self.is_connected = connected
        self._load(props)

    def __repr__(self):
        return (
            f'User({{'
            f'name: "{self.name}"'
            f'{f", address: {self.address}" if self.address is not None else ""}'
            f'{f", description: {self.description}" if self.description else ""}'
            f'{f", domain: {self.domain}" if self.domain else ""}'
            f'{f", start_time: {self.start_time}" if self.start_time is not None else ""}'
            f'{f", end_time: {self.end_time}" if self.end_time is not None else ""}'
            f'{f", is_connected: {self.is_connected}" if self.is_connected is not None else ""}'
            f'}})'
        )

    def __str__(self):
        address = (f'{self.address}{f":{self.port}" if self.port is not None else ""}'
                   if self.address else None)
        start_time = f'{self.start_time.iso_time()}' if self.address else None
        return (
            f'User:'
            f' name="{self.name}"'
            f'{f", address: {address}" if address is not None else ""}'
            f'{f", description: {self.description}" if self.description else ""}'
            f'{f", domain: {self.domain}" if self.domain else ""}'
            f'{f", start_time: {start_time}" if start_time is not None else ""}'
            f'{f", end_time: {self.end_time.iso_time()}" if self.end_time else ""}'
            f'{f", is_connected: {self.is_connected}" if self.is_connected is not None else ""}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == _json_address:
                self.address = parse_ip_address(v) if v else None
            elif k == _json_description:
                self.description = v if v else ''
            elif k == _json_domain:
                self.domain = v if v else ''
            elif k == _json_end_time:
                self.end_time = PeekTime(v) if v else None
            elif k == _json_account or k == _json_name:
                self.name = v if v else ''
            elif k == _json_port:
                self.port = OmniPort(v) if v else None
            elif k == _json_security_id:
                self.security_id = v if v else ''
            elif k == _json_start_time:
                self.start_time = PeekTime(v) if v else None

    @classmethod
    def get_connected_user_list(cls, engine: OmniEngine):
        """Gets the connected user list"""
        pr = engine.perf('get_connected_users')
        command = 'connected-users/'
        resp = engine._issue_command(command, pr)
        return _create_user_list(resp, True)

    @classmethod
    def get_user_list(cls, engine: OmniEngine):
        """Gets the user list"""
        if engine is not None:
            command = 'user-list/'
            pr = engine.perf('get_user_list')
            resp = engine._issue_command(command, pr)
            return _create_user_list(resp)
        return None


def _create_user_list(resp: dict, connected: Union[bool, None] = None) -> List[User]:
    lst = []
    users = resp.get('users')
    if isinstance(users, list):
        lst = [User(p, connected) for p in users]
    else:
        users = resp.get('userList')
        if isinstance(users, list):
            lst = [User(p, connected) for p in users]
        if lst:
            sys_info = resp.get('systemInfo')
            if isinstance(sys_info, dict):
                dm = sys_info.get('domainMember')
                if dm:
                    domain = sys_info.get('name')
                    if domain:
                        for u in lst:
                            u.domain = domain
    lst.sort(key=lambda x: x.name)
    return lst

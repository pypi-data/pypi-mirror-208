"""RemoteEngine class.
"""
# Copyright (c) LiveAction, Inc. 2022-2023. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

# Allow get() to use RemoteEngine as an parameter type hint.
from __future__ import annotations

import json

from typing import List, Union

try:
    from omniengine import OmniEngine
except ImportError:
    import sys
    OmniEngine = sys.modules[__package__ + '.omniengine']

from .helpers import load_native_props_from_dict, is_success
from .invariant import EngineOperation as EO
from .omniid import OmniId


_remote_engine_dict = {
    'group': 'group',
    'host': 'host',
    'id': 'id',
    'lastLogin': 'last_login',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'name': 'name',
    'password': 'password',
    'remoteName': 'remote_name',
    'username': 'user_name'
}


class RemoteEngine(object):
    """The RemoteEngine class has the attributes of a remote engine."""

    group = ''
    """Engine group."""

    host = ''
    """Engine host."""

    id = ''
    """Engine id."""

    last_login = None
    """Time of last login (In ISO 8601 format: CCYY-MM-DDThh:mm:ssZ)."""

    latitude = 0.0
    """Latitude of engine."""

    longitude = 0.0
    """Longitude of engine."""

    name = ''
    """Engine name."""

    password = ''
    """Engine password."""

    remote_name = ''
    """Engine name."""

    user_name = ''
    """Engine username."""

    find_attributes = ('name', 'id')

    _engine = None
    """The OmniEngine this RemoteEngine is from."""

    def __init__(self, engine: OmniEngine, props: Union[dict, None] = None):
        self._engine = engine
        self.group = RemoteEngine.group
        self.host = RemoteEngine.host
        self.id = RemoteEngine.id
        self.last_login = RemoteEngine.last_login
        self.latitude = RemoteEngine.latitude
        self.longitude = RemoteEngine.longitude
        self.name = RemoteEngine.name
        self.password = RemoteEngine.password
        self.remote_name = RemoteEngine.remote_name
        self.user_name = RemoteEngine.user_name
        self._load(props)

    def __repr__(self) -> str:
        return (
            f'RemoteEngine({{'
            f'group: "{self.group}", '
            f'host: "{self.host}", '
            f'id: "{self.id}", '
            f'last_login: "{self.last_login}", '
            f'latitude: {self.latitude}, '
            f'longitude: {self.longitude}, '
            f'name: "{self.name}", '
            f'password: "{self.password}", '
            f'remote_name: "{self.remote_name}", '
            f'user_name: "{self.user_name}"'
            f'}})'
        )

    def __str__(self) -> str:
        return (
            f'Remote Engine: '
            f'group="{self.group}", '
            f'host="{self.host}", '
            f'id="{self.id}", '
            f'last_login="{self.lastLogin}", '
            f'latitude={self.latitude}, '
            f'longitude={self.longitude}, '
            f'name="{self.name}", '
            f'password="{self.password}", '
            f'remote_name="{self.remoteName}", '
            f'user_name="{self.username}"'
        )

    def _load(self, props: Union[dict, None]):
        """Set attributes from a dictionary."""
        load_native_props_from_dict(self, props, _remote_engine_dict)

    def _store(self) -> str:
        """Return attributes as a string."""
        props = {
            'group': self.group,
            'host': self.host,
            'id': str(self.id),
            'lastLogin': str(self.last_login) if self.last_login else None,
            'latitude': self.latitude if self.latitude else None,
            'longitude': self.longitude if self.longitude else None,
            'name': self.name,
            'password': self.password,
            'remoteName': self.remote_name,
            'username': self.user_name,
        }
        return props

    @classmethod
    def add(cls, engine: OmniEngine,
            engines: Union[List[RemoteEngine, OmniId, str], RemoteEngine, OmniId, str]):
        if engine and engines:
            lst = engines if isinstance(engines, list) else [engines]
            _engines = [e for e in lst]
            for e in _engines:
                e.last_login = ""

            props = {
                'engines': [eng._store() for eng in _engines]
            }
            data = json.dumps(props)
            pr = engine.perf('add_remote_engine')
            resp = engine._issue_command('engines/', pr, EO.POST, data=data)
            return is_success(resp)

    @classmethod
    def get(cls, engine: OmniEngine, id: Union[RemoteEngine, OmniId, str]):
        if engine and id:
            props = cls._imp_get(engine, id)
            return cls(engine, props)

    @classmethod
    def get_all(cls, engine: OmniEngine):
        if engine:
            pr = engine.perf('get_engines')
            resp = engine._issue_command('engines/', pr)
            return _create_remote_engine_list(engine, resp)

    @staticmethod
    def delete(engine: OmniEngine,
               ids: Union[List[RemoteEngine, OmniId, str], RemoteEngine, OmniId, str]):
        """Delete one or more RemoteEngines from the OmniEngine."""
        if engine and ids:
            _ids = ids if isinstance(ids, list) else [ids]
            lst = [id.id if isinstance(id, RemoteEngine) else OmniId(id) for id in _ids]
            return [RemoteEngine._imp_delete(engine, id) for id in lst]

    @staticmethod
    def delete_all(engine: OmniEngine):
        """Delete all RemoteEngines from the OmniEngine."""
        if engine:
            pr = engine.perf('delete_all_remote_egines')
            engine._issue_command('engines/', pr, EO.DELETE)

    @staticmethod
    def update(engine: OmniEngine, remote: RemoteEngine):
        """Update the RemoteEngine on the OmniEngine."""
        props = {
            'engines': [
                remote._store()
            ]
        }
        data = json.dumps(props)
        pr = engine.perf('update_remote_engine')
        command = f'engines/{remote.id}/'
        resp = engine._issue_command(command, pr, EO.PUT, data=data)
        return is_success(resp)

    @staticmethod
    def _imp_delete(engine: OmniEngine, id: Union[RemoteEngine, OmniId, str]):
        _id = id.id if isinstance(id, RemoteEngine) else OmniId(id)
        if engine and _id:
            pr = engine.perf('delete_remote_egine')
            command = f'engines/{_id}/'
            resp = engine._issue_command(command, pr, EO.DELETE)
            return is_success(resp)

    @classmethod
    def _imp_get(cls, engine: OmniEngine, id: Union[RemoteEngine, OmniId, str]) -> dict:
        if engine and id:
            _id = id.id if isinstance(id, RemoteEngine) else OmniId(id)
            pr = engine.perf('get_remote_egine')
            command = f'engines/{_id}/'
            return engine._issue_command(command, pr)

    def refresh(self) -> None:
        """Refresh the attributes"""
        props = RemoteEngine._imp_get(self._engine, self.id)
        self._load(props)


def _create_remote_engine_list(engine: OmniEngine, props: dict) -> Union[List[RemoteEngine], None]:
    """Create a list of RemoteEngine object from a dictionary."""
    lst = []
    if isinstance(props, dict):
        engines = props.get('engines')
        if isinstance(engines, list):
            lst = [RemoteEngine(engine, props) for props in engines] if engines is not None else lst
            lst.sort(key=lambda x: x.name)
    return lst


def find_remote_engine(engines: List[RemoteEngine, OmniId, str],
                       value, attrib=RemoteEngine.find_attributes[0]) -> Union[RemoteEngine, None]:
    """Finds the first RemoteEngine in a list of RemoteEngines with the
    provided value.
    """
    if not engines or not hasattr(RemoteEngine, attrib):
        return None

    if len(engines) == 0:
        return None

    _value, _attrib = (value.id, 'id') if isinstance(value, RemoteEngine) else (value, attrib)
    return next((i for i in engines if getattr(i, _attrib) == _value), None)

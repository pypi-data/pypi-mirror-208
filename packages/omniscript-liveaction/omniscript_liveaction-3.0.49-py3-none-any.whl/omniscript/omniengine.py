"""OmniEngine class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import os
import json
import requests
import six
import time

from pathlib import PurePath, PurePosixPath
from typing import List, Optional, Union

import omniscript

from .alarm import Alarm
from .adapter import Adapter
from .analysismodule import AnalysisModule
from .auditlog import AuditLog
from .authenticationtoken import AuthenticationToken
from .capabilities import Capabilities
from .capture import Capture
from .capturesession import CaptureSession
from .capturetemplate import CaptureTemplate
from .decryptionkey import DecryptionKey
from .decryptionkeytemplate import DecryptionKeyTemplate
from .directory import Directory
from .enginestatus import EngineStatus
from .enginesettings import EngineSettings, SetSettingsResponse
from .expertpreferences import ExpertPreferences
from .eventlog import EventLog, EventLogEntry
from .fileinformation import FileInformation
from .filter import Filter
from .forensicsearch import ForensicSearch
from .forensictemplate import ForensicTemplate
from .helpers import OmniScriptEncoder
from .invariant import (DatabaseOperation, Diagnostics, EngineOperation as EO,
                        EngineDataFormat as DF, TraceLogLevel)
from .license import License, LicenseSettings
from .liveflow import (LiveFlow, LiveFlowConfiguration, LiveFlowConfigurationResponse,
                       LiveFlowContext, LiveFlowStatus)
from .nametable import NameTable
from .notifications import Notifications, NotificationActions, SendEmailResponse
from .omnierror import OmniError
from .omniid import OmniId
from .peektime import PeekTime
from .performancelogger import PerformanceLogger
from .protocol import Protocol
from .protocoltranslation import ProtocolTranslation as PT
from .remoteengine import RemoteEngine
from .selection import Selection
from .user import User

from .adapter import _create_adapter_list, find_adapter
from .adapterinformation import _create_adapter_information_list
from .alarm import _create_alarm_list
from .analysismodule import _create_analysis_module_list
from .application import _create_application_list
from .authenticationtoken import _create_authentication_token_list
from .capture import _create_capture_list, find_capture
from .capturesession import _create_capture_session_list
from .capturetemplate import _create_capture_template_list
from .country import _create_country_list
from .decryptionkey import _create_decryption_key_list, find_decryption_key
# from .directory import _create_file_system
# from .fileinformation import _create_file_information_list
from .filter import _create_filter_list, find_filter
from .forensicsearch import _create_forensic_search_list, find_forensic_search
from .graphtemplate import _create_graph_template_list
from .helpers import is_almost_success, is_success
from .invariant import DEFAULT_CONNECTION_TIMEOUT, DEFAULT_PORT, DEFAULT_REQUEST_TIMEOUT
from .packetfileinformation import PacketFileInformation, _create_packet_file_information_list
from .protocol import _create_protocol_list
from .protocoltranslation import _create_protocol_translations_list

ENGINECONFIG = '/etc/omni/engineconfig.xml'
OMNI_CONF = '/etc/omni/omni.conf'
CTD_RATIO = 75

find_attributes = ('name', 'id')

_tag_results = 'results'

jtrue = 'true'
jfalse = 'false'


def jbool(b):
    """Returns 'true' if 'b' is True else 'false'.
    """
    return jtrue if b else jfalse


def _capture_id_list(captures):
    """Returns a list of OmniId.
    """
    capturelist = captures if isinstance(captures, list) else [captures]
    ids = []
    for c in capturelist:
        if isinstance(c, six.string_types):
            id = OmniId(c)
            if id != OmniId.null_id:
                ids.append(id)
        elif isinstance(c, OmniId):
            ids.append(c)
        elif isinstance(c, Capture):
            ids.append(c.id)
        else:
            raise TypeError("capture must be or contain a GUID.")
    return ids


def _capture_session_list(session):
    """Returns a list of session ids.
    """
    session_list = session if isinstance(session, list) else [session]
    lst = []
    for s in session_list:
        if isinstance(s, (int, six.string_types)):
            lst.append(int(s))
        elif isinstance(s, CaptureSession):
            lst.append(s.session_id)
        else:
            raise TypeError(
                'session must be or contain an integer session id.')
    return lst


def _capture_decryption_key_list(keys):
    """Returns a list of session ids.
    """
    key_list = keys if isinstance(keys, list) else [keys]
    lst = []
    for s in key_list:
        if isinstance(s, (int, six.string_types)):
            lst.append(OmniId(s))
        elif isinstance(s, DecryptionKey):
            lst.append(s.id)
        elif isinstance(s, DecryptionKeyTemplate):
            lst.append(s.id)
        else:
            raise TypeError(
                'decryption key must be or contain an integer decryption key id.')
    return lst


def _capture_template_list(template):
    """Returns a list of template ids.
    """
    template_list = template if isinstance(template, list) else [template]
    lst = []
    for t in template_list:
        if isinstance(t, (int, six.string_types)):
            lst.append(OmniId(t))
        elif isinstance(t, CaptureTemplate):
            lst.append(t.id)
        else:
            raise TypeError(
                'template must be or contain an integer template id.')
    return lst


class EngineTimeouts(object):
    """The Timeouts for an OmniEngine."""

    connection = DEFAULT_CONNECTION_TIMEOUT
    """The HTTP Connection timeout value in seconds.
    The numeric value may be an integer or float."""

    request = DEFAULT_REQUEST_TIMEOUT
    """The HTTP Request timeout value in seconds.
    The numeric value may be an integer or float."""

    def __init__(self, value: Optional[Union['EngineTimeouts', str, list]] = None,
                 request: Optional[Union[int, float, str]] = None):
        self.connection = EngineTimeouts.connection
        self.request = EngineTimeouts.request
        self._load(value, request)

    def __str__(self):
        return f'Connection: {self.connection}, Request: {self.request}'

    def _load(self, args: Union['EngineTimeouts', str, list],
              request: Optional[Union[int, float, str]]):
        if args is None:
            return
        if isinstance(args, EngineTimeouts):
            self.set_connection(args.connection)
            self.set_request(args.request)
        elif isinstance(args, six.string_types):
            if args.lower() == 'off' or args.lower() == 'none':
                self.connection = None
                self.request = None
            else:
                c, r = args.split()
                self.set_connection(c)
                self.set_request(r)
        elif isinstance(args, list):
            if len(args) >= 2:
                self.set_connection(args[0])
                self.set_request(args[1])
        elif isinstance(args, (int, float, str)) and isinstance(request, (int, float, str)):
            self.set_connection(args)
            self.set_request(request)

    def as_tuple(self):
        if self.connection is None and self.request is None:
            return None
        return (self.connection, self.request)

    def set_connection(self, value: Union[int, float, str]):
        connection = float(value.strip(', /(/)')) if isinstance(value, six.string_types) else value
        if connection is not None and connection >= 0.0:
            self.connection = float(connection)

    def set_request(self, value: Union[int, float, str]):
        request = float(value.strip(', /(/)')) if isinstance(value, six.string_types) else value
        if request is not None and request >= 0.0:
            self.request = float(request)


class OmniEngine(object):
    """The OmniEngine class provides access to an OmniEngie.
    The function
    :func:`create_engine() <omniscript.omniscript.OmniScript.create_engine>`
    returns an OmniEngine object.
    Then use the function
    :func:`login() <omniscript.omniscript.OmniEngine.login>`
    to enter user credentials to login to the engine.
    """

    logger = None
    """The logging object for the engine."""

    host = ''
    """The address of the host system."""

    port = DEFAULT_PORT
    """The port, https (443)."""

    timeout = EngineTimeouts()
    """The default timeout, in milliseconds, for issuing commands.
    The default is 10 minutes.
    """

    _omni = None
    """The parent OmniScript object of self."""

    _base_url = ''
    """The base URL for the REST API."""

    _base_dms_url = ''
    """The base URL for the REST API."""

    _session = None
    """The HTTP Session for the REST API."""

    _connected = False
    """Is the client connected and logged in?"""

    _last_status = None
    """The last EngineStatus object. Cached for performance."""

    _file_system = None
    """The file system of the host system. A tree of Directory object"""

    _perf_logger = None
    """The engine's Performance Log file."""

    def __init__(self, omni, host: str = 'localhost', port: int = DEFAULT_PORT,
                 secure: bool = True, timeouts: Optional[Union[EngineTimeouts, str, list]] = None):
        self._omni = omni
        self.logger = omni.logger
        self.host = host if host else 'localhost'
        self.port = port if port else OmniEngine.port
        self.timeouts = EngineTimeouts(timeouts)
        self._connected = False
        self._last_status = None
        self._file_system = Directory(self, 'root')
        self._perf_logger = OmniEngine._perf_logger

        # if isinstance(self.host, (OmniAddress, IPv4Address, IPv6Address)):
        #     _host = self.host.format()
        # else:
        #     _host = self.host

        # if isinstance(self.port, OmniPort):
        #     _port = self.port.port
        # else:
        #     _port = int(port)

        # _base_url must end with a '/'.
        # _base_dms_url must end with a '/'.
        protocol = 'https' if secure else 'http'
        self._base_url = f'{protocol}://{self.host}:{int(self.port)}/api/v1/'
        self._base_dms_url = f'{protocol}://{self.host}:{int(self.port)}/dms/v1/'
        self._session = requests.Session()
        self._session.keep_alive = True

    def __repr__(self) -> str:
        return f'OmniEngine: {self.name}'

    def __str__(self) -> str:
        return f'OmniEngine: {self.name}'

    @property
    def name(self):
        return self._last_status.name if self._last_status else 'OmniEngine'

    def _operate_url(self, operation, url, params=None, data=None):
        if operation == EO.GET:
            return self._session.get(url, verify=False, params=params, data=data,
                                     timeout=self.timeouts.as_tuple())
        elif operation == EO.POST:
            return self._session.post(url, verify=False, params=params, data=data,
                                      timeout=self.timeouts.as_tuple())
        elif operation == EO.PUT:
            return self._session.put(url, verify=False, params=params, data=data,
                                     timeout=self.timeouts.as_tuple())
        elif operation == EO.DELETE:
            return self._session.delete(url, verify=False, params=params, data=data,
                                        timeout=self.timeouts.as_tuple())
        return None

    def _pr_operate_url(self, pr, operation, url, params=None, data=None):
        resp = None
        if operation == EO.GET:
            pr.start = PeekTime()
            resp = self._session.get(
                url, verify=False, params=params, data=data, timeout=self.timeouts.as_tuple())
            pr.end = PeekTime()
        elif operation == EO.POST:
            pr.start = PeekTime()
            resp = self._session.post(
                url, verify=False, params=params, data=data, timeout=self.timeouts.as_tuple())
            pr.end = PeekTime()
        elif operation == EO.PUT:
            pr.start = PeekTime()
            resp = self._session.put(
                url, verify=False, params=params, data=data, timeout=self.timeouts.as_tuple())
            pr.end = PeekTime()
        elif operation == EO.DELETE:
            pr.start = PeekTime()
            resp = self._session.delete(
                url, verify=False, params=params, data=data, timeout=self.timeouts.as_tuple())
            pr.end = PeekTime()
        return resp

    def _retry_operate_url(self, operation, url, params=None, data=None):
        retries = 3
        resp = self._operate_url(operation, url, params, data)
        while (resp.status_code == 503) and (retries > 0):
            time.sleep(1)
            retries -= 1
            resp = self._operate_url(operation, url)
        return resp

    def _pr_retry_operate_url(self, pr, operation, url, params=None, data=None):
        retries = 3
        resp = self._pr_operate_url(pr, operation, url, params, data)
        while (resp.status_code == 503) and (retries > 0):
            time.sleep(1)
            retries -= 1
            resp = self._pr_operate_url(pr, operation, url)
        return resp

    def _issue_command(self, command, pr=None, operation=EO.GET,
                       format=DF.JSON, params=None, data=None, dms=False):
        """Issue the command and return the response data.
        The OmniEngine object must have a connection to an OmniEngine.

        Args:
            command (str): the command to issue.

        Returns:
            Success: response data or None on failure.
        """
        _text = None
        if self.is_connected:
            if format == DF.JSON:
                self._session.headers.update({'accept': 'application/json'})
            elif format == DF.PLAIN:
                self._session.headers.update({'accept': 'text/plain'})
            elif format == DF.HTML:
                self._session.headers.update({'accept': 'text/html'})
            elif format == DF.TAG_STREAM:
                self._session.headers.update(
                    {'accept': 'application/octet-stream'})
            else:
                raise OmniError('Unrecognized format parameter.')
            # TODO: refactor out the dms test.
            url = self._base_url + command if not dms else self._base_dms_url + command
            if pr:
                resp = self._pr_retry_operate_url(
                    pr, operation, url, params=params, data=data)
            else:
                resp = self._retry_operate_url(
                    operation, url, params=params, data=data)

            if format != DF.JSON:
                self._session.headers.update({'accept': 'application/json'})

            if resp is None:
                raise OmniError('REST API Command failed: Invalid operation.')
            if resp.status_code == 200 or resp.status_code == 201:
                if format == DF.JSON:
                    _text = json.loads(resp.text)
                elif format == DF.TAG_STREAM:
                    _text = resp.text.encode()
                else:
                    _text = resp.text
            elif resp.status_code == 204:
                _text = {'results': [0]}
            elif resp.status_code == 503:
                # 503 - Service temporarily unavailable
                raise OmniError('REST API Command failed: '
                                f'{resp.status_code}: {resp.reason}.')
            else:
                raise OmniError(
                    f'REST API Command failed: {resp.status_code}', code=resp.status_code)
        return _text

    def add_alarm(self, alarm: Alarm):
        """ Add a new alarm to the OmniEngine
        """
        if not isinstance(alarm, Alarm):
            raise ValueError('An Alarm object is required.')
        pr = self.perf('add_alarm')
        data = json.dumps(alarm._store())
        return self._issue_command(f'{Alarm._endpoint}{alarm.id.format()}/', pr, EO.PUT, data=data)

    def add_capture_template(self, template):
        """Add a Capture Template to the OmniEngine.

        Return:
            bool: True on success, False on failure.
        """
        if isinstance(template, CaptureTemplate):
            t = template.store(encapsulate=True)
        else:
            raise ValueError('A CaptureTemplate is required.')
        pr = self.perf('add_capture_template')
        resp = self._issue_command('capture-templates/', pr, EO.POST, data=t)
        return is_success(resp)

    def add_decryption_key_templates(self, key_template):
        """Add one or more Decryption Key Templates to the OmniEngine.

        Return:
            bool: True on success, False on failure.
        """
        key_template_props = []
        key_templates = [key_template] if isinstance(
            key_template, DecryptionKeyTemplate) else key_template

        if not isinstance(key_templates, list):
            raise TypeError(
                "The decryption key templates parameter must be a DecryptionKeyTemplate or a list.")
        for _key_template in key_templates:
            if isinstance(_key_template, DecryptionKeyTemplate):
                props = _key_template._store()
                key_template_props.append(props)

        req_props = {
            'keys': key_template_props
        }
        pr = self.perf('add_decryption_key_templates')

        data = json.dumps(req_props)
        self._issue_command('decryption-keys/', pr, EO.POST, data=data)
        return None

    def add_events(self, events):
        """Add one or more entries to the OmniEngine's Event Log.

        Args:
            event (EventLogEntry or a list of EventLogEntry):
        """
        evt_props = []
        _events = [events] if isinstance(events, EventLogEntry) else events
        if not isinstance(_events, list):
            raise TypeError(
                "The events parameter must be an EventLogEntry or a list.")
        for evt in _events:
            if isinstance(evt, EventLogEntry):
                props = {
                    'longMessage': '',
                    'severity': evt.severity,
                    'shortMessage': evt.message,
                    'sourceId': str(OmniId.null_id),
                    'sourceKey': 0
                }
                if isinstance(evt.capture_id, OmniId):
                    props['contextId'] = evt.capture_id.format()
                if isinstance(evt.timestamp, PeekTime):
                    props['timestamp'] = evt.timestamp.iso_time()
                evt_props.append(props)
        req_props = {
            'events': evt_props
        }
        pr = self.perf('add_events')
        data = json.dumps(req_props)
        resp = self._issue_command('events/', pr, EO.PUT, data=data)
        return resp

    def add_filter(self, omnifilter):
        """Add one to the engine's filter set.

        Args:
            omnifilter (str, Filter): the filter to add.
        """
        item = None
        if isinstance(omnifilter, six.string_types):
            item = Filter(criteria=omnifilter)
        elif isinstance(omnifilter, Filter):
            item = omnifilter
        else:
            raise TypeError('omnifilter must be or contain a Filter.')

        pr = self.perf('add_filter')
        props = item._store()
        cmd = f'filters/{item.id.format()}'
        resp = self._issue_command(cmd, pr, EO.PUT, data=props)
        if not is_success(resp):
            raise OmniError('Failed to add filter.')
        return self.get_filter(item.id)

    def add_remote_engine(self, ids: List[RemoteEngine]):
        """Add one or more RemoteEngines to the OmniEngine."""
        return RemoteEngine.add(self, ids)

    def convert_filter_string(self, filter: str, validate: bool = False) -> Optional[Filter]:
        """ Convert a filter string to a filter object and return the object and error status """
        ret = None
        pr = self.perf('convert_filter_string')
        params = {'validateOnly': jbool(validate)}
        resp = self._issue_command(
            'filter-convert/', pr, EO.POST, params=params, data=filter)

        if isinstance(resp, dict):
            if 'filter' in resp:
                ret = Filter(criteria=resp['filter'])

        return ret

    def create_capture(self, template):
        """Create a new Capture from a
        :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
        object.

        Args:
            template(str or
            :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
            ): the capture template.

        Returns:
            A :class:`Capture <omniscript.capture.Capture>`
            object of the new capture or None.
        """
        if isinstance(template, six.string_types):
            ct = template
        elif isinstance(template, CaptureTemplate):
            ct = template.store(self, True)
        pr = self.perf('create_capture')
        cmd = 'captures/'
        resp = self._issue_command(cmd, pr, EO.POST, data=ct)
        if not resp:
            raise OmniError('Failed to create capture.')
        if isinstance(resp, dict):
            if 'id' in resp:
                id = resp['id']
                cl = self.get_capture_list()
                return find_capture(cl, id, 'id')
        return None

    def create_directory(self, directory: str) -> None:
        """Creates a new directory on the engine."""
        Directory.create(self, directory)

    def create_file(self, file: str) -> Optional[dict]:
        """Create a file on the engine, if the file exists its content
        will be discarded.
        """
        params = {
            'path': file
        }
        pr = self.perf('create_file')
        self._issue_command('create-file/', pr, EO.POST, params=params)

    def create_forensic_search(self, template):
        """Create a new Forensic Search from a
        :class:`ForensicTemplate
        <omniscript.forensictemplate.ForensicTemplate>`
        object.

        Args:
            template(str or
            :class:`ForensicTemplate
            <omniscript.forensictemplate.ForensicTemplate>`
            ): the settings of the search.

        Returns:
            A :class:`ForensicSearch
            <omniscript.forensicsearch.ForensicSearch>`
            object or None."""
        if isinstance(template, six.string_types):
            fst = template
        elif isinstance(template, ForensicTemplate):
            fst = template.store(self, True)
        pr = self.perf('create_forensic_search')
        cmd = 'forensic-searches/'
        resp = self._issue_command(cmd, pr, EO.POST, data=fst)
        if not resp:
            raise OmniError('Failed to create Forensic Search.')
        if isinstance(resp, dict):
            if 'id' in resp:
                id = resp['id']
                return self.get_forensic_search(id)
        return None

    def create_token(self, token: AuthenticationToken) -> Optional[dict]:
        """ Create a new authentication token with the given template """
        resp = None
        if isinstance(token, AuthenticationToken):
            pr = self.perf('create_token')
            data = json.dumps(token._create_template())
            resp = self._issue_command(
                AuthenticationToken.endpoint, pr, EO.POST, data=data)

            if not resp:
                raise OmniError('Failed to create authentication token')

        return resp if isinstance(resp, dict) else None

    def delete_adapter(self, adapter: Union[Adapter, OmniId, str]):
        """ Delete the specified adapter from the engine. """
        id = adapter.adapter_id if isinstance(adapter, Adapter) else adapter
        pr = self.perf('delete_adapter')
        command = f'{Adapter._endpoint}/{str(id)}/'
        props = self._issue_command(command, pr, EO.DELETE)
        if not is_success(props):
            raise OmniError('Delete Adapter failed')

    def delete_alarm(self, alarm_id: Union[Alarm, OmniId, str]):
        """ Delete the specified alarm in the list """
        _id = alarm_id.id if isinstance(alarm_id, Alarm) else OmniId(alarm_id)
        pr = self.perf('delete_alarm')
        props = self._issue_command(f'{Alarm._endpoint}{_id.format()}', pr, EO.DELETE)
        if not is_success(props):
            raise OmniError('Delete Alarm failed')

    def delete_all_audit_log(self):
        """Delete all messages in the OmniEngine's Audit Log.
        """
        pr = self.perf('delete_all_audit_log')
        props = self._issue_command('audit-log/', pr, EO.DELETE)
        if not is_success(props):
            raise OmniError('Delete all Audit Log Messages failed.')

    def delete_all_capture_sessions(self):
        """ Delete all the Capture Sessions from the engine.

        Note that 'Capture Sessions' are different from Captures.
        See the Details tab at the bottom of an OmniEngine's
        Forensics tab.
        """
        pr = self.perf('delete_all_capture_sessions')
        props = self._issue_command('capture-sessions/', pr, EO.DELETE)
        if not is_success(props):
            raise OmniError('Faild to delete all Capture Sessions.')

    def delete_all_filters(self):
        """ Delete all the Filters from the engine.
        """
        pr = self.perf('delete_all_filters')
        props = self._issue_command('filters/', pr, EO.DELETE)
        if not is_success(props):
            raise OmniError('Failed to delete all Filters.')

    def delete_all_forensic_searches(self):
        """ Delete all the Forensic Searches from the engine.
        """
        pr = self.perf('delete_all_forensic_searches')
        props = self._issue_command('forensic-searches/', pr, EO.DELETE)
        # if there are no Forensic Searches, then {return:[]} is returned.
        if not is_almost_success(props):
            raise OmniError('Failed to delete all Forensic Searches')

    def delete_all_remote_engines(self):
        """ Delete all the RemoteEngines from the engine."""
        RemoteEngine.delete_all(self)

    def delete_capture(self, capture, retry=3):
        """Delete a Capture from the OmniEngine.

        Args:
            capture (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Capture <omniscript.capture.Capture>`
            ): the capture's id or a Capture object.
            Or a list of captures.
        """
        ids = _capture_id_list(capture)
        for id in ids:
            pr = self.perf('delete_capture')
            cmd = f'captures/{id.format()}'
            props = self._issue_command(cmd, pr, EO.DELETE)
            if not is_success(props):
                raise OmniError('Failed to delete Capture')

    def delete_capture_session(self, session):
        """Deletes Capture Sessions from the OmniEngine.

        Args:
            session (int, str,
            :class:`CaptureSession <omniscript.capturesession.CaptureSession>`
            ): the session's id or a CaptureSession object.
            Or a list of sessions.
        """
        ids = _capture_session_list(session)
        for id in ids:
            pr = self.perf('delete_capture_session')
            cmd = f'capture-sessions/{id}'
            props = self._issue_command(cmd, pr, EO.DELETE)
            if not is_success(props):
                raise OmniError('Failed to delete Capture Session')

    def delete_capture_template(self, template):
        """Deletes Capture Templates from the OmniEngine.

        Args:
            template (int, str,
            :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
            ): the template's id or a CaptureTemplate object.
            Or a list of templates.
        """
        ids = _capture_template_list(template)
        for id in ids:
            pr = self.perf('delete_capture_template')
            cmd = f'capture-templates/{id.format()}'
            props = self._issue_command(cmd, pr, EO.DELETE)
            if not is_success(props):
                raise OmniError('Failed to delete Capture Template.')

    def delete_decryption_keys(self, decryptkey: list):
        """Deletes Decryption Keys from the OmniEngine.
        """
        _ids = _capture_decryption_key_list(decryptkey)
        req_props = []
        for _id in _ids:
            req_props.append(('ids', _id))
        if not req_props:
            raise TypeError('No decryption key specified.')

        pr = self.perf('delete_decryption_keys')
        cmd = 'decryption-keys/'
        resp = self._issue_command(cmd, pr, EO.DELETE, params=req_props)

        if not is_almost_success(resp):
            raise OmniError('Failed to delete Decryption Keys')

    def delete_directory(self, directory: str) -> None:
        """Delete/remove a directory from the engine."""
        Directory.delete(self, directory)

    def delete_event_log(self, capture=None, compact=False):
        """Delete the OmniEngine's Event Log.

        Args:
            capture (OmniId, str, Capture, CaptureSession):
            Delete the entries for just this 'capture'.
            compact (bool): compact the Event Log after deleting
            entries.
        """
        if isinstance(capture, OmniId):
            _context_id = capture
        elif isinstance(capture, six.string_types):
            _context_id = OmniId(capture)
        elif isinstance(capture, Capture):
            _context_id = capture.id
        elif isinstance(capture, CaptureSession):
            _context_id = capture.capture_id
        else:
            _context_id = OmniId()
        req_props = {
            'contextId': _context_id.format(),
            'compact': jbool(compact)
        }
        pr = self.perf('delete_event_log')
        cmd = 'events/'
        resp = self._issue_command(cmd, pr, EO.DELETE, params=req_props)
        if not isinstance(resp, dict):
            raise OmniError('Failed to Delete Event Log.')

    def delete_file(self, target):
        """Delete a list of files from the OmniEngine.

        Args:
            target (str): one or more files to delete. If not fully qualified
                          then target will be relative to the engine's
                          data directory.

        Failure:
            Raises an OmniError with results as the list of failures.
        """
        _target = target if isinstance(target, list) else [target]
        req_props = []
        for _t in _target:
            if isinstance(_t, PacketFileInformation):
                _name = _t.path
            elif isinstance(_t, FileInformation):
                _name = _t.name
            else:
                _name = _t
            req_props.append(('files', _name))
        if not req_props:
            raise TypeError('No files specified.')
        pr = self.perf('delete_files')
        cmd = 'files/'
        resp = self._issue_command(cmd, pr, EO.DELETE, params=req_props)
        if isinstance(resp, dict):
            results = resp.get('results')
            failures = []
            if isinstance(results, list):
                for r in results:
                    if isinstance(r, dict):
                        code = r.get('result')
                        if code != 0:
                            failures.append(r)
                if failures:
                    raise OmniError(
                        'Failed to delete 1 or more files.', result=failures)

    def delete_filter(self, omnifilter: Union[Filter, List[Filter]]):
        """Delete a filter from the OmniEngine's filter set.

        Args:
            omnifilter (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Filter <omniscript.filter.Filter>`
            ): the id of the filter or a Filter object.
        """
        if not omnifilter:
            return
        idlist = []
        filterlist = omnifilter if isinstance(omnifilter, list) else [omnifilter]
        for f in filterlist:
            if isinstance(f, Filter):
                idlist.append(f.id)
            elif isinstance(f, OmniId):
                idlist.append(f)
            elif isinstance(f, six.string_types):
                idlist.append(OmniId(f))
            elif f is not None:
                raise TypeError('omnifilter must be a Filter.')
        if idlist:
            fl = self.get_filter_list()
            for id in idlist:
                if find_filter(fl, id, 'id'):
                    pr = self.perf('delete_filter')
                    cmd = f'filters/{id.format()}'
                    props = self._issue_command(cmd, pr, EO.DELETE)
                    if not is_success(props):
                        raise OmniError('Failed to delete Filter')

    def delete_filter_list(self):
        """ Delete the entire filter list """
        if len(self.get_filter_list()) > 0:
            pr = self.perf('delete_filter_list')
            self._issue_command(Filter.endpoint, pr, EO.DELETE)

    def delete_forensic_search(self, search):
        """Delete a
        :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
        for the specified id.

        Returns:
            A
            :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
            object.
        """
        if isinstance(search, ForensicSearch):
            id = search.id
        else:
            id = OmniId(search)
        pr = self.perf('delete_forensic_search')
        props = self._issue_command(
            f'forensic-searches/{id.format()}', pr, EO.DELETE)
        if not is_success(props):
            raise OmniError('Failed to delete Forensic Search')

    def delete_notification(self, notificationId) -> Optional[dict]:
        """ Delete the notification from the engine """
        return Notifications(self).delete_notification(notificationId)

    def delete_remote_engine(self, remote_engine: Union[RemoteEngine, OmniId, str]):
        return RemoteEngine.delete(self, remote_engine)

    def delete_token(self, tokens: Union[List[AuthenticationToken], AuthenticationToken]):
        """ Delete the specified tokens from the input list """
        list_ = tokens if isinstance(tokens, list) else [tokens]
        if list_:
            pr = self.perf('delete_token')
            props = [('ids', token.authentication_token_id) for token in list_]
            resp = self._issue_command(
                AuthenticationToken.endpoint, pr, EO.DELETE, params=props)
            if not is_almost_success(resp):
                raise OmniError('Delete Token failed')

    def disconnect(self):
        """Disconnect from the OmniEngine
        """
        return self.logout()

    def file_database_operation(self, operation=DatabaseOperation.SYNC):
        """Perform one of the file database maintenance operations.

        Input:
            operation : Must be one of the DATABASE_ constants.
        """
        if operation == DatabaseOperation.SYNC:
            pr = self.perf('synchronize_file_databases')
            self._issue_command('database-sync/', pr, EO.POST)
        elif operation == DatabaseOperation.INDEX:
            pr = self.perf('file_databases_index')
            self._issue_command('database-index/', pr, EO.POST)
        elif operation == DatabaseOperation.MAINTENANCE:
            pr = self.perf('file_databases_maintenance')
            self._issue_command('database-maintenance/', pr, EO.POST, DF.PLAIN)
        else:
            raise OmniError('Illeagal operation, must be one of the DATABASE_ constants.')

    def find_adapter(self, value, attrib=Adapter.find_attributes[0]):
        """Find an :class:`Adapter <omniscript.adapter.Adapter>`
        in the OmniEngine's list of adapters.

        Args:
            value (str or :class:`Adapter <omniscript.adapter.Adapter>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            An :class:`Adapter <omniscript.adapter.Adapter>`
            object of the adapter.

        Note:
            If value is an :class:`Adapter <omniscript.adapter.Adapter>`,
            then the search is performed on the Adapter's id.
        """
        adapters = self.get_adapter_list()
        return find_adapter(adapters, value, attrib)

    def find_capture(self, value, attrib=find_attributes[0]):
        """Find an :class:`Capture <omniscript.capture.Capture>`
        in the OmniEngine's list of captures.

        Args:
            value (str or :class:`Capture <omniscript.capture.Capture>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            An :class:`Capture <omniscript.capture.Capture>`
            object of the capture.

        Note:
            If value is an :class:`Capture <omniscript.capture.Capture>`,
            then the search is performed on the Capture's id.
        """
        captures = self.get_capture_list()
        return find_capture(captures, value, attrib)

    def find_decryption_key(self, value, attrib=DecryptionKey.find_attributes[0]):
        """Find an :class:`DecryptionKey <omniscript.decryptionkey.DecryptionKey>`
        in the OmniEngine's list of decryption keys.

        Args:
            value (str or :class:`DecryptionKey <omniscript.decryptionkey.DecryptionKey>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            An :class:`DecryptionKey <omniscript.decryptionkey.DecryptionKey>`
            object of the DecryptionKey.

        Note:
            If value is an :class:`DecryptionKey<omniscript.decryptionkey.DecryptionKey>`,
            then the search is performed on the DecryptionKey's id.
        """
        keys = self.get_decryption_key_list()
        return find_decryption_key(keys, value, attrib)

    def find_filter(self, value, attrib=find_attributes[0]):
        """Find a :class:`Filter <omniscript.filter.Filter>`
        in the OmniEngine's filter set.

        Args:
            value (str or :class:`Filter <omniscript.filter.Filter>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            A :class:`Filter <omniscript.filter.Filter>` object
            of the filter or None.
        """
        filters = self.get_filter_list()
        return omniscript.find_filter(filters, value, attrib)

    def find_forensic_search(self, value, attrib=find_attributes[0]):
        """Find a
        :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
        in the OmniEngine's Forensic Search list.

        Args:
            value (str or
            :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            A
            :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
            object or None.
        """
        searches = self.get_forensic_search_list()
        return find_forensic_search(searches, value, attrib)

    def get_adapter_list(self):
        """Get the OmniEngine's list of
        :class:`Adapter <omniscript.adapter.Adapter>`.

        Returns:
            A list of
            :class:`Adapter <omniscript.adapter.Adapter>`
            objects.
        """
        pr = self.perf('get_adapter_list')
        props = self._issue_command('adapters/', pr)
        return _create_adapter_list(self, props) if props else None

    def get_adapter_information_list(self):
        """Get the OmniEngine's list of
        :class:`AdapterInformation <omniscript.adapterinformation.AdapterInformation>`.

        Returns:
            A list of
            :class:`AdapterInformation <omniscript.adapterinformation.AdapterInformation>`
            objects.
        """
        pr = self.perf('get_adapter_information_list')
        props = self._issue_command('adapters/info/', pr)
        return _create_adapter_information_list(self, props) if props else None

    def get_alarm(self, alarm_id: Union[Alarm, OmniId, str]) -> Optional[Alarm]:
        """Get a specific OmniEngine Alarm.
        """
        _id = alarm_id.id if isinstance(alarm_id, Alarm) else OmniId(alarm_id)
        pr = self.perf('get_alarm')
        props = self._issue_command(f'{Alarm._endpoint}{_id.format()}/', pr)
        alarm_list = _create_alarm_list(props)
        return alarm_list[0] if alarm_list and len(alarm_list) else None

    def get_alarm_list(self) -> Optional[List[Alarm]]:
        """Get the OmniEngine's list of alarms.

        Returns:
            A list of :class:`Alarm <omniscript.alarm.Alarm>` objects.
        """
        pr = self.perf('get_alarm_list')
        props = self._issue_command(Alarm._endpoint, pr)
        return _create_alarm_list(props) if isinstance(props, dict) else []

    def get_analysis_module_list(self):
        """Get the OmniEngine's list of Analysis Modules.

        Returns:
            A list of
            :class:`AnalysisModule <omniscript.analysismodule.AnalysisModule>`
            objects.
        """
        pr = self.perf('get_analysis_module_list')
        props = self._issue_command('capabilities/', pr)
        return _create_analysis_module_list(self, props.get('pluginsInfo')) if (
            props and 'pluginsInfo' in props) else None

    def get_audit_log(self):
        """Return the OmniEngine's Audit Log.
        """
        pr = self.perf('get_audit_log')
        props = self._issue_command('audit-log/', pr)
        return AuditLog(self, props)

    def get_application_list(self):
        """The the list of Applications.
        """
        pr = self.perf('get_application_list')
        props = self._issue_command('applications/', pr)
        return _create_application_list(props)

    def get_capabilities(self) -> Capabilities:
        """Gets the engine capabilties"""
        command = 'capabilities/'
        pr = self.perf('get_capabilities')
        props = self._issue_command(command, pr)
        if not isinstance(props, dict):
            raise OmniError('Failed to get engine capabilities.')
        return Capabilities(props)

    def get_capture_list(self):
        """Get the OmniEngine's list of
        :class:`Capture <omniscript.capture.Capture>`.

        Returns:
            A list of
            :class:`Capture <omniscript.capture.Capture>`
            objects.
        """
        pr = self.perf('get_capture_list')
        props = self._issue_command('captures/', pr)
        return _create_capture_list(self, props) if props else None

    def get_capture_session_list(self):
        """Get the OmniEngine's list of
        :class:`CaptureSession <omniscript.capturesession.CaptureSession>`.

        Returns:
            A list of
            :class:`CaptureSession <omniscript.capturesession.CaptureSession>`
            objects.
        """
        pr = self.perf('get_capture_session_list')
        props = self._issue_command('capture-sessions/', pr)
        return _create_capture_session_list(self, props) if props else None

    def get_capture_template(self, obj):
        """Get one of the stored Capture Templates.

        Returns:
            A :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
            object.
        """
        if isinstance(obj, CaptureTemplate):
            id = obj.id
        else:
            id = OmniId(obj)
        pr = self.perf('get_capture_template')
        cmd = f'capture-templates/{id.format()}/'
        props = self._issue_command(cmd, pr)
        return CaptureTemplate(props=props, engine=self) if props else None

    def get_capture_template_list(self):
        """Get the OmniEngine's list of stored
        :class:`CaptureTemplates <omniscript.capturetemplate.CaptureTemplate>`.

        Returns:
            A list of
            :class:`Capture <omniscript.capturetemplate.CaptureTemplate>`
            objects.
        """
        pr = self.perf('get_capture_template_list')
        props = self._issue_command('capture-templates/', pr)
        return _create_capture_template_list(self, props) if props else None

    def get_connected_user_list(self):
        """Return the list of connected users."""
        return User.get_connected_user_list(self)

    def get_country_list(self):
        """Return the list of Country Names and Codes.
        """
        pr = self.perf('get_country_list')
        props = self._issue_command('countries/', pr)
        return _create_country_list(props)

    def get_decryption_key_list(self) -> list:
        """Return the list of DecryptionKeys

        """
        pr = self.perf('get_decryption_key_list')
        props = self._issue_command('decryption-keys/', pr)
        return _create_decryption_key_list(props)

    def get_diagnostics(self, command: Diagnostics = Diagnostics.DEFAULT,
                        verbose: bool = False) -> Optional[str]:
        """Get diagnostice information from the Engine.
        """
        cmd_labels = 'default', 'drives', 'processes', 'raid', 'system-log'
        if command not in Diagnostics:
            raise TypeError(
                'command must be one of the Diagnostics constants.')
        req_props = {
            'verbose': jbool(verbose)
        }
        pr = self.perf('get_diagnostics')
        cmd = f'diagnostics/{cmd_labels[command]}/'
        txt = self._issue_command(cmd, pr, EO.POST, DF.PLAIN, params=req_props)
        return txt

    def get_directory(self, path: str = None, files: bool = True, hidden: bool = False):
        """Get a :class:`Directory <omniscript.directory.Directory>`
        object of the host system's File System.
        Default path is the engine's data directory.
        Returns:
            A
            :class:`Directory <omniscript.directory.Directory>`
            object.
        """
        if path:
            _path = path
        elif self._last_status is not None:
            _path = self._last_status.data_directory
        else:
            _path = '/var/lib/omni/data'
        req_props = {
            'path': _path,
            'showFiles': jbool(files),
            'showHiddenFiles': jbool(hidden)
        }
        pr = self.perf('get_directory')
        cmd = 'directory-list/'
        resp = self._issue_command(cmd, pr, params=req_props)
        return Directory(self, resp)

    def get_engine_settings(self) -> Optional[EngineSettings]:
        """ Get the engine settings from the engine """
        return EngineSettings.get(self)

    def get_event_log(self, first=None, count=None, capture=None, query=None, time_span=None):
        """Get the OmniEngine's Event Log.

        Args:
            first (int): the index of the first entry to retrieve.
            count (int): the maximum number of entries to retrieve.
            capture (OmniId, str, Capture, CaptureSession):
            Get entries for just this 'capture'.
            query (str): only entries whos message contains query.

        Returns:
            A :class:`EventLog <omniscript.eventlog.EventLog>` object.
        """
        if isinstance(capture, OmniId):
            _context_id = capture
        elif isinstance(capture, six.string_types):
            _context_id = OmniId(capture)
        elif isinstance(capture, Capture):
            _context_id = capture.id
        elif isinstance(capture, CaptureSession):
            _context_id = capture.capture_id
        else:
            _context_id = None

        req_props = {
            'informational': jtrue,
            'major': jtrue,
            'minor': jtrue,
            'severe': jtrue,
            'messages': jtrue
            # 'sourceId': str(OmniId.null_id),
            # 'sourceKey': 0,
        }

        if first is not None:
            req_props['offset'] = int(first)
        if count is not None:
            req_props['limit'] = int(count)
        if _context_id:
            req_props['contextId'] = _context_id.format()
        if query:
            req_props['search'] = query
        if isinstance(time_span, (tuple, list, dict)) and len(time_span) == 2:
            req_props['startTime'] = time_span[0].iso_time()
            req_props['stopTime'] = time_span[1].iso_time()

        pr = self.perf('get_event_log')
        cmd = 'events/'
        resp = self._issue_command(cmd, pr, params=req_props)
        return EventLog(self, resp, _context_id, query)

    def get_expert_preferences(self) -> List[ExpertPreferences]:
        """ Get the expert preferences from the engine """
        pr = self.perf('get_expert_prefs')
        command = 'expert-prefs/'
        resp = self._issue_command(command, pr)
        return ExpertPreferences(resp)

    def get_file(self, source: str, delete: bool = False):
        """Get a file from the OmniEngine.

        Args:
            source (str): name of the file to get. If not fully qualified
                          then source will be relative to the engine's
                          data directory.

        Returns:
            The contents of the file as an array of bytes.
        """
        if isinstance(source, PacketFileInformation):
            _source = source.path
        elif isinstance(source, FileInformation):
            _source = source.name
        else:
            _source = source

        req_props = {
            'file': _source,
            'delete': jtrue if delete else jfalse
        }
        pr = self.perf('get_file')
        cmd = 'files/'
        resp = self._issue_command(cmd, pr, params=req_props, format=DF.PLAIN)
        return resp

    # def get_file_system(self, path='/', files=True, hidden=False):
    #     """Get host system's File System as a tree of Directory
    #     objects.

    #     Returns:
    #         A list of
    #         :class:`Directory <omniscript.directory.Directory>`
    #         objects.
    #     """
    #     p = self._last_status.data_directory
    #     req_props = {
    #         'path': path,
    #         'showFiles': jbool(files),
    #         'showHiddenFiles': jbool(hidden)
    #     }
    #     pr = self.perf('get_file_system')
    #     cmd = f'directory-list/'
    #     resp = self._issue_command(cmd, pr, params=req_props)
    #     if resp.status_code != 200:
    #         return None
    #     props = json.loads(resp.text)
    #     return _create_file_system(self, props)

    def get_filter(self, omnifilter: Union[Filter, OmniId, str]) -> Optional[Filter]:
        """Get :class:`Filter <omniscript.filter.Filter>` from the engine.

        Args:
            omnifilter (str, id, Filter): id of the Filter
        Returns:
            A  :class:`Filter <omniscript.filter.Filter>` object.
        """
        if isinstance(omnifilter, Filter):
            id = omnifilter.id
        elif isinstance(omnifilter, OmniId):
            id = omnifilter
        elif isinstance(omnifilter, six.string_types):
            id = OmniId(omnifilter)
        elif omnifilter is not None:
            raise TypeError('omnifilter must be an OmniId.')
        else:
            return None

        pr = self.perf('get_filter')
        cmd = f'{Filter.endpoint}{id.format()}'
        props = self._issue_command(cmd, pr)
        filter_list = _create_filter_list(props)
        return filter_list[0] if filter_list else None

    def get_filter_list(self, refresh=True):
        """Get the OmniEngine's :class:`Filter <omniscript.filter.Filter>`
        set.

        Args:
            refresh(bool): If True will force a refresh, else refresh
                           if the timeout has expired.
        Returns:
            A list of
            :class:`Filter <omniscript.filter.Filter>`
            objects.
        """
        pr = self.perf('get_filter_list')
        props = self._issue_command(Filter.endpoint, pr)
        return _create_filter_list(props)

    def get_forensic_search(self, search):
        """Get a
        :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
        for the specified id.

        Returns:
            A
            :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
            object.
        """
        if isinstance(search, ForensicSearch):
            id = search.id
        else:
            id = OmniId(search)
        pr = self.perf('get_forensic_template')
        props = self._issue_command(f'forensic-searches/{id.format()}', pr)
        return ForensicSearch(props, self) if props else None

    def get_forensic_file_list(self):
        return None

    def get_forensic_search_list(self):
        """Get the OmniEngine's list of
        :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`.

        Returns:
            A list of
            :class:`ForensicSearch <omniscript.forensicsearch.ForensicSearch>`
            objects.
        """
        pr = self.perf('get_forensic_search_list')
        props = self._issue_command('forensic-searches/', pr)
        return _create_forensic_search_list(self, props) if props else None

    def get_graph_template_list(self):
        """Get the OmniEngine's list of
        :class:`GraphTemplate <omniscript.graphtemplate.GraphTemplate>`.

        Returns:
            A list of :class:`GraphTemplate <omniscript.graphtemplate.GraphTemplate>`
            objects.
        """
        pr = self.perf('get_graph_template_list')
        props = self._issue_command('graphs/', pr)
        return _create_graph_template_list(props) if props else None

    def get_license(self) -> Optional[License]:
        """ Get the license information from the engine """
        pr = self.perf('get_license')
        props = self._issue_command(License.endpoint, pr)
        return License(props) if isinstance(props, dict) else None

    def get_license_locking_code(self, criteria: Union[List[int], int]) -> Optional[str]:
        """ Get the license locking code from the engine """
        pr = self.perf('get_license_locking_code')
        flags = sum(criteria, 0) if isinstance(criteria, list) else criteria
        props = self._issue_command(
            f'{License.endpoint}locking-code/{flags}', pr)

        return props['lockingCode'] if isinstance(props, dict) else None

    def get_license_settings(self) -> Optional[LicenseSettings]:
        """ Get the license settings from the engine """
        pr = self.perf('get_license_settings')
        props = self._issue_command(LicenseSettings.endpoint, pr)
        return LicenseSettings(props) if isinstance(props, dict) else None

    def get_liveflow_configuration(self) -> Optional[LiveFlowConfiguration]:
        """ Get the liveflow configuration from the engine """
        return LiveFlow(self).get_liveflow_configuration()

    def get_liveflow_context(self) -> Optional[LiveFlowContext]:
        """ Get the liveflow context from the engine """
        return LiveFlow(self).get_liveflow_context()

    def get_liveflow_status(self) -> Optional[LiveFlowStatus]:
        """ Get the liveflow status from the engine """
        return LiveFlow(self).get_liveflow_status()

    def get_name_table(self):
        """Get the list of Name Objects."""
        pr = self.perf('get_names')
        props = self._issue_command('names/', pr)
        return NameTable(self, props)

    def get_notification(self, notificationId) -> Optional[NotificationActions]:
        """ Get the notification from the engine """
        return Notifications(self).get_notification(notificationId)

    def get_notifications(self) -> Optional[NotificationActions]:
        """ Get the notifications from the engine """
        return Notifications(self).get_notifications()

    def get_packet_file_list(self):
        """Get a list of packet files and their attributes.

        Returns:
            A list of
            :class:`PacketFileInformation <omniscript.packetfileinformation.PacketFileInformation>`
            objects.
        """
        pr = self.perf('get_packet_file_list')
        props = self._issue_command('files-list/', pr)
        return _create_packet_file_information_list(props) if props else None

    def get_protocol_list(self) -> List[Protocol]:
        """Get the list of protocols.
        """
        pr = self.perf('get_protocol_list')
        props = self._issue_command('protocols/', pr)
        return _create_protocol_list(props)

    def get_protocol_translation_list(self) -> List[PT]:
        """ Get the list of protocol translations """
        pr = self.perf('get_protocol_translations_list')
        props = self._issue_command(PT.endpoint, pr)
        return _create_protocol_translations_list(props)

    def get_remote_engine(self, id):
        return RemoteEngine.get(self, id)

    def get_remote_engine_list(self) -> Optional[RemoteEngine]:
        """ Get the engine's list of remote engines """
        return RemoteEngine.get_all(self)

    def get_select_related_progress(self, endpoint: str, id: int, timeout: float) -> int:
        """ Get the progress percentage for the select related """
        progress = 0
        pr = self.perf('get_select_related_progress')
        command = f'{endpoint}/{Selection.Command.Progress}/{id}/'

        # Add some delay if needed to help the select related complete
        time.sleep(timeout)

        props = self._issue_command(command, pr)

        if isinstance(props, dict):
            if Selection.Command.Progress in props:
                val = props[Selection.Command.Progress]
                if isinstance(val, int):
                    progress = val

        return progress

    def get_selection_packets(self, id: int, endpoint: str, pr_log: str, timeout: float) -> dict:
        """ Shared helper to retrieve the packets based on id and endpoint """
        packets = {}
        if self.get_select_related_progress(endpoint, id, timeout) == 100:
            command = f'{endpoint}/{Selection.Command.Results}/{id}/'
            pr = self.perf(pr_log)
            props = self._issue_command(command, pr)
            packets = props if isinstance(props, dict) else {}
        else:
            OmniError(
                'Failed to complete select related in a timely manner. Increase timeout')

        return packets

    def get_select_related_packets(self, id: int, timeout: float = 0.2) -> dict:
        """ Get the select related packets """
        return self.get_selection_packets(id, endpoint='select-related',
                                          pr_log='get_select_related_packets', timeout=timeout)

    def get_select_related_filter_config_packets(self, id: int, timeout: float = 0.2) -> dict:
        """ Get the select related packets """
        return self.get_selection_packets(id, endpoint='select-related-filter-config',
                                          pr_log='get_select_related_filter_config_packets',
                                          timeout=timeout)

    def get_session_token(self):
        """Return the current Session Token.
        """
        if 'authorization' in self._session.headers:
            token = self._session.headers['authorization']
            if len(token) > 11:
                return token[11:]
        return None

    def get_status(self):
        """Return the current OmniEngine Status.
        """
        pr = self.perf('get_status')
        data = self._issue_command('status/', pr)
        self._last_status = EngineStatus(self, data)
        return self._last_status

    def get_settings(self) -> Optional[EngineSettings]:
        """Gets the engine settings"""
        if self.engine is not None:
            command = 'settings/'
            pr = self.engine.perf('get_settings')
            resp = self.engine._issue_command(command, pr, EO.GET)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get engine settings.')
            return EngineSettings(resp)
        return None

    # def get_support_information(self) -> Optional[str]:
    #     """Return Support Information for the OmniEngine.

    #     Returns:
    #         The Support Information text as a string.
    #     """
    #     return Engine(self).get_support()

    def get_timeouts(self) -> EngineTimeouts:
        """Return a list with the engine's HTTPS Connection and Request
        timeouts in seconds."""
        return self.timeouts

    def get_token(self, id: str) -> Optional[AuthenticationToken]:
        """ Return the token based on the ID """
        pr = self.perf('get_token')
        props = self._issue_command(f'token/{id}', pr)
        return AuthenticationToken(props) if isinstance(props, dict) else None

    def get_token_list(self) -> List[AuthenticationToken]:
        pr = self.perf('get_token_list')
        props = self._issue_command(AuthenticationToken.endpoint, pr)
        return _create_authentication_token_list(props) if isinstance(props, dict) else []

    def get_trace_log_level(self):
        """Return the Trace Log logging level.

        Returns:
            Logging levels as TraceLogLevel.
        """
        level = TraceLogLevel.OFF
        pr = self.perf('get_audit_logging_level')
        props = self._issue_command('log-level/', pr)
        if isinstance(props, dict):
            level = props.get('logLevel')
            if level is None:
                raise (OmniError('Failed to get the Trace Log logging level.'))
        return TraceLogLevel(level)

    def get_user_list(self):
        return User.get_user_list(self)

    def get_version(self):
        """Get the OmniEngine's version string.

        Returns:
            The OmniEngine's version as a string.
        """
        pr = self.perf('get_version')
        props = self._issue_command('version/', pr)
        return props['engineVersion'] if isinstance(props, dict) and (
            'engineVersion' in props) else None

    def is_connected(self):
        """Get the connection status of the OmniEngine object.

        Returns:
            True if OmniEngine object is connected to an OmniEngine,
            otherwise False.
        """
        return self._connected

    def login(self, user, password, otp=None, session_token=None, timeouts=None):
        """Login and connect to the OmniEngine: Account user name, Account
        password, optional One Time Password (otp), optional Session token
        and optional Connection timeout.
        """
        _timeouts = (EngineTimeouts(timeouts) if timeouts is not None else self.timeouts)
        try:
            if session_token:
                # TODO: rewrite with f-string.
                token = ('authToken: '
                         + session_token.decode('utf-8')).encode('utf-8')
                self._session.headers.update({'authorization': token})
                status_url = f'{self._base_url}status/'
                resp = self._session.get(status_url, verify=False, timeouts=_timeouts.as_tuple())
                if resp.status_code == 200:
                    self._connected = True
                    self.get_status()
                    return True
            url = f'{self._base_url}login/'
            cred_dict = {
                'username': user,
                'password': password,
                'client': 'OmniScript',
                'attempt': 0
            }
            if otp is not None:
                cred_dict['otp'] = otp
            credentials = json.dumps(cred_dict)
            self._session.headers.update({'accept': 'application/json'})
            self._session.headers.update({'Content-Type': 'application/json'})
            resp = self._session.post(url, verify=False, data=credentials,
                                      timeout=_timeouts.as_tuple())
            if (resp is None) or (resp.status_code != 200):
                self.logger.debug('Could not login. Retrying')
                retry = True
                while retry and (cred_dict['attempts'] < 6) and (resp.status_code != 200):
                    cred_dict['attempts'] += 1
                    self.logger.debug(f'Attempt No: {cred_dict["attempts"]}')
                    credentials = json.dumps(cred_dict)
                    time.sleep(5)
                    resp = self._session.post(url, verify=False, data=credentials,
                                              timeout=_timeouts.as_tuple())
                    if resp.status_code == 200:
                        self.logger.debug(
                            f'Retry Succeeded after {cred_dict["attempts"]} attempts.')
                        retry = False
                if cred_dict['attempts'] > 5:
                    if resp.status_code == 502:
                        self.logger.debug(
                            'Could not connect to engine. Please Check if engine is running and '
                            f'then retry. Response code : {resp.status_code}')
                    else:
                        self.logger.debug(
                            f'Could not connect to engine. Response code : {resp.status_code}')
                    return False
            resp_data = json.loads(resp.text)
            token = ('authToken: ' + resp_data['authToken']).encode('utf-8')
            self._session.headers.update({'authorization': token})
            self._connected = True
            self.get_status()
        except Exception as e:
            self.logger.debug(f'Exception while logging in. {e}')
        return self._connected

    def logout(self):
        """logout and disconnect from the OmniEngine.
        """
        self._connected = False
        errors = []
        if 'authorization' not in self._session.headers:
            return errors
        url = f'{self._base_url}logout/'
        token = self._session.headers['authorization'].decode('utf-8')
        # TODO: rewrite with f-string.
        data = "{\"authToken\":\"" + token + "\"}"
        try:
            self._session.post(url, verify=False, data=data, timeout=self.timeouts.as_tuple())
        except Exception:
            errors.extend(['Exception while logging out'])
            self.logger.debug('Exception while logging out')
        return errors

    def modify_alarm(self, alarm: Alarm) -> None:
        """ Modify an alarm to the OmniEngine
        """
        pr = self.perf('modify_alarm')
        data = json.dumps(alarm._store())
        return self._issue_command(f'{Alarm._endpoint}{alarm.id.format()}/', pr, EO.PUT, data=data)

    def modify_token(self, token: AuthenticationToken):
        """ Modify an authentication token at the input ID """
        pr = self.perf('modify_token')

        data = json.dumps(token._modify_template())
        self._issue_command(f'{AuthenticationToken.endpoint}{token.authentication_token_id}/',
                            pr, EO.PUT, data=data)

    def perf(self, msg):
        """Log a performance message.
        """
        return self._perf_logger.perf(msg) if self._perf_logger else None

    def rename_decryption_key(self, decryptkeys, name: str):
        """ Sets the name of the DecryptionKey specified by the id.
        Function does nothing if no key exists.
        """
        if isinstance(decryptkeys, DecryptionKey) or isinstance(decryptkeys, DecryptionKeyTemplate):
            id = decryptkeys.id
        else:
            id = OmniId(decryptkeys)

        pr = self.perf('rename_decryption_key')
        data = json.dumps({"name": name})
        return self._issue_command(f'decryption-keys/name/{id.format()}/', pr, EO.PUT, data=data)

    def redirect_standard_out(self, std_out=None, std_err=None):
        """Redirect the Standard Output and Standard Error
        to the specified file paths.
        """
        pr = self.perf('redirect_standard_out')
        req_props = {}
        if std_out:
            req_props['stdoutlog'] = std_out
        if std_err:
            req_props['stderrlog'] = std_err
        data = json.dumps(req_props)
        self._issue_command('log-redirect/', pr, EO.POST, data=data)

    def rename_adapter(self, new_name):
        raise OmniError('Not implemented')

    # def restart(self):
    #     """Request the OmniEngine to Restart itself.
    #     The user will be logged off and the connection will be lost.
    #     """
    #     try:
    #         return Engine(self).engine_restart()
    #     except Exception:
    #         self.logger.debug('Exception while restarting the engine.')

    def send_email(self, email) -> Optional[SendEmailResponse]:
        """ Send an email from the engine """
        return Notifications(self).send_email(email)

    def send_file(self, path, destination=''):
        """Send a file to the OmniEngine.

        Args:
            path (str): name of the name of the file to send. If not fully qualified
                          then a relative path will be used.
            destination (str): destination path. If None then engine's data
                          directory.

        Returns:
            The number of bytes transfered.
        """
        if isinstance(path, PacketFileInformation):
            _path = path.path
        elif isinstance(path, FileInformation):
            _path = path.name
        else:
            _path = path
        if not os.path.isfile(_path):
            raise OmniError(f'File not found: {_path}')
        with open(_path, 'rb') as data_file:
            data = data_file.read()

        p = PurePath(_path)
        kind = ''   # magic.from_file(_path, mime=True)
        req_props = {
            'file': str(PurePosixPath(destination, p.name)),
            'type': kind
        }
        pr = self.perf('send_file')
        cmd = 'files/'
        resp = self._issue_command(cmd, pr, EO.POST, params=req_props, data=data)
        count = 0
        if isinstance(resp, dict):
            count = int(resp.get('size'))
        return count

    def send_notifications(self, notifications) -> Optional[dict]:
        """ Send a notification from the engine """
        return Notifications(self).send_notifications(notifications)

    def send_plugin_message(self, plugin, message=None):
        if isinstance(plugin, AnalysisModule):
            id = plugin.id
        else:
            id = OmniId(plugin)
        pr = self.perf('plugin_message')
        cmd = f'plugins/{str(id)}/message/'
        data = json.dumps({
            "data": "",
            "message": message if message is not None else ""
        })
        self._issue_command(cmd, pr, EO.POST, data=data)

    def set_alarm_list(self, alarms: List[Alarm]):
        """ Update the engine's list of alarms with the input list
        """
        pr = self.perf('set_alarm_list')
        props_list = [alarm._store() for alarm in alarms]
        data = json.dumps({
            "alarms": props_list,
            "modificationTime": PeekTime().iso_time()
        })
        self._issue_command(Alarm._endpoint, pr, EO.POST, data=data)

    # def set_engine_settings(self, settings: EngineSettings) -> Optional[SetSettingsResponse]:
    #     """ Set the engine settings from the engine """
    #     return Engine(self).set_settings(settings)

    # def set_expert_prefs(self, preferences: ExpertPreferences) -> Optional[dict]:
    #     """ Set the expert preferences from the engine """
    #     return Engine(self).set_expert_prefs(preferences)

    def set_filter_list(self, list_: List[Filter]):
        """ Update the engine's list of filters with the input list """

        if isinstance(list_, list):
            props_list = []
            pr = self.perf('set_filter_list')

            for filter in list_:
                props_list.append(filter.props)

            data = json.dumps({
                "filters": props_list,
                "modificationTime": PeekTime().iso_time()
            })
            self._issue_command(Filter.endpoint, pr, EO.POST, data=data)

    def set_license(self, license: str, source: int = 1):
        """ Set the license of the engine. Will cause a restart """
        pr = self.perf('set_license')
        data = json.dumps({
            'data': license,
            'source': source
        })
        self._issue_command(License.endpoint, pr, EO.POST, data=data)

    def set_license_settings(self, settings: dict):
        """ Set the license settings of the engine """
        pr = self.perf('set_license_settings')
        data = json.dumps(settings)
        self._issue_command(LicenseSettings.endpoint, pr, EO.POST, data=data)

    def set_liveflow_configuration(self, liveflowConfig: LiveFlowConfiguration) -> (
            Optional[LiveFlowConfigurationResponse]):
        """ Set the liveflow configuration on the engine """
        return LiveFlow(self).set_liveflow_configuration(liveflowConfig)

    def set_notification(self, notificationId, notifications) -> Optional[dict]:
        """ Set the notification from the engine """
        return Notifications(self).set_notification(notificationId, notifications)

    def set_notifications(self, notifications) -> Optional[dict]:
        """ Set the notifications from the engine """
        return Notifications(self).set_notifications(notifications)

    def set_protocol_translations_list(self, list_: List[PT]):
        """ Update the engine's list of translations with the input list """
        props_list = []

        if isinstance(list_, list):
            pr = self.perf('set_protocol_translations_list')

            for translation in list_:
                props_list.append(translation.props)

        data = json.dumps({
            "protocolTranslations": props_list
        })
        self._issue_command(PT.endpoint, pr, EO.POST, data=data)

    def set_settings(self, settings: EngineSettings) -> Optional[SetSettingsResponse]:
        """Sets the engine settings"""
        if self.engine is not None:
            command = 'settings/'
            pr = self.engine.perf('set_settings')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(settings, cls=OmniScriptEncoder))
            if not isinstance(resp, dict):
                raise OmniError('Failed to set engine settings.')
            return SetSettingsResponse(resp)
        return None

    def set_timeouts(self, connection_timeout: Union[int, float],
                     request_timeout: Optional[Union[int, float]]) -> EngineTimeouts:
        """Set the timeout values for HTTP Connection and Timeout in seconds.
        If the connection_timeout is less then zero or None, then the
        connection_timeout value is not changed.
        If the request_timeout is less then zero or None, then the
        request_timeout is set to the connection_timeout.
        """
        if connection_timeout is not None and connection_timeout >= 0:
            self.timeouts.set_connection(connection_timeout)
        if request_timeout is not None and request_timeout >= 0:
            self.timeouts.set_request(request_timeout)
        else:
            self.timeouts.set_request(self.timeouts.connection)
        return self.timeouts

    def set_trace_log_level(self, level):
        """Set the Trace Log logging level.
        """
        pr = self.perf('set_trace_log_level')
        req_props = {
            'logLevel': int(level)
        }
        data = json.dumps(req_props)
        self._issue_command('log-level/', pr, EO.POST, data=data)

    def start_capture(self, capture, retry=3):
        """Signal a Capture, or list of Captures, to begin
        capturing packets.

        Args:
            capture (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Capture <omniscript.capture.Capture>`
            ): the capture's id or a Capture object.
            Or a list of captures.
        """
        ids = _capture_id_list(capture)
        for id in ids:
            pr = self.perf('start_capture')
            command = f'running-captures/{id.format()}/'
            props = self._issue_command(command, pr, EO.POST)
            if not is_almost_success(props):
                raise OmniError('Command failed: 0x80004005')

    def start_performance_logging(self, filename, mode='a'):
        """Start loggin the time it takes for the OmniEngine to perform
        each command.

        Args:
            filename: the name of the file to write the log entries.
            mode: open the file in append 'a', or create/overwrite 'c'.
        """
        if self._perf_logger:
            self.stop_performance_logging()
        self._perf_logger = PerformanceLogger(filename, mode)

    def start_selection(self, id: Union[str, OmniId], pr_log: str, endpoint: str,
                        data: Optional[str] = None, params=None) -> Optional[Selection]:
        """ Shared helper for starting select related operations """
        pr = self.perf(pr_log)
        select_id = id.get_id() if isinstance(id, OmniId) else id
        command = f'{endpoint}/start/{select_id}/'
        resp = self._issue_command(
            command, pr, EO.POST, data=data, params=params)

        return Selection(resp) if isinstance(resp, dict) else None

    def start_select_related(
            self, id: Union[str, OmniId], packets: List[int], prefer_logical_addr: bool,
            select_related_by: int) -> Optional[Selection]:
        """ Starts a select related operation for the specified capture or search on the engine """
        data = json.dumps({
            'packets': packets,
            'preferLogicalAddress': prefer_logical_addr,
            'selectRelatedBy': select_related_by
        })

        return self.start_selection(id, pr_log='start_select_related',
                                    endpoint='select-related', data=data)

    def start_select_related_filter_config(self, id: Union[str, OmniId], filters: List[Filter],
                                           mode: int, first_packet_number: int,
                                           last_packet_number: int) -> Optional[Selection]:
        """ Starts a select related operation using a pre-defined filter configuration """
        data = json.dumps({
            'filters': [filter.UUID for filter in filters],
            'mode': mode
        })
        params = [('firstPacketNumber', first_packet_number),
                  ('lastPacketNumber', last_packet_number)]

        return self.start_selection(id, pr_log='start_select_related_filter_config',
                                    endpoint='select-related-filter-config', data=data,
                                    params=params)

    def stop_capture(self, capture, retry=3):
        """Signal a Capture, or list of Captures, to
        stop capturing packets.

        Args:
            capture (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Capture <omniscript.capture.Capture>`
            ): the capture's id or a Capture object.
            Or a list of captures.
        """
        ids = _capture_id_list(capture)
        for id in ids:
            pr = self.perf('stop_capture')
            command = f'running-captures/{id.format()}/'
            props = self._issue_command(command, pr, EO.DELETE)
            if not is_almost_success(props):
                raise OmniError('Command failed: 0x80004005')

    def stop_performance_logging(self):
        """Stop Performance Logging.
        """
        if self._perf_logger:
            self._perf_logger = None

    def update_capture_template(self, template):
        """Update an existing Capture Template to the OmniEngine.

        Return:
            bool: True on success, False on failure.
        """
        if isinstance(template, CaptureTemplate):
            t = template.store()
        else:
            raise ValueError('A CaptureTemplate is required.')
        pr = self.perf('update_capture_template')
        cmd = f'capture-templates/{template.id.format()}/'
        resp = self._issue_command(cmd, pr, EO.PUT, data=t)
        return is_success(resp)

    def update_remote_engine(self, remote):
        return remote.update(self, remote)

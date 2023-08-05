"""Notifications class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import json
from typing import Union

from .invariant import (
    EmailScheme, EngineOperation as EO, PeekResult, Severity, NOTIFICATION_SOURCES)
from .omnierror import OmniError
from .helpers import load_props_from_dict, OmniScriptEncoder, repr_array, str_array


_json_enabled = 'enabled'

_notification_action_severity_dict = {
    'enabled': 'enabled'
}


class NotificationActionSeverity(object):
    """The NotificationActionSeverity class has the attributes of a notification action severity."""

    enabled = False
    """Whether the severity is enabled."""

    severity = Severity.INFORMATIONAL
    """Severity."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'NotificationActionSeverity({{'
            f'enabled: {self.enabled}, '
            f'severity: {self.severity}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Notification Action Severity: '
            f'enabled={self.enabled}, '
            f'severity={self.severity}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            enabled = props.get(_json_enabled)
            if isinstance(enabled, bool):
                self.enabled = bool(enabled)

            severity = props.get('severity')
            if isinstance(severity, int):
                self.severity = severity if severity in Severity else Severity.INFORMATIONAL


_email_notification_action_dict = {
    'authentication': 'authentication',
    'clearPassword': 'clearPassword',
    'clsid': 'clsid',
    'id': 'id',
    'name': 'name',
    'password': 'password',
    'port': 'port',
    'recipient': 'recipient',
    'sender': 'sender',
    'server': 'server',
    'username': 'username'
}


class EmailNotificationAction(object):
    """The EmailNotificationAction class has the attributes of an email notification action."""

    authentication = False
    """Whether authenticatino is used."""

    clearPassword = ''
    """Clear text password."""

    clsid = 'FF13FDFE-31BA-40DD-AB8A-77A85C3A439A'
    """clsid."""

    disabledSources = []
    """Disabled sources."""

    id = ''
    """Notification action id."""

    name = ''
    """Notification name."""

    password = ''
    """Encoded password."""

    port = 25
    """Port."""

    recipient = ''
    """Recipient."""

    scheme = EmailScheme.SMTP
    """Email scheme."""

    sender = ''
    """Sender."""

    server = ''
    """SMTP server."""

    severities = []
    """Notification severities."""

    username = ''
    """Username."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'EmailNotificationAction({{'
            f'authentication: {self.authentication}, '
            f'clearPassword: "{self.clearPassword}", '
            f'clsid: "{self.clsid}", '
            f'disabledSources: [{repr_array(self.disabledSources)}], '
            f'id: "{self.id}", '
            f'name: "{self.name}", '
            f'password: "{self.password}", '
            f'port: {self.port}, '
            f'recipient: "{self.recipient}", '
            f'scheme: {self.scheme}, '
            f'sender: "{self.sender}", '
            f'server: "{self.server}", '
            f'severities: [{repr_array(self.severities)}], '
            f'username: "{self.username}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Email Notification Action: '
            f'authentication={self.authentication}, '
            f'clearPassword="{self.clearPassword}", '
            f'clsid="{self.clsid}", '
            f'disabledSources=[{str_array(self.disabledSources)}], '
            f'id="{self.id}", '
            f'name="{self.name}", '
            f'password="{self.password}", '
            f'port={self.port}, '
            f'recipient="{self.recipient}", '
            f'scheme={self.scheme}, '
            f'sender="{self.sender}", '
            f'server="{self.server}", '
            f'severities=[{str_array(self.severities)}], '
            f'username="{self.username}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _email_notification_action_dict)

        if isinstance(props, dict):
            disabledSources = []
            if 'disabledSources' in props:
                disabledSources = props['disabledSources']
            if isinstance(disabledSources, list):
                self.disabledSources = []
                for v in disabledSources:
                    if [item for item in NOTIFICATION_SOURCES].count(v) != 0:
                        self.disabledSources.append(v)

            scheme = EmailScheme.SMTP
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP

            severities = []
            if 'severities' in props:
                severities = props['severities']
            if isinstance(severities, list):
                self.severities = []
                for v in severities:
                    self.severities.append(NotificationActionSeverity(v))


_execute_notification_action_dict = {
    'arguments': 'arguments',
    'clsid': 'clsid',
    'command': 'command',
    'directory': 'directory',
    'id': 'id',
    'name': 'name'
}


class ExecuteNotificationAction(object):
    """The ExecuteNotificationAction class has the attributes of an execute notification action."""

    arguments = ''
    """Execution arguments."""

    clsid = '0D8DFB6C-237C-4ADE-8C37-E215D4F8CF00'
    """clsid."""

    command = ''
    """Execution command."""

    directory = ''
    """Execution directory."""

    disabledSources = []
    """Disabled sources."""

    id = ''
    """Notification action id."""

    name = ''
    """Notification name."""

    severities = []
    """Notification severities."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'ExecuteNotificationAction({{'
            f'arguments: "{self.arguments}", '
            f'clsid: "{self.clsid}", '
            f'command: "{self.command}", '
            f'directory: "{self.directory}", '
            f'disabledSources: [{repr_array(self.disabledSources)}], '
            f'id: "{self.id}", '
            f'name: "{self.name}", '
            f'severities: [{repr_array(self.severities)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Execute Notification Action: '
            f'arguments="{self.arguments}", '
            f'clsid="{self.clsid}", '
            f'command="{self.command}", '
            f'directory="{self.directory}", '
            f'disabledSources=[{str_array(self.disabledSources)}], '
            f'id="{self.id}", '
            f'name="{self.name}", '
            f'severities=[{str_array(self.severities)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _execute_notification_action_dict)

        if isinstance(props, dict):
            disabledSources = []
            if 'disabledSources' in props:
                disabledSources = props['disabledSources']
            if isinstance(disabledSources, list):
                self.disabledSources = []
                for v in disabledSources:
                    if [item for item in NOTIFICATION_SOURCES].count(v) != 0:
                        self.disabledSources.append(v)

            scheme = EmailScheme.SMTP
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP

            severities = []
            if 'severities' in props:
                severities = props['severities']
            if isinstance(severities, list):
                self.severities = []
                for v in severities:
                    self.severities.append(NotificationActionSeverity(v))


_log_notification_action_dict = {
    'clsid': 'clsid',
    'id': 'id',
    'name': 'name'
}


class LogNotificationAction(object):
    """The LogNotificationAction class has the attributes of an log notification action."""

    clsid = 'B2DA6C79-C270-4988-8A20-995A0BB7A1CE'
    """clsid."""

    disabledSources = []
    """Disabled sources."""

    id = ''
    """Notification action id."""

    name = ''
    """Notification name."""

    severities = []
    """Notification severities."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'LogNotificationAction({{'
            f'clsid: "{self.clsid}", '
            f'disabledSources: [{repr_array(self.disabledSources)}], '
            f'id: "{self.id}", '
            f'name: "{self.name}", '
            f'severities: [{repr_array(self.severities)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Log Notification Action: '
            f'clsid="{self.clsid}", '
            f'disabledSources=[{str_array(self.disabledSources)}], '
            f'id="{self.id}", '
            f'name="{self.name}", '
            f'severities=[{str_array(self.severities)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _log_notification_action_dict)

        if isinstance(props, dict):
            disabledSources = []
            if 'disabledSources' in props:
                disabledSources = props['disabledSources']
            if isinstance(disabledSources, list):
                self.disabledSources = []
                for v in disabledSources:
                    if [item for item in NOTIFICATION_SOURCES].count(v) != 0:
                        self.disabledSources.append(v)

            scheme = EmailScheme.SMTP
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP

            severities = []
            if 'severities' in props:
                severities = props['severities']
            if isinstance(severities, list):
                self.severities = []
                for v in severities:
                    self.severities.append(NotificationActionSeverity(v))


_snmp_notification_action_dict = {
    'clsid': 'clsid',
    'community': 'community',
    'id': 'id',
    'name': 'name',
    'recipient': 'recipient'
}


class SNMPNotificationAction(object):
    """The SNMPNotificationAction class has the attributes of an SNMP notification action."""

    clsid = 'ED19F042-0A45-44A6-9C47-E2A9D696881C'
    """clsid."""

    community = ''
    """Community."""

    disabledSources = []
    """Disabled sources."""

    id = ''
    """Notification action id."""

    name = ''
    """Notification name."""

    recipient = ''
    """Recipient."""

    severities = []
    """Notification severities."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'SNMPNotificationAction({{'
            f'clsid: "{self.clsid}", '
            f'community: "{self.community}", '
            f'disabledSources: [{repr_array(self.disabledSources)}], '
            f'id: "{self.id}", '
            f'name: "{self.name}", '
            f'recipient: "{self.recipient}", '
            f'severities: [{repr_array(self.severities)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'SNMP Notification Action: '
            f'clsid="{self.clsid}", '
            f'community="{self.community}", '
            f'disabledSources=[{str_array(self.disabledSources)}], '
            f'id="{self.id}", '
            f'name="{self.name}", '
            f'recipient="{self.recipient}", '
            f'severities=[{str_array(self.severities)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _snmp_notification_action_dict)

        if isinstance(props, dict):
            disabledSources = []
            if 'disabledSources' in props:
                disabledSources = props['disabledSources']
            if isinstance(disabledSources, list):
                self.disabledSources = []
                for v in disabledSources:
                    if [item for item in NOTIFICATION_SOURCES].count(v) != 0:
                        self.disabledSources.append(v)

            scheme = EmailScheme.SMTP
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP

            severities = []
            if 'severities' in props:
                severities = props['severities']
            if isinstance(severities, list):
                self.severities = []
                for v in severities:
                    self.severities.append(NotificationActionSeverity(v))


_syslog_notification_action_dict = {
    'clsid': 'clsid',
    'destination': 'destination',
    'id': 'id',
    'name': 'name'
}


class SysLogNotificationAction(object):
    """The SysLogNotificationAction class has the attributes of an syslog notification action."""

    clsid = '5D3B11A5-993F-4B18-B603-F1799AD3736E'
    """clsid."""

    destination = ''
    """Destination."""

    disabledSources = []
    """Disabled sources."""

    id = ''
    """Notification action id."""

    name = ''
    """Notification name."""

    severities = []
    """Notification severities."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'SysLogNotificationAction({{'
            f'clsid: "{self.clsid}", '
            f'destination: "{self.destination}", '
            f'disabledSources: [{repr_array(self.disabledSources)}], '
            f'id: "{self.id}", '
            f'name: "{self.name}", '
            f'severities: [{repr_array(self.severities)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'SysLog Notification Action: '
            f'clsid="{self.clsid}", '
            f'destination="{self.destination}", '
            f'disabledSources=[{str_array(self.disabledSources)}], '
            f'id="{self.id}", '
            f'name="{self.name}", '
            f'severities=[{str_array(self.severities)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _syslog_notification_action_dict)

        if isinstance(props, dict):
            disabledSources = []
            if 'disabledSources' in props:
                disabledSources = props['disabledSources']
            if isinstance(disabledSources, list):
                self.disabledSources = []
                for v in disabledSources:
                    if [item for item in NOTIFICATION_SOURCES].count(v) != 0:
                        self.disabledSources.append(v)

            scheme = EmailScheme.SMTP
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP

            severities = []
            if 'severities' in props:
                severities = props['severities']
            if isinstance(severities, list):
                self.severities = []
                for v in severities:
                    self.severities.append(NotificationActionSeverity(v))


_textlog_notification_action_dict = {
    'clsid': 'clsid',
    'currentFileCount': 'currentFileCount',
    'deleteFileCount': 'deleteFileCount',
    'fileCount': 'fileCount',
    'fileCountsEnabled': 'fileCountsEnabled',
    'fileName': 'fileName',
    'fileNameAppend': 'fileNameAppend',
    'fileNameExtension': 'fileNameExtension',
    'filePath': 'filePath',
    'fileSize': 'fileSize',
    'fileSizesEnabled': 'fileSizesEnabled',
    'finished': 'finished',
    'id': 'id',
    'name': 'name',
    'totalFileSizes': 'totalFileSizes'
}


class TextLogNotificationAction(object):
    """The TextLogNotificationAction class has the attributes of an text log notification action."""

    clsid = 'EF21EA89-80C3-4801-98F6-544677CF12D0'
    """clsid."""

    currentFileCount = 0
    """Current file count."""

    deleteFileCount = 0
    """Delete file count."""

    disabledSources = []
    """Disabled sources."""

    fileCount = 0
    """File count."""

    fileCountsEnabled = True
    """Whether file count is enabled."""

    fileName = ''
    """File name."""

    fileNameAppend = ''
    """File name append."""

    fileNameExtension = ''
    """File name extension."""

    filePath = ''
    """File path."""

    fileSize = 1
    """File size (in bytes)."""

    fileSizesEnabled = True
    """Whether file size is enabled."""

    finished = True
    """Whether notification is finished."""

    id = ''
    """Notification action id."""

    name = ''
    """Notification name."""

    severities = []
    """Notification severities."""

    totalFileSizes = 1
    """Total file size (in bytes)."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'TextLogNotificationAction({{'
            f'clsid: "{self.clsid}", '
            f'currentFileCount: {self.currentFileCount}, '
            f'deleteFileCount: {self.deleteFileCount}, '
            f'disabledSources: [{repr_array(self.disabledSources)}], '
            f'fileCount: {self.fileCount}, '
            f'fileCountsEnabled: {self.fileCountsEnabled}, '
            f'fileName: "{self.fileName}", '
            f'fileNameAppend: "{self.fileNameAppend}", '
            f'fileNameExtension: "{self.fileNameExtension}", '
            f'filePath: "{self.filePath}", '
            f'fileSize: {self.fileSize}, '
            f'fileSizesEnabled: {self.fileSizesEnabled}, '
            f'finished: {self.finished}, '
            f'id: "{self.id}", '
            f'name: "{self.name}", '
            f'severities: [{repr_array(self.severities)}],'
            f'totalFileSizes: {self.totalFileSizes}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Text Log Notification Action: '
            f'clsid="{self.clsid}", '
            f'currentFileCount={self.currentFileCount}, '
            f'deleteFileCount={self.deleteFileCount}, '
            f'disabledSources=[{str_array(self.disabledSources)}], '
            f'fileCount={self.fileCount}, '
            f'fileCountsEnabled={self.fileCountsEnabled}, '
            f'fileName="{self.fileName}", '
            f'fileNameAppend="{self.fileNameAppend}", '
            f'fileNameExtension="{self.fileNameExtension}", '
            f'filePath="{self.filePath}", '
            f'fileSize: {self.fileSize}, '
            f'fileSizesEnabled: {self.fileSizesEnabled}, '
            f'finished: {self.finished}, '
            f'id="{self.id}", '
            f'name="{self.name}", '
            f'severities=[{str_array(self.severities)}],'
            f'totalFileSizes={self.totalFileSizes}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _textlog_notification_action_dict)

        if isinstance(props, dict):
            disabledSources = []
            if 'disabledSources' in props:
                disabledSources = props['disabledSources']
            if isinstance(disabledSources, list):
                self.disabledSources = []
                for v in disabledSources:
                    if [item for item in NOTIFICATION_SOURCES].count(v) != 0:
                        self.disabledSources.append(v)

            scheme = EmailScheme.SMTP
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP

            severities = []
            if 'severities' in props:
                severities = props['severities']
            if isinstance(severities, list):
                self.severities = []
                for v in severities:
                    self.severities.append(NotificationActionSeverity(v))


_notification_actions_dict = {
    'modificationTime': 'modificationTime'
}


class NotificationActions(object):
    """The NotificationActions class has the attributes of notifications."""

    actions = []
    """Notification actions."""

    modificationTime = ''
    """Notification action type."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'NotificationActions({{'
            f'actions: [{repr_array(self.actions)}], '
            f'modificationTime: "{self.modificationTime}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Notification Actions: '
            f'actions=[{str_array(self.actions)}], '
            f'modificationTime="{self.modificationTime}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _notification_actions_dict)

        if isinstance(props, dict):
            actions = None
            if 'actions' in props:
                actions = props['actions']
            if isinstance(actions, list):
                self.actions = []
                for v in actions:
                    if isinstance(v, dict):
                        clsid = None
                        if 'clsid' in v:
                            clsid = v['clsid']
                            if clsid == 'FF13FDFE-31BA-40DD-AB8A-77A85C3A439A':
                                self.actions.append(EmailNotificationAction(v))
                            elif clsid == '0D8DFB6C-237C-4ADE-8C37-E215D4F8CF00':
                                self.actions.append(ExecuteNotificationAction(v))
                            elif clsid == 'B2DA6C79-C270-4988-8A20-995A0BB7A1CE':
                                self.actions.append(LogNotificationAction(v))
                            elif clsid == 'ED19F042-0A45-44A6-9C47-E2A9D696881C':
                                self.actions.append(SNMPNotificationAction(v))
                            elif clsid == '5D3B11A5-993F-4B18-B603-F1799AD3736E':
                                self.actions.append(SysLogNotificationAction(v))
                            elif clsid == 'EF21EA89-80C3-4801-98F6-544677CF12D0':
                                self.actions.append(TextLogNotificationAction(v))


_send_email_request_dict = {
    'body': 'body',
    'password': 'password',
    'port': 'port',
    'recipients': 'recipients',
    'scheme': 'scheme',
    'sender': 'sender',
    'server': 'server',
    'subject': 'subject',
    'useAuthentication': 'useAuthentication',
    'username': 'username'
}


class SendEmailRequest(object):
    """The SendEmailRequest class has the attributes of a send email request."""

    body = ''
    """Email body."""

    password = ''
    """Password."""

    port = 25
    """Port."""

    recipients = ''
    """Recipient list."""

    scheme = EmailScheme.SMTP
    """Email scheme."""

    sender = ''
    """Sender."""

    server = ''
    """SMTP server."""

    subject = ''
    """Email subject."""

    useAuthentication = False
    """Whether authentication is enabled."""

    username = ''
    """Username."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'SendEmailRequest({{'
            f'body: "{self.body}", '
            f'password: "{self.password}", '
            f'port: {self.port}, '
            f'recipients: "{self.recipients}", '
            f'scheme: {self.scheme}, '
            f'sender: "{self.sender}", '
            f'server: "{self.server}", '
            f'subject: "{self.subject}", '
            f'useAuthentication: {self.useAuthentication}, '
            f'username: "{self.username}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Send Email Request: '
            f'body="{self.body}", '
            f'password="{self.password}", '
            f'port={self.port}, '
            f'recipients="{self.recipients}", '
            f'scheme={self.scheme}, '
            f'sender="{self.sender}", '
            f'server="{self.server}", '
            f'subject="{self.subject}", '
            f'useAuthentication={self.useAuthentication}, '
            f'username="{self.username}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _send_email_request_dict)

        if isinstance(props, dict):
            scheme = None
            if 'scheme' in props:
                scheme = props['scheme']
            if isinstance(scheme, int):
                self.scheme = scheme if scheme in EmailScheme else EmailScheme.SMTP


_send_email_respone_dict = {
    'error': 'error'
}


class SendEmailResponse(object):
    """The SendEmailResponse class has the attributes of a send email response."""

    error = ''
    """Error."""

    result = PeekResult.OK
    """Result."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'SendEmailResponse({{'
            f'error: "{self.error}", '
            f'result: {self.result}'
            f'}})'
        )

    def __str__(self):
        return (
            f'Send Email Response: '
            f'error="{self.error}", '
            f'result={self.result}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _send_email_respone_dict)

        if isinstance(props, dict):
            result = PeekResult.OK
            if 'result' in props:
                result = props['result']
            if isinstance(result, int):
                self.result = result if result in PeekResult else PeekResult.OK


_send_notification_dict = {
    'context': 'context',
    'longMessage': 'longMessage',
    'shortMessage': 'shortMessage',
    'source': 'source',
    'sourceKey': 'sourceKey',
    'timestamp': 'timestamp'
}


class SendNotification(object):
    """The SendNotification class has the attributes of a send notification."""

    context = ''
    """Context."""

    longMessage = ''
    """Long message."""

    severity = Severity.INFORMATIONAL
    """Severity."""

    shortMessage = ''
    """short message."""

    source = ''
    """Source."""

    sourceKey = 0
    """Source key."""

    timestamp = ''
    """Timestamp."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'SendNotification({{'
            f'context: "{self.context}", '
            f'longMessage: "{self.longMessage}", '
            f'severity: {self.severity}, '
            f'shortMessage: "{self.shortMessage}", '
            f'source: "{self.source}", '
            f'sourceKey: {self.sourceKey}, '
            f'timestamp: "{self.timestamp}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Send Notification: '
            f'context="{self.context}", '
            f'longMessage="{self.longMessage}", '
            f'severity={self.severity}, '
            f'shortMessage="{self.shortMessage}", '
            f'source="{self.source}", '
            f'sourceKey={self.sourceKey}, '
            f'timestamp="{self.timestamp}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _send_notification_dict)

        if isinstance(props, dict):
            severity = Severity.INFORMATIONAL
            if 'severity' in props:
                severity = props['severity']
            if isinstance(severity, int):
                self.severity = severity if severity in Severity else Severity.INFORMATIONAL


class SendNotificationRequest(object):
    """The SendNotificationRequest class has the attributes of a send notification request."""

    notifications = []
    """Notifications."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'SendNotificationRequest({{'
            f'notifications: [{repr_array(self.notifications)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Send Notification Request: '
            f'notifications=[{str_array(self.notifications)}]'
        )

    def _load(self, props):
        if isinstance(props, dict):
            notifications = []
            if 'notifications' in props:
                notifications = props['notifications']
            if isinstance(notifications, list):
                self.notifications = []
                for v in notifications:
                    self.notifications.append(SendNotification(v))


NotificationAction = Union[
    EmailNotificationAction, ExecuteNotificationAction, LogNotificationAction,
    SNMPNotificationAction, SysLogNotificationAction, TextLogNotificationAction]


class Notifications(object):
    """The Notifications class is an interface into Notification operations."""

    engine = None
    """OmniEngine interface."""

    def __init__(self, engine):
        self.engine = engine

    def __repr__(self):
        return f'Notifications({repr(self.engine)})'

    def __str__(self):
        return 'Notifications'

    def get_notifications(self) -> Union[NotificationActions, None]:
        """Get the notifications"""
        if self.engine is not None:
            command = 'notifications/'
            pr = self.engine.perf('get_notifications')
            resp = self.engine._issue_command(command, pr, EO.GET)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get notifications.')
            return NotificationActions(resp)
        return None

    def set_notifications(self, notifications: NotificationActions) -> Union[dict, None]:
        """Sets the notifications"""
        if self.engine is not None:
            command = 'notifications/'
            pr = self.engine.perf('set_notifications')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(notifications, cls=OmniScriptEncoder))
            if not isinstance(resp, dict):
                raise OmniError('Failed to set notifications.')
            return resp
        return None

    def get_notification(self, notificationId: str) -> Union[NotificationActions, None]:
        """Get the notification"""
        if self.engine is not None:
            command = f'notifications/{notificationId}/'
            pr = self.engine.perf('get_notification')
            resp = self.engine._issue_command(command, pr, EO.GET)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get notification.')
            return NotificationActions(resp)
        return None

    def set_notification(self, notificationId: str,
                         notification: NotificationAction) -> Union[dict, None]:
        """Sets the notification"""
        if self.engine is not None:
            command = f'notifications/{notificationId}/'
            pr = self.engine.perf('set_notification')
            resp = self.engine._issue_command(command, pr, EO.PUT,
                                              data=json.dumps(notification, cls=OmniScriptEncoder))
            if not isinstance(resp, dict):
                raise OmniError('Failed to set notification.')
            return resp
        return None

    def delete_notification(self, notificationId: str) -> Union[dict, None]:
        """Deletes the notification"""
        if self.engine is not None:
            command = f'notifications/{notificationId}/'
            pr = self.engine.perf('delete_notification')
            resp = self.engine._issue_command(command, pr, EO.DELETE)
            if not isinstance(resp, dict):
                raise OmniError('Failed to delete notification.')
            return resp
        return None

    def send_email(self, email: SendEmailRequest) -> Union[SendEmailResponse, None]:
        """Sends an email"""
        if self.engine is not None:
            command = 'send/email/'
            pr = self.engine.perf('send_email')
            resp = self.engine._issue_command(command, pr, EO.POST,
                                              data=json.dumps(email, cls=OmniScriptEncoder))
            if not isinstance(resp, dict):
                raise OmniError('Failed to send email.')
            return SendEmailResponse(resp)
        return None

    def send_notifications(self, notifications: SendNotificationRequest) -> None:
        """Sends a notifications"""
        if self.engine is not None:
            command = 'send/notifications/'
            pr = self.engine.perf('send_notifications')
            data = json.dumps(notifications, cls=OmniScriptEncoder)
            self.engine._issue_command(command, pr, EO.POST, data=data)

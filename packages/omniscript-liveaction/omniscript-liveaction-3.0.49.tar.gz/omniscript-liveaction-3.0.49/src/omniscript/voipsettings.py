"""VoIP Settings class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import omniscript

from .omniid import OmniId

# Tags
_tag_classid = 'class_id'
_tag_label = 'VoIPConfig'
_tag_name = "name"
_tag_prop = "prop"
_tag_props = "properties"

# JSON Tags
_json_classid = 'clsid'
_json_enabled = 'enabled'


def _from_prop_boolean(value):
    return int(value) != 0


def _get_class_id(name):
    class_name_ids = omniscript.get_class_name_ids()
    id = class_name_ids[name]
    return id.format() if id else ''


class VoIPSettings(object):
    """VoIP Settings.
    """

    _class_id = None
    """The Class Identifier of the object."""

    max_calls = 2000
    """The maximum number of calls to track."""

    severity = 3
    """The serverity level of the notifications."""

    option_notify = True
    """Send notifications."""

    option_stop_analysis = True
    """Stop tracking VoIP calls if a notification is sent."""

    # Tags
    _json_label = 'voipConfig'
    _json_max_calls = 'maximumCalls'
    _json_severity = 'severity'
    _json_notify = 'notify'
    _json_stop_analysis = 'stopAnalysis'

    _tag_class_name = 'SimplePropBag'
    _tag_label = 'VoIPConfig'
    _tag_max_calls = 'max_calls'
    _tag_severity = 'severity'
    _tag_notify = 'option_notify'
    _tag_stop_analysis = 'option_stop_analysis'

    _tag_xml_root_name = _tag_props
    _tag_xml_max_calls = "MaxCalls"
    _tag_xml_notify = "Notify"
    _tag_xml_severity = "Severity"
    _tag_xml_stop_analysis = "StopAnalysis"

    _voip_prop_dict = {
        _json_classid: _tag_classid,
        _json_max_calls: _tag_max_calls,
        _json_notify: _tag_notify,
        _json_severity: _tag_severity,
        _json_stop_analysis: _tag_stop_analysis
    }

    def __init__(self):
        self.max_calls = VoIPSettings.max_calls
        self.severity = VoIPSettings.severity
        self.option_notify = VoIPSettings.option_notify
        self.option_stop_analysis = VoIPSettings.option_stop_analysis

    def _get_props(self):
        """Return the VoIP Settings as a Dictionary."""
        props = {}
        props[VoIPSettings._json_max_calls] = self.max_calls
        props[VoIPSettings._json_severity] = self.severity
        props[VoIPSettings._json_notify] = self.option_notify
        props[VoIPSettings._json_stop_analysis] = self.option_stop_analysis
        props[_json_classid] = _get_class_id(VoIPSettings._tag_class_name)
        return props

    def _load(self, props):
        """Load the VoIP Settings from a dictionairy."""
        if isinstance(props, dict):
            for k, v in props.items():
                a = VoIPSettings._voip_prop_dict.get(k)
                if a == _tag_classid:
                    self._class_id = OmniId(v)
                elif a == VoIPSettings._tag_max_calls:
                    self.max_calls = int(v)
                elif a == VoIPSettings._tag_severity:
                    self.severity = int(v)
                elif a == VoIPSettings._tag_notify:
                    self.option_notify = v
                elif a == VoIPSettings._tag_stop_analysis:
                    self.option_stop_analysis = v

    def _load_xml(self, obj):
        """Load the VoIP Settings from an ETree SubElement."""
        props = obj.find(VoIPSettings._tag_xml_root_name)
        if props is not None:
            for prop in props.findall(_tag_prop):
                propName = prop.attrib[_tag_name]
                if propName == VoIPSettings._tag_xml_max_calls:
                    self.max_calls = int(prop.text)
                elif propName == VoIPSettings._tag_xml_severity:
                    self.severity = int(prop.text)
                elif propName == VoIPSettings._tag_xml_notify:
                    self.option_notify = _from_prop_boolean(prop.text)
                elif propName == VoIPSettings._tag_xml_stop_analysis:
                    self.option_stop_analysis = _from_prop_boolean(prop.text)

    # def _store(self, props):
    #     """Store the VoIP Settings into a Dictionary."""
    #     if not isinstance(props, dict):
    #         return
    #     props[StatisticsOutputPreferencesSettings._json_label] = self._get_props()

    @classmethod
    def get_label(cls):
        return cls._tag_label

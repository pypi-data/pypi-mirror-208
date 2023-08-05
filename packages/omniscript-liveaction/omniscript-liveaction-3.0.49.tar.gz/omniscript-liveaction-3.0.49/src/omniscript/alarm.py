"""Alarm class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from typing import List, Union

from .helpers import load_props_from_dict
from .omniid import OmniId
from .peektime import PeekTime

from .invariant import AlarmTrackerType, FindType


class AlarmCondition(object):
    """A condition of an Alarm.
    """

    comparison_type = 0
    """The type of comparision to make."""

    duration = 0
    """Duration in seconds."""

    enabled = False
    """Is the Alarm enabled."""

    severity = 0
    """The severifty of the Alaram."""

    condition_type = 0
    """The type of Alarm."""

    value = 0.0
    """The value to be compared."""

    # Tags
    _json_comparison_type = 'comparisonType'
    _json_duration = 'duration'
    _json_enabled = 'enabled'
    _json_severity = 'severity'
    _json_condition_type = 'conditionType'
    _json_value = 'value'

    _tag_comparison_type = 'comparison_type'
    _tag_duration = 'duration'
    _tag_enabled = 'enabled'
    _tag_severity = 'severity'
    _tag_type = 'condition_type'
    _tag_value = 'value'

    _alarm_condition_prop_dict = {
        _json_comparison_type: _tag_comparison_type,
        _json_duration: _tag_duration,
        _json_enabled: _tag_enabled,
        _json_severity: _tag_severity,
        _json_condition_type: _tag_type,
        _json_value: _tag_value
    }

    def __init__(self, props: dict):
        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            load_props_from_dict(
                self, props, AlarmCondition._alarm_condition_prop_dict)

    def _format(self) -> dict:
        ret = {}
        for key, attribute in AlarmCondition._alarm_condition_prop_dict.items():
            ret[key] = getattr(self, attribute)
        return ret

    @classmethod
    def setup(cls, comparison_type: int, condition_type: int, duration: int, enabled: bool,
              severity: int, value: float):
        """ Class Method to return an instance populated with the parameters
        passed in. Pseudo constructor method.
        """
        return cls({
            AlarmCondition._json_comparison_type: comparison_type,
            AlarmCondition._json_duration: duration,
            AlarmCondition._json_enabled: enabled,
            AlarmCondition._json_severity: severity,
            AlarmCondition._json_condition_type: condition_type,
            AlarmCondition._json_value: value
        })


class TrackingSummary(object):
    """A Tracking Summary object.
    """

    flags = 0
    """The flags of the TrackingSummary."""

    id = None
    """The identifier of the TrackingSummary."""

    type = 0
    """The type of the TrackingSummary."""

    _json_flags = 'flags'
    _json_id = 'id'
    _json_type = 'summaryStatisticsType'

    _tag_flags = 'flags'
    _tag_id = 'id'
    _tag_type = 'type'

    _tracking_summary_prop_dict = {
        _json_flags: _tag_flags,
        _json_id: _tag_id,
        _json_type: _tag_type
    }

    def __init__(self, props: dict):
        self.flags = TrackingSummary.flags
        self.id = TrackingSummary.id
        self.type = TrackingSummary.type
        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == TrackingSummary._json_flags:
                    self.flags = int(v)
                elif k == TrackingSummary._json_id:
                    self.id = OmniId(v)
                elif k == TrackingSummary._json_type:
                    self.type = int(v)

    def _format(self) -> dict:
        ret = {}
        for key, attribute in TrackingSummary._tracking_summary_prop_dict.items():
            val = getattr(self, attribute)
            if isinstance(val, OmniId):
                ret[key] = str(val.get_id()).upper()
            else:
                ret[key] = getattr(self, attribute)
        return ret

    @classmethod
    def setup(cls, flags: int, id: int, summary_statistics_type: int):
        """ Class Method to return an instance populated with the parameters
        passed in. Pseudo constructor method.
        """
        return cls({
            TrackingSummary._json_flags: flags,
            TrackingSummary._json_id: id,
            TrackingSummary._json_type: summary_statistics_type,
        })


class StatisticsTracker(object):
    """An object that tracks the statistics of an Alarm.
    """

    classid = None
    """The OmniId of the object's class."""

    type = 0
    """The type of statistics to track."""

    history = 0
    """the history of the object."""

    summary = None
    """The summary of the tracker."""

    _json_classid = 'clsid'
    _json_type = 'statisticsType'
    _json_history = 'history'
    _json_summary = 'summary'

    _tab_classid = 'classid'
    _tab_type = 'type'
    _tab_history = 'history'
    _tab_summary = 'summary'

    _statistics_tracker_prop_dict = {
        _json_classid: _tab_classid,
        _json_type: _tab_type,
        _json_history: _json_history,
        _json_summary: _tab_summary
    }

    def __init__(self, props: dict):
        self.classid = None
        self.type = 0
        self.history = 0
        self.summary = None
        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == StatisticsTracker._json_classid:
                    self.classid = OmniId(v)
                elif k == StatisticsTracker._json_type:
                    self.type = int(v)
                elif k == StatisticsTracker._json_history:
                    self.history = int(v)
                elif k == StatisticsTracker._json_summary:
                    self.summary = TrackingSummary(v)

    def _format(self) -> dict:
        ret = {}
        for key, attribute in StatisticsTracker._statistics_tracker_prop_dict.items():
            val = getattr(self, attribute)
            if isinstance(val, TrackingSummary):
                ret[key] = val._format()
            elif isinstance(val, OmniId):
                ret[key] = str(val.get_id()).upper()
            else:
                ret[key] = getattr(self, attribute)
        return ret

    @classmethod
    def setup(cls, classid: str, type: int, history: int, summary: dict):
        """ Class Method to return an instance populated with the parameters
        passed in. Pseudo constructor method.
        """
        return cls({
            StatisticsTracker._json_classid: classid,
            StatisticsTracker._json_type: type,
            StatisticsTracker._json_history: history,
            StatisticsTracker._json_summary: summary,
        })


class Alarm(object):
    """The Alarm class has the attributes of an alarm.
    The :func:`get_alarm_list()
    <omniscript.omniengine.OmniEngine.get_alarm_list>`
    function returns a list of Alarm objects.
    """

    conditions = []
    """The conitions of the alarm."""

    created = None
    """The time and date the alarm was created as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    id = None
    """The alarms's identifier."""

    modified = None
    """The time and date of the last modification as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    name = ''
    """The name of the alarm."""

    tracker_type = AlarmTrackerType.UNDEFINED
    """The Track Type of the alarm."""

    tracker = None
    """The Statistics Tracker for the Alarm."""

    modification_time = ""
    """The last time any of the Alarms where modified."""

    find_types = (FindType.NAME, FindType.ID)

    _class_id = None

    _json_classid = 'clsid'
    _json_alarms = 'alarms'
    _json_classid_name = 'Alarm'
    _json_conditions = 'conditions'
    _json_created = 'created'
    _json_id = 'id'
    _json_modified = 'modified'
    _json_name = 'name'
    _json_tracker_type = 'trackType'
    _json_tracker = 'statisticsTracker'

    _tag_classid = '_class_id'
    _tag_conditions = 'conditions'
    _tag_created = 'created'
    _tag_id = 'id'
    _tag_modified = 'modified'
    _tag_name = 'name'
    _tag_tracker_type = 'tracker_type'
    _tag_tracker = 'tracker'

    _alarm_node_prop_dict = {
        _json_classid: _tag_classid,
        _json_conditions: _tag_conditions,
        _json_created: _tag_created,
        _json_id: _tag_id,
        _json_modified: _tag_modified,
        _json_name: _tag_name,
        _json_tracker_type: _tag_tracker_type,
        _json_tracker: _tag_tracker,
    }

    _endpoint = 'alarms/'
    """ Part of the REST API endpoint for the alarm collection """

    def __init__(self, criteria: dict = None):
        self.id = Alarm.id
        self.name = Alarm.name
        self.created = PeekTime()
        self.modified = PeekTime()
        self.tracker_type = Alarm.tracker_type
        self._load(criteria)

    def __str__(self) -> str:
        return f'Alarm: {self.name} -> {self.id.format() if self.id else ""}'

    def __eq__(self, other) -> bool:
        return (self.id, self.name, self.created, self.tracker_type) == (
            other.id, other.name, other.created, other.tracker_type)

    def _load(self, props: dict):
        if not isinstance(props, dict):
            return
        p_list = props.get('alarms')
        if isinstance(p_list, list) and len(p_list):
            _props = p_list[0]
        else:
            _props = props
        for k, v in _props.items():
            a = Alarm._alarm_node_prop_dict.get(k)
            if a == Alarm._tag_classid:
                self._class_id = OmniId(v)
            elif a == Alarm._tag_id:
                self.id = OmniId(v)
            elif a == Alarm._tag_conditions:
                self.conditions = _make_condition_list(v)
            elif a == Alarm._tag_created:
                self.created = PeekTime(v)
            elif a == Alarm._tag_modified:
                self.modified = PeekTime(v)
            elif a == Alarm._tag_name:
                self.name = v
            elif a == Alarm._tag_tracker_type:
                self.tracker_type = int(v)
            elif a == Alarm._tag_tracker:
                self.tracker = StatisticsTracker(v)
        if not self.id:
            self.id = OmniId(None)

    def _store(self) -> dict:
        props = {}
        for key, attribute in Alarm._alarm_node_prop_dict.items():
            val = getattr(self, attribute)
            if isinstance(val, OmniId):
                props[key] = str(val.get_id()).upper()
            elif isinstance(val, list):
                props[key] = [condition._format() for condition in val]
            elif isinstance(val, StatisticsTracker):
                props[key] = val._format()
            elif isinstance(val, PeekTime):
                props[key] = val.iso_time()
            else:
                props[key] = getattr(self, attribute)
        return props

    @classmethod
    def setup(cls, classid: str, conditions: List[dict], created: str, id: OmniId,
              modified: str, name: str, tracker: dict, tracker_type: AlarmTrackerType):
        """
        Class Method to return an instance populated with the parameters passed in.
        (Pseudo constructor method)
        """
        return cls({
            Alarm._json_classid: classid,
            Alarm._json_conditions: conditions,
            Alarm._json_created: created,
            Alarm._json_id: id,
            Alarm._json_modified: modified,
            Alarm._json_name: name,
            Alarm._json_tracker: tracker,
            Alarm._json_tracker_type: tracker_type
        })


def _make_condition_list(props: List[dict]) -> List[AlarmCondition]:
    result = []
    if isinstance(props, list):
        for condition in props:
            result.append(AlarmCondition(condition))
    return result


def _create_alarm_list(props: dict) -> List[Alarm]:
    lst = []
    if isinstance(props, dict):
        alarms = props.get('alarms')
        if alarms:
            for props in alarms:
                lst.append(Alarm(props))
        lst.sort(key=lambda x: x.name)
    return lst


def find_alarm(alarms: List[Alarm], value: Union[Alarm, OmniId, str],
               attrib: FindType = FindType.NAME) -> Union[Alarm, None]:
    """Finds an alarm in the list"""
    if (not alarms) or (attrib not in Alarm.find_types):
        return None

    if isinstance(value, Alarm):
        _value = value.id
        attrib = FindType.ID
    else:
        _value = value

    return next((i for i in alarms if getattr(i, attrib) == _value), None)

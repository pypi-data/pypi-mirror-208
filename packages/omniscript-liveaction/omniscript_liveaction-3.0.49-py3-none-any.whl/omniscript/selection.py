""" Selection Class """

# Copyright (c) LiveAction, Inc. 2022. All rights reserved.

from enum import Enum, IntEnum, unique

from .helpers import load_props_from_dict


class Selection(object):
    """ A Selection Object. Handles selecting all related packets based on parameters """

    @unique
    class Command(str, Enum):
        Cancel = 'cancel'
        Progress = 'progress'
        Results = 'results'

    @unique
    class Select(IntEnum):
        Source = 0
        Destination = 1
        SourceAndDestination = 2
        Protocol = 3
        Port = 4
        Conversation = 5
        VLAN = 6
        Application = 7

    @unique
    class Mode(IntEnum):
        AcceptAll = 0
        AcceptAnyMatching = 1
        RejectAll = 2
        RejectAnyMatching = 3
        AcceptAllMatching = 4
        RejectAllMatching = 5

    task_id = 0
    """ The selection task ID """

    progress = 0
    """ The percentage of the select related operation that has been completed """

    first_packet_data_time = ""
    """ The timestamp of the first selected packet in the array in ISO 8601 format """

    last_packet_date_time = ""
    """ The timestamp of the last selected packet in the array in ISO 8601 format """

    packets = []
    """ The list of packet numbers of the selected packets """

    _json_first_packet_date_time = 'firstPacketDateTime'
    _json_last_packet_date_time = 'lastPacketDateTime'
    _json_packets = 'packets'

    _selection_results_prop_dict = {
        _json_first_packet_date_time: 'first_packet_date_time',
        _json_last_packet_date_time: 'last_packet_date_time',
        _json_packets: 'packets'
    }

    def __init__(self, props: dict):
        self.task_id = Selection.task_id
        self.progress = Selection.progress
        self.first_packet_data_time = Selection.first_packet_data_time
        self.last_packet_date_time = Selection.last_packet_date_time
        self.packets = Selection.packets

        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            if 'taskId' in props:
                self.task_id = props['taskId']

    def update(self, progress: float):
        """ Update the progress of the select related operation """
        self.progress = progress

    @property
    def results(self) -> dict:
        """ Return the results dictionary for select related operation """
        return {
            Selection._json_first_packet_date_time: self.first_packet_data_time,
            Selection._json_last_packet_date_time: self.last_packet_date_time,
            Selection._json_packets: self.packets
        }

    @results.setter
    def results(self, props: dict):
        """ Update the results """
        load_props_from_dict(
            self, props, Selection._selection_results_prop_dict)

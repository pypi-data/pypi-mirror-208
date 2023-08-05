""" Protocol Translation Class """

# Copyright (c) LiveAction, Inc. 2022. All rights reserved.

from enum import Enum
from typing import List

from .helpers import load_props_from_dict


class ProtocolTranslation(object):
    """ A Protocol Translation Object. Handles mapping of port & protocol combination """

    class PortType(Enum):
        TCP = 0
        UDP = 1
        SCTP = 2
        SCTP_PAYLOAD_ID = 3

    port = 0
    """ The port number for the translation """

    protospec = 0
    """ The protospec mapping for the translation """

    port_type = PortType.TCP.value
    """ The type of the port for the translation """

    find_attributes = ('port', 'protospec', 'type')
    """ Attributes to search list of Protocols on. """

    endpoint = 'protocol-translations/'
    """ Part of the REST API endpoint for the protocol translation collection """

    _json_port = 'port'
    _json_protospec = 'protospec'
    _json_type = 'type'

    _protocol_translation_props_dict = {
        _json_port: 'port',
        _json_protospec: 'protospec',
        _json_type: 'port_type'
    }

    def __init__(self, props: dict):
        self._load(props)

    def __str__(self) -> str:
        return f'{self.props}'

    def __eq__(self, other) -> bool:
        """ Compare this instance to another for same values """
        return ((self.port, self.protospec, self.port_type)
                == (other.port, other.protospec, other.port_type))

    def _load(self, props: dict):
        """ Load the props if they exist """
        if isinstance(props, dict):
            load_props_from_dict(
                self, props, ProtocolTranslation._protocol_translation_props_dict)

    @property
    def props(self) -> dict:
        """ Return props as dictionary in correct format for json """
        return {
            ProtocolTranslation._json_port: self.port,
            ProtocolTranslation._json_protospec: self.protospec,
            ProtocolTranslation._json_type: self.port_type
        }


def _create_protocol_translations_list(props: dict) -> List[ProtocolTranslation]:
    """ External facing method that creates a list of protocol translations objects """
    list_ = []
    if isinstance(props, dict):
        translation_list = props.get('protocolTranslations')
        if isinstance(translation_list, list):
            for translation in translation_list:
                list_.append(ProtocolTranslation(translation))
        list_.sort(key=lambda x: x.protospec)

    return list_

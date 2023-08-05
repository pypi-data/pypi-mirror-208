"""AuthenticationToken class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from typing import List

from .helpers import load_props_from_dict

find_attribs = ['name', 'code']


class AuthenticationToken(object):
    """An Authentication Token object.
    """

    authentication_token_id = ''
    """The authenticaion token identifier of the token."""

    client = ''
    """The name of the client of the token."""

    expiration_time = ''
    """When the token expires."""

    label = ''
    """The label of the token."""

    last_activity_time = ''
    """The timestamp of when the token was last used."""

    user_domain = ''
    """The user domain of the token."""

    user_id = ''
    """The user's identifier of the token."""

    user_information_id = 0
    """The user information identifier of the token."""

    user_name = ''
    """The user's name of the token."""

    option_authentication = False
    """"Has the token been authenticated."""

    option_enabled = False
    """Is the token enabled."""

    # Tags
    _json_authentication_token_id = 'authTokenId'
    _json_client = 'client'
    _json_expiration_time = 'expirationTime'
    _json_label = 'label'
    _json_last_activity_time = 'lastActivityTime'
    _json_user_domain = 'userDomain'
    _json_user_id = 'userId'
    _json_user_information_id = 'userInfoId'
    _json_user_name = 'userName'
    _json_option_authentication = 'authentication'
    _json_option_enabled = 'enabled'

    _tag_authentication_token_id = 'authentication_token_id'
    _tag_client = 'client'
    _tag_expiration_time = 'expiration_time'
    _tag_label = 'label'
    _tag_last_activity_time = 'last_activity_time'
    _tag_user_domain = 'user_domain'
    _tag_user_id = 'user_id'
    _tag_user_information_id = 'user_information_id'
    _tag_user_name = 'user_name'
    _tag_option_authentication = 'option_authentication'
    _tag_option_enabled = 'option_enabled'

    # Props format for when authentication tokens need to be modified
    _modify_auth_token_prop_dict = {
        _json_client: _tag_client,
        _json_expiration_time: _tag_expiration_time,
        _json_label: _tag_label,
        _json_option_authentication: _tag_option_authentication,
        _json_option_enabled: _tag_option_enabled
    }

    # Props format for when authentication tokens need to be created
    _create_auth_token_prop_dict = {
        _json_user_domain: _tag_user_domain,
        _json_user_id: _tag_user_id,
        _json_user_information_id: _tag_user_information_id,
        _json_user_name: _tag_user_name,
        **_modify_auth_token_prop_dict
    }

    # Expected props format for when receiving authentication tokens
    _get_auth_token_prop_dict = {
        _json_authentication_token_id: _tag_authentication_token_id,
        _json_last_activity_time: _tag_last_activity_time,
        **_create_auth_token_prop_dict
    }

    endpoint = 'token/'
    """ Part of the REST API endpoint for the authentication token collection """

    def __init__(self, props: dict) -> None:
        self._load(props)

    def __eq__(self, other) -> bool:
        return ((self.option_authentication, self.authentication_token_id, self.client,
                 self.option_enabled, self.expiration_time, self.label, self.user_domain,
                 self.user_id, self.user_information_id, self.user_name)
                == (other.option_authentication, other.authentication_token_id, other.client,
                    other.option_enabled, other.expiration_time, other.label,
                    other.user_domain, other.user_id, other.user_information_id,
                    other.user_name))

    def __str__(self) -> str:
        return f'{self._create_template()}'

    def _load(self, props: dict):
        if not isinstance(props, dict):
            return
        load_props_from_dict(
            self, props, AuthenticationToken._get_auth_token_prop_dict)

    def _format(self, prop_dict: dict) -> dict:
        ret = {}
        for key, attribute in prop_dict.items():
            ret[key] = getattr(self, attribute)
        return ret

    def _create_template(self) -> dict:
        """ Create the template for the create authentication tokens commands """
        return self._format(AuthenticationToken._create_auth_token_prop_dict)

    def _modify_template(self) -> dict:
        """ Create the template for the modify authentication tokens commands """
        return self._format(AuthenticationToken._modify_auth_token_prop_dict)

    @classmethod
    def create(cls, authentication: bool, client: str, enabled: bool, expiration_time: str,
               label: str, user_domain: str, user_id: str, user_info_id: int, user_name: str):
        return cls({
            AuthenticationToken._json_option_authentication: authentication,
            AuthenticationToken._json_client: client,
            AuthenticationToken._json_option_enabled: enabled,
            AuthenticationToken._json_expiration_time: expiration_time,
            AuthenticationToken._json_label: label,
            AuthenticationToken._json_user_domain: user_domain,
            AuthenticationToken._json_user_id: user_id,
            AuthenticationToken._json_user_information_id: user_info_id,
            AuthenticationToken._json_user_name: user_name
        })


def _create_authentication_token_list(props: dict) -> List[AuthenticationToken]:
    lst = []
    if 'tokens' in props:
        tokens = props.get('tokens')
        if isinstance(tokens, list):
            for t in tokens:
                lst.append(AuthenticationToken(t))
    return lst

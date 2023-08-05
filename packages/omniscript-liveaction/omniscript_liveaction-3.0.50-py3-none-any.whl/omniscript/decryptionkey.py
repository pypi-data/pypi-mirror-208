"""Decryption Key class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .omniid import OmniId


class DecryptionKey(object):
    """The DecryptionKey class has the attributes of a decryption key.
    The :func:`get_decryption_key_list()
    <omniscript.omniengine.OmniEngine.get_decrypt_key_list>`
    function returns a list of DecryptionKey objects.
    """

    # TODO: Replace with OmniId.
    id = None
    """The decryption key's unique identifier.
    Format AAAAAAAA-BBBB-AAAA-BBBB-ABABABABABAB
    """

    name = ''
    """The name of the decryption key this can be changed via an API call
    """

    password_protected = False
    """ Boolean that returns true if the decryption key is password protected.
    """

    find_attributes = ('name', 'id')
    """Searchable attributes for decryption keys can search by name or unique ID.
    """
    def __init__(self, props: dict):
        self.id = DecryptionKey.id
        self.name = DecryptionKey.name
        self.password_protected = DecryptionKey.password_protected
        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == 'id':
                    self.id = OmniId(v) if v is not None else OmniId(True)
                elif k == 'name':
                    self.name = v
                elif k == 'passwordProtected':
                    self.password_protected = v

    def __repr__(self):
        return (f'DecryptionKey id:{self.id} name:{self.name} password_protected: '
                f'{self.password_protected}')

    def __str__(self):
        return (f'DecryptionKey id:{self.id} name:{self.name} password_protected: '
                f'{self.password_protected}')


def _create_decryption_key_list(props: dict):
    lst = []
    if isinstance(props, dict):
        decryptkeys = props.get('keys')
        if isinstance(decryptkeys, list):
            for k in decryptkeys:
                lst.append(DecryptionKey(k))
        lst.sort(key=lambda x: x.name)
    return lst


def find_decryption_key(decryptkeys: list, value, attrib=DecryptionKey.find_attributes[0]):
    """Find the DecryptionKey in the list that matches the provided ID."""
    if (not decryptkeys) or (attrib not in DecryptionKey.find_attributes):
        return None

    if len(decryptkeys) == 0:
        return None

    if isinstance(value, DecryptionKey):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in decryptkeys if getattr(i, attrib) == _value), None)

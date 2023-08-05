"""Decryption Key Template class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .omniid import OmniId


class DecryptionKeyTemplate(object):
    """The DecryptionKeyTemplate class has the attributes of a decryption key to be added.
    The
    :func:`add_decryption_key_list()
    <omniscript.omniengine.OmniEngine.get_decrypt_key_list>`
    function returns a list of DecryptionKey objects.
    """

    name = ''
    """The name of the decryption key this can be changed via an API call
    """

    password = ''
    """The decryption key's password. Set when adding decryption keys
    """

    id = None
    """The decryption key's unique identifier.
    Format AAAAAAAA-BBBB-AAAA-BBBB-ABABABABABAB
    """

    certificate = None
    """ Server certificate associated with the decryption key.
    """

    private_key = None
    """The private key (decryption key). Set when adding a key
    """

    # Tags
    _json_certificate = 'certificate'
    _json_id = 'id'
    _json_name = 'name'
    _json_password = 'password'
    _json_private_key = 'privateKey'

    def __init__(self, name: str, password='', id=None, cert_file_path=None,
                 privkey_file_path=None):
        self.name = name
        self.password = password
        self.id = OmniId(id) if id is not None else OmniId(True)
        if cert_file_path is not None:
            self.load_certificate(cert_file_path)
        if privkey_file_path is not None:
            self.load_private_key(privkey_file_path)

    def load_certificate(self, cert_file_path):
        certfile = open(cert_file_path, 'rb')
        try:
            cert_byte_array = certfile.read(-1)
            self.certificate = cert_byte_array
        except IOError:
            print('Error while opening certificatete file!')

    def load_private_key(self, privkey_file_path):
        privkey_file = open(privkey_file_path, 'rb')
        try:
            privkey_byte_array = privkey_file.read(-1)
            self.private_key = privkey_byte_array
        except IOError:
            print('Error while opening private key file!')

    def _store(self):
        props = {}
        cert_str = self.certificate.decode('utf-8') if self.certificate is not None else ''
        privkey_str = self.private_key.decode('utf-8') if self.private_key is not None else ''
        props[DecryptionKeyTemplate._json_certificate] = cert_str
        props[DecryptionKeyTemplate._json_id] = self.id.format()
        props[DecryptionKeyTemplate._json_name] = self.name
        if self.password != '':
            props[DecryptionKeyTemplate._json_password] = self.password
        props[DecryptionKeyTemplate._json_private_key] = privkey_str
        return props

    def __repr__(self) -> str:
        return (f'DecryptionKeyTemplate name: {self.name} password: {self.password} id:{self.id} '
                f'certificate:{self.certificate} :privateKey {self.private_key}')

    def __str__(self) -> str:
        return (f'DecryptionKeyTemplate name: {self.name} password: {self.password} id:{self.id} '
                f'certificate:{self.certificate} :privateKey {self.private_key}')

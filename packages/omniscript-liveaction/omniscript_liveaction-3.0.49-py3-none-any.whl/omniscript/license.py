""" License Class """
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.

from enum import Enum

from .helpers import load_props_from_dict


class LicenseSettings(object):
    """ License settings helper class """

    license_id = ''
    """ License ID """

    product_key = ''
    """ Product activation key """

    _json_license_id = 'licenseId'
    _json_product_key = 'productKey'

    _license_settings_prop_dict = {
        _json_license_id: 'license_id',
        _json_product_key: 'product_key'
    }

    endpoint = 'license/settings/'

    def __init__(self, props: dict):
        self._load(props)

    def __eq__(self, other):
        return (self.license_id, self.product_key) == (other.license_id, other.product_key)

    def _load(self, props: dict):
        if isinstance(props, dict):
            load_props_from_dict(
                self, props, LicenseSettings._license_settings_prop_dict)

    def _format(self) -> dict:
        ret = {}
        for key, attribute in LicenseSettings._license_settings_prop_dict.items():
            ret[key] = getattr(self, attribute)
        return ret

    @classmethod
    def setup(cls, license_id: str, product_key: str):
        """ Class Method to return an instance populated with the parameters passed in. """
        return cls({
            LicenseSettings._json_license_id: license_id,
            LicenseSettings._json_product_key: product_key
        })


class License(object):
    """ License class """

    class Flags(Enum):
        PROM_ID = 1
        IP_ADDRESS = 2
        DISK_ID = 4
        HOST_NAME = 8
        MAC_ADDRESS = 16
        HD_SERIAL_NUMBER = 2048
        CPU_INFORMATION = 4096
        UUID = 8192

    _json_aid = 'aid'
    _json_eid = 'eid'
    _json_expiration_date = 'expirationDate'
    _json_expired = 'expired'
    _json_type = 'type'
    _json_valid = 'valid'

    _license_prop_dict = {
        _json_aid: _json_aid,
        _json_eid: _json_eid,
        _json_expiration_date: 'expiration_date',
        _json_expired: _json_expired,
        _json_type: _json_type,
        _json_valid: _json_valid
    }

    endpoint = 'license/'

    def __init__(self, props: dict):
        # self.locking_code = ''
        # self.settings = None
        self._load(props)

    def _load(self, props: dict):
        if isinstance(props, dict):
            load_props_from_dict(
                self, props, License._license_prop_dict)

    def _format(self) -> dict:
        ret = {}
        for key, attribute in License._license_prop_dict.items():
            ret[key] = getattr(self, attribute)
        return ret

    @property
    def locking_code(self) -> str:
        return self.locking_code

    @locking_code.setter
    def locking_code(self, code: str):
        self.locking_code = code

    @property
    def settings(self):
        return self.settings._format()

    @settings.setter
    def settings(self, val):
        self.settings = LicenseSettings(val)

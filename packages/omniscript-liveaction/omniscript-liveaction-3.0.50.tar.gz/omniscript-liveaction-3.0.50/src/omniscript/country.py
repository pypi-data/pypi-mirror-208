"""Country class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.


class Country(object):
    """An Country object.
    """

    code = ''
    """The country code of the Country."""

    name = ''
    """The name of the Country."""

    # Tags
    _tag_code = 'code'
    _tag_name = 'name'

    def __init__(self, props):
        self.code = Country.code
        self.name = Country.name
        self._load(props)

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == Country._tag_code:
                    self.code = v
                elif k == Country._tag_name:
                    self.name = v


def _create_country_list(props):
    lst = []
    if isinstance(props, dict):
        if 'countries' in props:
            countries = props.get('countries')
            if isinstance(countries, list):
                for c in countries:
                    lst.append(Country(c))
    return lst


def create_country_name_dictionary(countries):
    """Create a diction with the country name as the key
    and the country code as the value.

    Input:
        countries as a dictionary of with one element 'countries', a list
        of 'code' and 'name' dictionary elements.
        Or as a list of Country objects.
    """
    dct = {}
    if isinstance(countries, dict):
        if 'countries' in countries:
            _countries = countries.get('countries')
            if isinstance(_countries, list):
                for c in countries:
                    dct[c.name] = c.code
    if isinstance(countries, list):
        for c in countries:
            dct[c.name] = c.code
    return dct


def create_country_code_dictionary(countries):
    """Create a diction with the country code as the key
    and the country code as the value.

    Input:
        countries as a dictionary of with one element 'countries', a list
        of 'code' and 'name' dictionary elements.
        Or as a list of Country objects.
    """
    dct = {}
    if isinstance(countries, dict):
        if 'countries' in countries:
            _countries = countries.get('countries')
            if isinstance(_countries, list):
                for c in countries:
                    dct[c.code] = c.name
    if isinstance(countries, list):
        for c in countries:
            dct[c.code] = c.name
    return dct

"""Application class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.


find_attribs = ['name', 'id']


class Application(object):
    """An Application object.
    """

    category = ''
    """The category of the Application."""

    color = 0
    """The color of the Application."""

    description = ''
    """The description of the Application."""

    id = ''
    """The identifier of the Application"""

    name = ''
    """The name of the Application."""

    productivity = 0
    """The productivity level of the Application."""

    reference = ''
    """The reference value of the Application."""

    risk = 0
    """The risk level of the application."""

    # Tags
    _tag_category = 'category'
    _tag_color = 'color'
    _tag_description = 'description'
    _tag_id = 'id'
    _tag_name = 'name'
    _tag_productivity = 'productivity'
    _tag_reference = 'reference'
    _tag_risk = 'risk'

    def __init__(self, props):
        self.category = Application.category
        self.color = Application.color
        self.description = Application.description
        self.id = Application.id
        self.name = Application.name
        self.productivity = Application.productivity
        self.reference = Application.reference
        self.risk = Application.risk
        self._load(props)

    def _load(self, props):
        if isinstance(props, dict):
            for k, v in props.items():
                if k == Application._tag_category:
                    self.category = v
                elif k == Application._tag_color:
                    self.color = int(v.strip('#'), 16)
                elif k == Application._tag_description:
                    self.description = v
                elif k == Application._tag_id:
                    self.id = v
                elif k == Application._tag_name:
                    self.name = v
                elif k == Application._tag_productivity:
                    self.productivity = int(v)
                elif k == Application._tag_reference:
                    self.reference = v
                elif k == Application._tag_risk:
                    self.risk = int(v)


def _create_application_list(props):
    lst = []
    if isinstance(props, dict):
        if 'applications' in props:
            apps = props.get('applications')
            if isinstance(apps, list):
                for app in apps:
                    lst.append(Application(app))
    return lst

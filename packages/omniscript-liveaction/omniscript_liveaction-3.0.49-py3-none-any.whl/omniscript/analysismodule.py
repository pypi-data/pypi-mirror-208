"""AnalysisModule class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .omniid import OmniId


_plugin_prop_dict = {
    'Identifier': 'id',
    'Name': 'name'
}


class AnalysisModule(object):
    """The AnalysisModule class has the attributes of an analysis module
    (plugin). The
    :func:`get_analysis_module_list()
    <omniscript.omniengine.OmniEngine.get_analysis_module_list>`
    function returns a list of AnalysisModule objects.
    """

    category_ids = []
    """The analysis module's list of category identifier."""

    configuration = None
    """For an instance of an Analysis Module in a CaptureTemplate, the
    configuration information for the instance.
    """

    engine = None
    """The OmniEngine of the analysis module."""

    file_name = None
    """The analysis module's file name on its OmniEngine."""

    id = None
    """The analysis module's identifier."""

    name = ''
    """The name of the analysis module."""

    publisher = None
    """The analysis module's publisher."""

    version = None
    """The version of the analysis module."""

    find_attributes = ('name', 'id')

    def __init__(self, engine, props=None, id=None):
        self.engine = engine
        self.category_ids = AnalysisModule.category_ids
        self.configuration = AnalysisModule.configuration
        self.file_name = AnalysisModule.file_name
        self.id = AnalysisModule.id
        self.name = AnalysisModule.name
        self.publisher = AnalysisModule.publisher
        self.version = AnalysisModule.version
        if props is not None:
            self._load(props)
        elif id is not None:
            self.id = id

    def __str__(self):
        return f'AnalysisModule: {self.name}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == 'clsid':
                self.id = OmniId(v)
            elif k == 'cagegoryIds':
                self.category_ids = v
            elif k == 'file':
                self.file_name = v
            elif k == 'name':
                self.name = v
            elif k == 'publisher':
                self.publisher = v
            elif k == 'version':
                self.version = v

    def get_configuration(self):
        return self.configuration

    def set_configuration(self, config):
        self.configuration = config


def _create_analysis_module_list(engine, props):
    lst = []
    if props and len(props) > 0:
        for plugin in props:
            lst.append(AnalysisModule(engine, plugin))
    lst.sort(key=lambda x: x.name)
    return lst


def find_analysis_module(analysis_modules, value, attrib=AnalysisModule.find_attributes[0]):
    """Finds an analysis module in the list"""
    if (not analysis_modules) or (attrib not in AnalysisModule.find_attributes):
        return None

    if len(analysis_modules) == 0:
        return None

    if isinstance(value, AnalysisModule):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in analysis_modules if getattr(i, attrib) == _value), None)

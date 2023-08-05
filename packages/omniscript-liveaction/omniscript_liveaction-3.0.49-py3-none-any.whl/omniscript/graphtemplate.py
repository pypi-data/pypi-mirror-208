"""GraphTemplate class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .omniid import OmniId
from .peektime import PeekTime

find_attribs = ['name', 'id']


class GraphItem(object):
    """The GraphItem class.
    A GraphTemplate contains a list of GraphItems.
    """

    id = OmniId()
    """The graph item's identifier."""

    name = ''
    """The name of the graph item."""

    description = ''
    """The description of the graph item."""

    unit_type = 0
    """The unit type of graph item"""

    item_id = None
    """The statistic item id of the graph item"""

    type = 0
    """The statistic type of the graph item"""

    flags = 0
    """The statistic flags of the graph item"""

    def __init__(self, criteria):
        self.id = GraphItem.id
        self.name = GraphItem.name
        self.description = GraphItem.description
        self._load(criteria)

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == 'id':
                self.id = OmniId(v)
            elif k == 'name':
                self.name = v
            elif k == 'description':
                self.description = v
            elif k == 'unitType':
                self.type = int(v)
            elif k == 'statisticItemId':
                self.item_id = OmniId(v)
            elif k == 'statisticType':
                self.type = int(v)
            elif k == 'statisticFlags':
                self.flags = int(v)


class GraphTemplate(object):
    """The GraphTemplate class has the attributes of an Graph Template.
    The
    :func:`get_graph_template_list()
    <omniscript.omniengine.OmniEngine.get_graph_template_list>`
    function returns a list of GraphTemplate objects.
    """

    id = OmniId()
    """The graph template's identifier."""

    name = ''
    """The name of the graph template."""

    description = ''
    """The description of the graph template."""

    graph_id = OmniId()
    """The graph identifier of the graph template."""

    start = 0
    """The start value"""

    sample_interval = 0
    """The sample interval"""

    sample_count = 0
    """The sample count"""

    graph_item_list = []
    """The list of graph items"""

    find_attributes = ('name', 'id')

    def __init__(self, criteria):
        self.id = OmniId(True) if criteria is None else GraphTemplate.id
        self.name = GraphTemplate.name
        self.description = GraphTemplate.description
        self.graph_id = OmniId(True) if criteria is None else GraphTemplate.graph_id
        self.start = GraphTemplate.start
        self.sample_interval = GraphTemplate.sample_interval
        self.sample_count = GraphTemplate.sample_count
        self.graph_item_list = GraphTemplate.graph_item_list
        self._load(criteria)

    def __str__(self):
        return f'GraphTemplate: {self.name}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k, v in props.items():
            if k == 'templateId':
                self.id = OmniId(v)
            elif k == 'title':
                self.name = v
            elif k == 'description':
                self.description = v
            elif k == 'id':
                self.graph_id = OmniId(v)
            elif k == 'startTime':
                self.start = PeekTime(v)
            elif k == 'sampleInterval':
                self.sample_interval = int(v)
            elif k == 'sampleCount':
                self.sample_count = int(v)
            elif k == 'graphItems':
                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            self.graph_item_list.append(GraphItem(i))
        if self.id is None:
            self.id = OmniId(None)


def _create_graph_template_list(props):
    lst = []
    graphs = props.get('graphs')
    for template in graphs:
        lst.append(GraphTemplate(criteria=template))
    lst.sort(key=lambda x: x.name)
    return lst


def find_graph_template(graphs, value, attrib=GraphTemplate.find_attributes[0]):
    """Finds a graph_template in the list"""
    if (not graphs) or (attrib not in GraphTemplate.find_attributes):
        return []

    if len(graphs) == 0:
        return []

    if isinstance(value, GraphTemplate):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in graphs if getattr(i, attrib) == _value), [])

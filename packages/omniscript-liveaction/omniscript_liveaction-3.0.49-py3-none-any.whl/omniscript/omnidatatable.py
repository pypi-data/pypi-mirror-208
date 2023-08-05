"""OmniDataTable class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .omnierror import OmniError
from .readstream import ReadStream


class OmniDataTable(object):
    """Parses a serialized IDataTable object into itself.
    This class is used by other OmniScript classes to parse binary data
    returned by an OmniEngine.
    """

    labels = []
    """The column labels"""

    types = []
    """The data type of each column."""

    rows = []
    """The rows of the Data Table, each element of a row is a list of
    len(labels) elements. Empty elements (cells) are set to None.
    """

    def __init__(self):
        self.labels = []
        self.types = []
        self.rows = []

    def load(self, data):
        """Load the Data Table from a string buffer containing a serialized
        IDataTable object.
        """
        stream = ReadStream(data)
        # print len(data)
        if len(data) < 8:
            return
        # TODO: use a readstream.
        major_ver = stream.read_uint()
        stream.read_uint()      # minor_ver
        # Expecting Version 3.0
        if major_ver != 3:
            raise OmniError('Unsupported Data Table version.')
        column_count = stream.read_uint()
        row_count = stream.read_uint()
        for _ in range(column_count):
            _type = stream.read_ushort()
            self.types.append(_type)
            label = stream.read_unicode()
            self.labels.append(label)
        for _ in range(row_count):
            row = []
            for _ in range(column_count):
                _type = stream.read_ushort()
                if _type == 3:
                    row.append(stream.read_uint())
                elif _type == 8:
                    row.append(stream.read_string())
                elif _type == 19:
                    row.append(stream.read_int())
                elif _type == 21:
                    row.append(stream.read_ulong())
                elif _type == 22:
                    row.append(stream.read_uint())
                elif _type == 23:
                    row.append(stream.read_uint())
                elif _type == 0:
                    row.append(None)
                else:
                    # print 'Row:', r, 'Column', c, 'Unknown Type:', type
                    # raise TypeError('Invalid type in data.')
                    pass
            self.rows.append(row)

    def __str__(self):
        return 'OmniDataTable'

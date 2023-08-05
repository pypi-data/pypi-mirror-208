"""OmniId class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import uuid

from .invariant import ID_FLAG_NONE, ID_FLAG_BRACES, ID_FLAG_LOWERCASE


class OmniId(object):
    """A uuid.UUID with a default string format:
    {ABCDEF01-2345-6789-ABCD-0123456789AB}
    """

    id = None
    """The UUID (GUID)."""

    null_id = uuid.UUID(int=0)

    def __init__(self, value=None, create=False, bytes_le=None):
        """Initialize the OmniId

        Args:
            value(str or bool) : optional initial value or flag to
                                 generate a new GUID.
        """
        if value is not None:
            if isinstance(value, OmniId):
                self.id = value.id
            elif isinstance(value, six.string_types):
                self.id = uuid.UUID(value)
            elif isinstance(value, bool) and value:
                self.id = uuid.uuid4()
            else:
                self.id = OmniId.null_id
        elif bytes_le is not None:
            self.id = uuid.UUID(bytes_le=bytes_le)
        else:
            self.id = OmniId.null_id

    def __cmp__(self, other):
        if isinstance(other, OmniId):
            return (self.id == other.id)
        if isinstance(other, six.string_types):
            return (self.id == uuid.UUID(other))

    def __eq__(self, other):
        if isinstance(other, OmniId):
            return (self.id == other.id)
        if isinstance(other, six.string_types):
            return (self.id == uuid.UUID(other))

    def __hash__(self):
        return self.id.__hash__()

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.id}")'

    def __str__(self):
        return f'{(str(self.id)).upper()}' if self.id else ''

    def bytes_le(self):
        """Return the id as a 16-byte string in little-endian format"""
        return self.id.bytes_le

    def format(self, flags=ID_FLAG_NONE):
        """Return the id as a string with formatting based on flags.

        Default: Uppercase without curly braces.

        Args:
            flags(int) : ID_FLAG_NONE, ID_FLAG_NO_BRACES,
            ID_FLAG_BRACES, ID_FLAG_LOWERCASE, ID_FLAG_UPPERCASE
        """
        if self.id is None:
            return ''
        result = str(self.id).lower() if (flags & ID_FLAG_LOWERCASE) else str(self.id).upper()
        if flags & ID_FLAG_BRACES:
            return f'{{{result}}}'
        return result

    def get_id(self):
        """return the UUID of the OmniId."""
        return self.id

    @staticmethod
    def is_id(value):
        if isinstance(value, OmniId):
            return True
        if isinstance(value, six.string_types):
            if len(value) == 38:
                if value[0] != '{':
                    return False
                if value[9] != '-':
                    return False
                if value[14] != '-':
                    return False
                if value[19] != '-':
                    return False
                if value[24] != '-':
                    return False
                if value[37] != '}':
                    return False
                return True
        return False

    def parse(self, value):
        """Parse the value into the id."""
        self.id = uuid.UUID(value)

    def new(self):
        """Create a new UUID/GUID."""
        self.id = uuid.uuid4()

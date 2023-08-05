"""ReadStream class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

# " ".join(['%02X' % ord(b) for b in data])

import os
import struct

import omniscript

from .omnierror import OmniError
from .omniid import OmniId


class ReadStream(object):
    """A class to read and parse a stream of bytes.
    """

    def __init__(self, data):
        self.data = data
        self.offset = 0

    def eof(self):
        """At the end of the stream?"""
        return self.offset >= len(self.data)

    def find(self, value):
        """Find a value in the entire stream of bytes.
        Return the offset where the value is found."""
        return self.data.find(value)

    def length(self):
        """Total number of bytes in the stream."""
        return len(self.data)

    def read(self, length):
        """Read a number of bytes and adavance the
        current position.
        """
        value = struct.unpack_from(f'={length}s', self.data, self.offset)[0]
        self.seek(length, os.SEEK_CUR)
        return value

    def read_byte(self):
        """Read a single byte and advance the current position."""
        value = struct.unpack_from('=B', self.data, self.offset)[0]
        self.seek(1, os.SEEK_CUR)
        return value

    def read_short(self):
        """Read a short, 2-byte, signed value and advance the
        current position.
        """
        value = struct.unpack_from('=h', self.data, self.offset)[0]
        self.seek(2, os.SEEK_CUR)
        return value

    def read_ushort(self):
        """Read a short, 2-byte, unsigned value and advance the
        current position.
        """
        value = struct.unpack_from('=H', self.data, self.offset)[0]
        self.seek(2, os.SEEK_CUR)
        return value

    def read_int(self):
        """Read an integer, 4-byte, signed value and advance the
        current position.
        """
        value = struct.unpack_from('=i', self.data, self.offset)[0]
        self.seek(4, os.SEEK_CUR)
        return value

    def read_uint(self):
        """Read an integer, 4-byte, unsigned value and advance the
        current position.
        """
        value = struct.unpack_from('=I', self.data, self.offset)[0]
        self.seek(4, os.SEEK_CUR)
        return value

    def read_long(self):
        """Read a long, 8-byte, signed value and advance the
        current position.
        """
        value = struct.unpack_from('=q', self.data, self.offset)[0]
        self.seek(8, os.SEEK_CUR)
        return value

    def read_ulong(self):
        """Read a long, 8-byte, unsigned value and advance the
        current position.
        """
        value = struct.unpack_from('=Q', self.data, self.offset)[0]
        self.seek(8, os.SEEK_CUR)
        return value

    def read_double(self):
        """Read a long, 8-byte, floating-point value and advance the
        current position.
        """
        value = struct.unpack_from('=d', self.data, self.offset)[0]
        self.seek(8, os.SEEK_CUR)
        return value

    def read_guid(self):
        """Read a 16-byte GUID and advance the current position."""
        value = struct.unpack_from('=16s', self.data, self.offset)[0]
        id = OmniId(bytes_le=value)
        self.seek(16, os.SEEK_CUR)
        return id

    def read_string(self, count=0):
        """Read a short length and string value and advance the
        current position.
        """
        if count == 0:
            length = self.read_ushort()
            if length == 0:
                return ""
            if length > 512:
                raise OmniError(f'String is too long: {length}')
        else:
            length = count
        value = struct.unpack_from(f'={length}s', self.data, self.offset)[0]
        self.seek(length, os.SEEK_CUR)
        return omniscript.string_from_unicode(value)

    def read_unicode(self, count=0):
        """Read an integer length and string value and advance the
        current position.
        """
        if count == 0:
            length = self.read_uint()
            if length == 0:
                return ''
            if (length % 2) != 0:
                raise ValueError
            if length > 512:
                raise OmniError(f'Unicode String is too long: {length}')
        else:
            length = count
        data = struct.unpack_from(
            f'{(length / 2) - 1}H', self.data, self.offset)
        self.seek(length, os.SEEK_CUR)
        return ''.join(chr(u) for u in data)

    def remaining(self):
        """The number of bytes remaining in the stream."""
        remain = len(self.data) - self.offset
        return remain if remain > 0 else 0

    def seek(self, offset, wence=0):
        """Move the current position by an offset."""
        if wence == os.SEEK_SET:
            new_offset = offset
        elif wence == os.SEEK_CUR:
            new_offset = self.offset + offset
        elif wence == os.SEEK_END:
            new_offset = len(self.data) - offset
        else:
            raise OmniError('Invalid seek type.')

        if new_offset > len(self.data):
            self.offset = len(self.data)
        elif new_offset < 0:
            self.offset = 0
        else:
            self.offset = new_offset
        return self.offset

    def tell(self):
        """Returns the current position."""
        return self.offset

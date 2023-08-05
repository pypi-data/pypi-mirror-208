"""OmniError class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.


class OmniError(Exception):
    """The exception class raised by OmniScript methods.
    """

    code = 0
    """Numeric Error code."""

    message = ''
    """String message."""

    result = None
    """Optional list of result information."""

    def __init__(self, message, code=0x80004005, result=None):
        self.code = code
        self.message = message
        self.result = result

    def __str__(self):
        return repr(self.message)

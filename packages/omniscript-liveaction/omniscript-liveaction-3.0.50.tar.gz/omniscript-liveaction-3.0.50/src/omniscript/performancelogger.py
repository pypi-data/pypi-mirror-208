"""PerformanceLogger class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .peektime import PeekTime


class PerformanceRecord(object):
    def __init__(self, command):
        self.command = command
        self.start = self.end = PeekTime()

    def __str__(self):
        return (f'{self.start.iso_time()}, {self.end.iso_time()}, '
                f'{self.end - self.start}, {self.command}')

    def log_format(self):
        return (f'{self.start.iso_time()}, {self.end.iso_time()}, '
                f'{self.end - self.start}, {self.command}\n')


class PerformanceLogger(object):
    file = None
    cache = []

    def __init__(self, filename, mode='w'):
        self.file = open(filename, mode)
        self.cache = []

    def __del__(self):
        self.close()

    def __str__(self):
        return 'Performance Loggging object'

    def close(self):
        if self.file:
            self.file.writelines(m.log_format() for m in self.cache)
            self.file.close()
            self.file = None

    def perf(self, message):
        """Create a new Performance object."""
        pr = PerformanceRecord(message)
        self.cache.append(pr)
        return pr

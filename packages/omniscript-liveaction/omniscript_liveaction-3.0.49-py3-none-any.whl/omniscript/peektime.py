"""PeekTime class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import time

from datetime import datetime, timezone
from .invariant import (
    NANOSECONDS_PER_SECOND, SECONDS_PER_HOUR, SECONDS_PER_MINUTE, SECONDS_PER_DAY,
    TIME_FLAGS_NANOSECONDS)


# Convert from Ansi time (seconds) to Peek Time (nanoseconds).
ANSI_TIME_MULTIPLIER = 1000000000
# The adjustment in seconds (Ansi Time), seconds between 1/1/1601 and 1/1/1970.
ANSI_TIME_ADJUSTMENT = 11644473600

UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
PEEK_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)

UNIX_EPOCH_DELTA = 719468   # Wolfram Alpha: days between 03/01/0000 to 1/1/1601
PEEK_EPOCH_DELTA = 584694   # Wolfram Alpha: days between 03/01/0000 to 1/1/1970


class PeekTime(object):
    """Peek Time is the number of nanoseconds since
    midnight January 1, 1601.

    PeekTime(), with no arguments is set to the current date and time.
    PeekTime(int), uses the integer as the value in nanoseconds.
    PeekTime(string), either ISO 8601, or the number of nanoseconds.
    PeekTime(PeekTime), copies the value of the other PeekTime.
    """

    value = 0
    """The number of nanoseconds since January 1, 1601."""

    # Parse a 8601 Timestamp
    # _date, _time = value.split('T')
    # _year, _month, _day = _date.split('-')
    # _hour, _minute, _real = _time.split(':')
    # _seconds, _mixed = _real.split('.')
    # _fraction, _zone = _mixed.split('Z')
    # _milliseconds = int(_fraction[-9:-3])
    # _nanoseconds = int(_fraction[-9:])

    _time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, value=None):
        self.value = PeekTime.value

        if value is None:
            self.value = PeekTime.system_time_ns_to_peek_time(time.time_ns())
        elif isinstance(value, PeekTime):
            self.value = value.value
        elif isinstance(value, int):
            self.value = value if value >= 0 else 0
        elif isinstance(value, six.string_types):
            self.value = int(value) if value.isnumeric() else PeekTime.parse_8601(value)

    @classmethod
    def _decode_other(cls, other):
        """A Class method that converts various types to an
        integer value.
        """
        if isinstance(other, PeekTime):
            return other.value
        else:
            return int(other)

    @classmethod
    def days_from_date(cls, year, month, day):
        """A Class method to calculate the number of days from 1/1/1601 to
        the year, month, day supplied.
        """
        y_adj = year - (month < 3)
        quad = (y_adj if (y_adj >= 0) else (y_adj - 399)) // 400
        quad_year = abs(y_adj - (quad * 400))
        year_day = (((153 * ((month - 3) if (month > 2) else (month + 9))) + 2) // 5) + (day - 1)
        quad_day = (quad_year * 365) + (quad_year // 4) - (quad_year // 100) + year_day
        days = (quad * 146097) + quad_day - 584694
        return days

    @classmethod
    def parse_8601(cls, value):
        """A Class method that parses an ISO-8601 timestamep and returns the
        number of nanoseconds in UTC since 1/1/1601.
        """
        if not isinstance(value, six.string_types):
            raise (Exception('The value to parse must be a string.'))
        if not value:
            return 0
        if 'T' not in value:
            raise (Exception('The value must contain a "T".'))

        ns = 0
        date_secs = time_secs = 0
        _date, _remaining = value.split('T')
        if '-' in _date:
            _date_split = _date.split('-')
            if len(_date_split) != 3:
                raise (Exception('Insufficent separators in date portion.'))

            year, month, day = _date_split
            _days = PeekTime.days_from_date(int(year), int(month), int(day))
            date_secs = _days * (24 * 60 * 60)

        time_zone_minutes = 0
        if 'Z' in _remaining:
            zone_split = _remaining.split('Z')
        elif '-' in _remaining:
            zone_split = _remaining.split('-')
            time_zone_minutes = 1
        elif '+' in _remaining:
            zone_split = _remaining.split('+')
            time_zone_minutes = -1
        else:
            zone_split = [_remaining, '']

        if len(zone_split) != 2:
            raise (Exception('If a timezone offset is specified it must contain 2 parts.'))

        _full_time, time_zone = zone_split

        _full_time_split = _full_time.split('.')
        if not _full_time_split:
            raise (Exception('The time portion is missing.'))

        _time = _full_time_split[0]
        nano = _full_time_split[1] if len(_full_time_split) > 1 else '000000000'

        if ':' not in _time:
            raise (Exception('The time portion must contain colons.'))

        _time_split = _time.split(':')
        if len(_time_split) != 3:
            raise (Exception('The time portions must contains 3 parts separated by colons.'))

        hour, minute, second = _time_split
        time_secs = (int(hour) * 3600) + (int(minute) * 60) + int(second)

        nano_secs = int(nano[:9]) * pow(10, (9 - len(nano[:9])))

        tzs = 0
        if len(time_zone) > 0:
            tz_clean = time_zone.replace(':', '')
            if len(tz_clean) < 2:
                raise (Exception('Timezone offset must be at least 2 charaters.'))
            tzm = (int(tz_clean[:2]) * 60)
            if len(tz_clean) > 2:
                if len(tz_clean) != 4:
                    raise (Exception('Timezone offset must be: hhmm, hh:mm or hh.'))
                tzm += int(tz_clean[2:])
            tzs = tzm * 60
            tzs *= time_zone_minutes

        ns = (((date_secs + time_secs + tzs) * 1000000000)) + nano_secs
        return ns

    @classmethod
    def peek_time_to_system_time_ns(cls, value):
        """A Class method that converts a Peek Time value to system
        time_ns.
        """
        return value - (ANSI_TIME_ADJUSTMENT * ANSI_TIME_MULTIPLIER)

    @classmethod
    def peek_time_to_system_time(cls, value):
        """A Class method that converts a Peek Time value to
        system time.
        """
        return int(value / ANSI_TIME_MULTIPLIER) - ANSI_TIME_ADJUSTMENT

    @classmethod
    def system_time_ns_to_peek_time(cls, value):
        """A Class method that converts a system time_ns to a
        Peek Time value.
        """
        return value + (ANSI_TIME_ADJUSTMENT * ANSI_TIME_MULTIPLIER)

    @classmethod
    def system_time_to_peek_time(cls, value):
        """A Class method that converts a system time to a
        Peek Time value.
        """
        return (value + ANSI_TIME_ADJUSTMENT) * ANSI_TIME_MULTIPLIER

    def __str__(self):
        return f'{self.value}'

    def __cmp__(self, other):
        return (self.value - PeekTime._decode_other(other))

    # Rich Comparisons - otherwise __cmp__ is called.
    def __lt__(self, other):
        return (self.value < PeekTime._decode_other(other))

    def __le__(self, other):
        return (self.value <= PeekTime._decode_other(other))

    def __eq__(self, other):
        return (self.value == PeekTime._decode_other(other))

    def __ne__(self, other):
        return (self.value != PeekTime._decode_other(other))

    def __gt__(self, other):
        return (self.value > PeekTime._decode_other(other))

    def __ge__(self, other):
        return (self.value >= PeekTime._decode_other(other))

    def __hash__(self):
        return self.value

    def __add__(self, other):
        return PeekTime(self.value + PeekTime._decode_other(other))

    def __sub__(self, other):
        return PeekTime(self.value - PeekTime._decode_other(other))

    def __mul__(self, other):
        return PeekTime(self.value * PeekTime._decode_other(other))

    def from_system_time(self, value):
        """Set the PeekTime from Python System Time, which is the
        number of seconds since January 1, 1970.
        """
        self.value = PeekTime.system_time_to_peek_time(value)

    def time(self):
        """Return the PeekTime as Python System Time, which is
        the number of seconds since January 1, 1970.
        """
        systime = self.value / ANSI_TIME_MULTIPLIER
        if systime > ANSI_TIME_ADJUSTMENT:
            systime -= ANSI_TIME_ADJUSTMENT
        return systime

    def ctime(self):
        """Return the PeekTime as Python
        :class:`ctime <time.ctime>`.
        """
        return time.ctime(self.time())

    def get_date(self):
        """
        Convert the PeekTime year, month, day.

        Returns a tuple of: year, month, day.
        """

        # Find the Quadricentennial (400 years) for the date.
        # Calendars are the same within each Quadricentinnial.
        # Start the calendar at March 1, this puts leap-day at the end, much easier to deal with.
        # The year will be one off for dates in January and February, so adjust if the Jan or Feb.
        # month is 1 to 12, month_index is 0 to 11.

        peek_days = (self.value // ANSI_TIME_MULTIPLIER) // SECONDS_PER_DAY
        days = peek_days + PEEK_EPOCH_DELTA        # days from 1/3/0000 to 1/1/1601

        quad = (days if (days >= 0) else (days - 146096)) // 146097
        quad_day = int(days - (quad * 146097))
        quad_year = ((quad_day - (quad_day // 1460)
                      + (quad_day // 36524) - (quad_day // 146096)) // 365)
        year_index = quad_year + (quad * 400)
        year_day = quad_day - ((365 * quad_year) + (quad_year // 4) - (quad_year // 100))
        month_index = ((5 * year_day) + 2) // 153
        day = year_day - (((153 * month_index) + 2) // 5) + 1
        month = (month_index + 3) if (month_index < 10) else (month_index - 9)
        year = year_index + (month < 3)
        return year, month, day

    def get_time(self):
        """Convert the PeekTime to hours, minutes, seconds, nanoseconds.

        Returns a tuple of: hours, minutes, seconds and nanoseconds.
        """
        v1 = self.value // NANOSECONDS_PER_SECOND
        nanoseconds = self.value % NANOSECONDS_PER_SECOND
        # days = v1 // SECONDS_PER_DAY
        v2 = v1 % SECONDS_PER_DAY
        hours = v2 // SECONDS_PER_HOUR
        v3 = v2 % SECONDS_PER_HOUR
        minutes = v3 // SECONDS_PER_MINUTE
        seconds = v3 % SECONDS_PER_MINUTE
        return hours, minutes, seconds, nanoseconds

    def iso_time(self, flags=TIME_FLAGS_NANOSECONDS):
        """Return the PeekTime as ISO 8601 time format.
        If flags has TIME_FLAG_NANOSECONDS set then the time is extended to
        nanoseconds (9 digits).
        """
        year, month, day = self.get_date()
        hour, minute, second, nano = self.get_time()

        ns = f'{nano:09}'
        frac = ns if (flags & TIME_FLAGS_NANOSECONDS) else ns[:-3]
        text = f'{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{frac}Z'
        return text

    def days_from_epoch(self):
        days = int(int(self.value / ANSI_TIME_MULTIPLIER) / SECONDS_PER_DAY)
        days += PEEK_EPOCH_DELTA    # days from 1/3/0000 to 1/1/1601
        return days

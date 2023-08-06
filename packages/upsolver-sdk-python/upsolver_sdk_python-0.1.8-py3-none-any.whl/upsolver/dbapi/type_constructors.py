"""
Example type constructors as specified by PEP 249, returning the
appropriate Python types. For a concrete implementation, these might
return something more database specific.

"""
import datetime as dt


__all__ = [
    "Date",
    "Time",
    "Timestamp",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "Binary",
    "STRING",
    "BINARY",
    "NUMBER",
    "DATETIME",
    "ROWID",
]

# Constructor definitions.
Date = dt.date
Time = dt.time
Timestamp = dt.datetime
DateFromTicks = dt.date.fromtimestamp
TimestampFromTicks = dt.datetime.fromtimestamp


def TimeFromTicks(timestamp: float):  # pylint: disable=invalid-name
    """Return the time, given a Unix timestamp."""
    return dt.datetime.fromtimestamp(timestamp).time()


def Binary(string):
    return string.encode("utf-8")


class DBAPITypeObject:
    def __init__(self, *values):
        self.values = [v.lower() for v in values]

    def __eq__(self, other):
        return other.lower() in self.values


STRING = DBAPITypeObject("StringArrayColumnType", "StringColumnType", "JSONStringColumnType")

BINARY = DBAPITypeObject()  # nothing has binary type in Upsolver

NUMBER = DBAPITypeObject("NumberColumnType", "DoubleColumnType", "BooleanColumnType")

DATETIME = DBAPITypeObject("TimeColumnType", "DateColumnType", "UtcTimeColumnType", "LocalDateColumnType")

ROWID = DBAPITypeObject()  # nothing indicates row id in Upsolver

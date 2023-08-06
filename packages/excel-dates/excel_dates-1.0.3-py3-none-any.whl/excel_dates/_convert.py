from datetime import date, datetime, time, timedelta
from typing import Union


epoch = datetime(1899, 12, 30)
"""
Excel's 'day zero'.
"""


AnyDateType = Union[float, int, date, datetime, time]
"""
Any Python date or time or datetime object, or an Excel serial date (int) or datetime (float).
"""


def get_compensation_from_excel_to_python(value: Union[float, int]) -> int:
    """
    Get the compensation in number of days to implement the 1900 leap year bug.
    """
    if value < 60:
        return 1

    if value >= 61:
        return 0

    raise ValueError("1900/02/29 does not exist in Python")


def ensure_python_date(value: AnyDateType) -> date:
    """
    Interpret the value and return a Python date object.

    >>> ensure_python_date(10)
    datetime.date(1900, 1, 10)
    >>> ensure_python_date(10.5)
    datetime.date(1900, 1, 10)
    >>> ensure_python_date(datetime(2020, 1, 2, 3, 4, 5))
    datetime.date(2020, 1, 2)
    >>> ensure_python_date(date(2020, 1, 2))
    datetime.date(2020, 1, 2)
    >>> ensure_python_date(time(3, 4, 5))
    datetime.date(1899, 12, 30)
    """
    if isinstance(value, (float, int)):
        # The given value is an Excel date or datetime serial number.
        # Convert it, and throw away the time part.
        return (
            epoch + timedelta(days=value + get_compensation_from_excel_to_python(value))
        ).date()

    if isinstance(value, datetime):
        # Just throw away the time part.
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, time):
        # Assume Excel's "day zero".
        return epoch.date()

    raise TypeError("Failed to convert value to date.")


def ensure_python_time(value: AnyDateType) -> time:
    """
    Interpret the value and return a Python time object.

    >>> ensure_python_time(10)
    datetime.time(0, 0)
    >>> ensure_python_time(10.5)
    datetime.time(12, 0)
    >>> ensure_python_time(datetime(2020, 1, 2, 3, 4, 5))
    datetime.time(3, 4, 5)
    >>> ensure_python_time(date(2020, 1, 2))
    datetime.time(0, 0)
    >>> ensure_python_time(time(3, 4, 5))
    datetime.time(3, 4, 5)
    """
    if isinstance(value, (float, int)):
        # The given value is an Excel date or datetime serial number.
        # Convert it, and throw away the date part.
        return (epoch + timedelta(days=value)).time()

    if isinstance(value, datetime):
        # Just throw away the date part.
        return value.time()

    if isinstance(value, date):
        # Return midnight.
        return time(0, 0, 0)

    if isinstance(value, time):
        return value

    raise TypeError("Failed to convert value to date.")


def ensure_python_datetime(value: AnyDateType) -> datetime:
    """
    Interpret the value and return a Python datetime object.

    >>> ensure_python_datetime(10)
    datetime.datetime(1900, 1, 10, 0, 0)
    >>> ensure_python_datetime(10.5)
    datetime.datetime(1900, 1, 10, 12, 0)
    >>> ensure_python_datetime(datetime(2020, 1, 2, 3, 4, 5))
    datetime.datetime(2020, 1, 2, 3, 4, 5)
    >>> ensure_python_datetime(date(2020, 1, 2))
    datetime.datetime(2020, 1, 2, 0, 0)
    >>> ensure_python_datetime(time(3, 4, 5))
    datetime.datetime(1899, 12, 30, 3, 4, 5)
    """
    if isinstance(value, (float, int)):
        # The given value is an Excel date or datetime serial number.
        # Convert it.
        return epoch + timedelta(
            days=value + get_compensation_from_excel_to_python(value)
        )

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        # The given value is a date without time. Assume midnight of that day.
        return datetime.combine(value, datetime.min.time())

    if isinstance(value, time):
        # The given value is a time without date. Assume Excel's day zero.
        return datetime.combine(epoch, value)

    raise TypeError("Failed to convert value to datetime.")


def get_compensation_from_python_to_excel(value: Union[datetime, date]) -> int:
    """
    Get the compensation in number of days to implement the 1900 leap year bug.
    """
    if type(value) == date:
        value = datetime.combine(value, datetime.min.time())

    if value >= datetime(1900, 3, 1):
        return 0

    return 1


def ensure_excel_date(value: AnyDateType) -> int:
    """
    Interpret the value and return an integer, representing an Excel serial date.

    >>> ensure_excel_date(10)
    10
    >>> ensure_excel_date(10.5)
    10
    >>> ensure_excel_date(datetime(2020, 1, 2, 3, 4, 5))
    43832
    >>> ensure_excel_date(date(2020, 1, 2))
    43832
    >>> ensure_excel_date(time(3, 4, 5))
    0
    """
    if isinstance(value, (float, int)):
        # The given value is already an Excel date or datetime serial number.
        # Casting to int throws away the time and keeps the date.
        return int(value)

    if isinstance(value, datetime):
        # Get the number of whole days since Excel's day zero.
        return (value - epoch).days - get_compensation_from_python_to_excel(value)

    if isinstance(value, date):
        # Get the number of whole days since Excel's day zero.
        return (value - epoch.date()).days - get_compensation_from_python_to_excel(
            value
        )

    if isinstance(value, time):
        # There is no date, so return zero.
        return 0


def ensure_excel_datetime(value: AnyDateType) -> float:
    """
    Interpret the value and return a float, representing an Excel serial datetime.

    >>> ensure_excel_datetime(10)
    10.0
    >>> ensure_excel_datetime(10.5)
    10.5
    >>> ensure_excel_datetime(datetime(2020, 1, 2, 3, 4, 5))
    43832.12783564815
    >>> ensure_excel_datetime(date(2020, 1, 2))
    43832.0
    >>> ensure_excel_datetime(time(3, 4, 5))
    0.12783564814814816
    """
    if isinstance(value, (float, int)):
        # The given value is already an Excel date or datetime serial number.
        return float(value)

    if isinstance(value, datetime):
        # Get the fractional number of days since Excel's day zero.
        return (
            value - epoch
        ).total_seconds() / 86400.0 - get_compensation_from_python_to_excel(value)

    if isinstance(value, date):
        # Get the fractional number of days since Excel's day zero.
        return (
            value - epoch.date()
        ).total_seconds() / 86400.0 - get_compensation_from_python_to_excel(value)

    if isinstance(value, time):
        # Get the fraction of the day that has passed since midnight.
        return (value.hour * 3600 + value.minute * 60 + value.second) / 86400

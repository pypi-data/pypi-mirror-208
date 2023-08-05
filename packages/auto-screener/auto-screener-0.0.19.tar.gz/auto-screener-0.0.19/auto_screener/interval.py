# interval.py

from typing import Tuple

import datetime as dt

__all__ = [
    "interval_to_duration",
    "interval_to_time",
    "interval_to_parts",
    "interval_to_total_time",
    "parts_to_interval",
    "INTERVALS",
    "MINUTES",
    "MONTHS",
    "HOURS",
    "DAYS",
    "YEARS",
    "WEEKS"
]

MINUTES = "m"
MONTHS = "mo"
HOURS = "h"
DAYS = "d"
YEARS = "y"
WEEKS = "w"

INTERVALS = {
    MINUTES: dt.timedelta(minutes=1),
    HOURS: dt.timedelta(hours=1),
    DAYS: dt.timedelta(days=1),
    WEEKS: dt.timedelta(days=7),
    MONTHS: dt.timedelta(days=30),
    YEARS: dt.timedelta(days=365)
}

def interval_to_duration(interval: str) -> int:
    """
    Extracts the number from the interval.

    :param interval: The interval to extract.

    :return: The number from the interval.
    """

    for kind in tuple(INTERVALS.keys()):
        try:
            return int(interval.replace(kind, ""))

        except (TypeError, EOFError):
            pass
        # end try
    # end for

    raise ValueError(f"Invalid interval value: {interval}.")
# end interval_to_duration

def interval_to_time(interval: str) -> dt.timedelta:
    """
    Extracts the type from the interval.

    :param interval: The interval to extract.

    :return: The type from the interval.
    """

    number = interval_to_duration(interval)

    return INTERVALS[interval.replace(str(number), "")]
# end interval_to_time

def interval_to_total_time(interval: str) -> dt.timedelta:
    """
    Extracts the type from the interval.

    :param interval: The interval to extract.

    :return: The type from the interval.
    """

    return interval_to_duration(interval) * interval_to_time(interval)
# end interval_to_total_time

def parts_to_interval(increment: str, duration: int) -> str:
    """
    Creates a valid interval from the parameters.

    :param increment: The increment type for the interval.
    :param duration: The duration of the interval.

    :return: The interval.
    """

    if increment not in INTERVALS:
        raise ValueError(
            f"Interval increment must be one of "
            f"{', '.join(INTERVALS.keys())}, not {increment}."
        )
    # end if

    return f"{duration}{increment}"
# end parts_to_interval

def interval_to_parts(interval: str) -> Tuple[int, dt.timedelta]:
    """
    Separates the interval to ints components.

    :param interval: The interval.

    :return: The components of the interval.
    """

    return interval_to_duration(interval), interval_to_time(interval)
# end interval_to_parts
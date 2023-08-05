# hints.py

import datetime as dt
from typing import Union

__all__ = [
    "Number",
    "DateTime"
]

Number = Union[int, float]
DateTime = Union[dt.datetime, dt.date]
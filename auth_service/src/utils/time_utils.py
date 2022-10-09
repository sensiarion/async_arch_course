import calendar
import datetime
from typing import Any


def now() -> datetime.datetime:
    return datetime.datetime.utcnow()


def timestamp_to_unix(value: datetime.datetime | float | int | Any) -> float:
    if type(value) == datetime.datetime:
        value: datetime.datetime
        return calendar.timegm(value.utctimetuple())
    elif type(value) == float or type(value) == int:
        return value
    else:
        raise ValueError("Only timestamps allowed")

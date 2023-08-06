from __future__ import annotations

import datetime
from uuid import uuid4

from iso8601 import iso8601, ParseError


def uid() -> str:
    return str(uuid4()).replace("-", "")


def utcnow() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def str_to_datetime_if_parseable(value: str) -> datetime.datetime | str:
    if len(value) < 8 or value.count('-') != 2:
        return value
    try:
        ret = iso8601.parse_date(value)
    except (ParseError, ValueError, TypeError):
        ret = value
    return ret

from datetime import datetime, timezone
from datetime import tzinfo as _tzinfo
from zoneinfo import ZoneInfo

tzinfo = ZoneInfo("Europe/Moscow")


def now() -> datetime:
    return datetime.now(tz=tzinfo)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(dt: datetime) -> float:
    return dt.timestamp()


def int_timestamp(dt: datetime) -> int:
    return int(timestamp(dt))


def fromtimestamp(t: float) -> datetime:
    return datetime.fromtimestamp(t, tzinfo)


def timezone_repr(timezone: _tzinfo) -> str:
    if isinstance(timezone, ZoneInfo):
        return timezone.key
    else:
        return repr(timezone)


def is_naive(value: datetime) -> bool:
    return value.utcoffset() is None


def make_aware(value: datetime) -> datetime:
    return value.replace(tzinfo=tzinfo)


def localtime(value: datetime | None = None) -> datetime:
    if value is None:
        return now()
    if is_naive(value):
        raise ValueError("localtime() cannot be applied to a naive datetime")
    return value.astimezone(tzinfo)


def as_aware_datetime(
    v: datetime | str | None,
) -> datetime | None:
    if v is None:
        return None

    if isinstance(v, str):
        if v.upper().endswith("Z"):
            v = v[:-1] + "+00:00"

        v = datetime.fromisoformat(v)

    if not v.tzinfo:
        return v.replace(tzinfo=tzinfo)
    return v

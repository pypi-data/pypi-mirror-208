import datetime as native_datetime
import pendulum
from pendulum.helpers import get_test_now
from pendulum.helpers import has_test_now
from pendulum.tz.timezone import Timezone
from pendulum.tz import local_timezone
from pendulum.tz import UTC
import logging
import math
from tarvis.common import environ
from tarvis.common.environ import DeploymentType
import time as native_time
from typing import Optional, Union

_TIME_INTERVAL_DECIMALS = 3


def span(
    weeks: float = 0,
    days: float = 0,
    hours: float = 0,
    minutes: float = 0,
    seconds: float = 0,
    milliseconds: float = 0,
) -> float:
    return round(
        (((((((weeks * 7) + days) * 24) + hours) * 60) + minutes) * 60)
        + seconds
        + (0.001 * milliseconds),
        _TIME_INTERVAL_DECIMALS,
    )


def current_interval(timestamp: float, interval: float) -> float:
    return round(
        interval * math.floor(round(timestamp / interval, _TIME_INTERVAL_DECIMALS)),
        _TIME_INTERVAL_DECIMALS,
    )


def next_interval(timestamp: float, interval: float) -> float:
    return current_interval(timestamp + interval, interval)


def previous_interval(timestamp: float, interval: float) -> float:
    return current_interval(timestamp - interval, interval)


def closest_interval(timestamp: float, interval: float) -> float:
    return round(
        interval * round(timestamp / interval, _TIME_INTERVAL_DECIMALS),
        _TIME_INTERVAL_DECIMALS,
    )


# noinspection PyPep8Naming
class datetime(pendulum.DateTime):
    @classmethod
    def _clone(cls, dt) -> "datetime":
        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )

    # The assumption should always be UTC, not local time
    @classmethod
    def fromtimestamp(cls, t, tz=UTC) -> "datetime":
        return cls._clone(native_datetime.datetime.fromtimestamp(t, tz=tz))

    # The assumption should always be UTC, not local time
    @classmethod
    def now(cls, tz: Optional[Union[str, Timezone]] = UTC) -> "datetime":
        """
        Returns an instance for the current date and time
        (in UTC by default, unlike Pendulum).
        """
        if has_test_now():
            test_instance = get_test_now()
            # noinspection PyProtectedMember
            _tz = pendulum._safe_timezone(tz)

            if tz is not None and _tz != test_instance.timezone:
                test_instance = test_instance.in_tz(_tz)

            return cls._clone(test_instance)

        dt = cls.fromtimestamp(time(), UTC)

        if tz is None or tz == "local":
            dt = dt.in_timezone(local_timezone())
        elif tz is UTC or tz == "UTC":
            pass
        else:
            dt = dt.in_timezone(tz)

        return cls._clone(dt)

    @classmethod
    def parse(cls, text, **options) -> "datetime":
        dt = pendulum.parse(text, **options)
        return cls._clone(dt)

    def __str__(self):
        return self.to_iso8601_string()

    def next_interval(self, interval: float) -> "datetime":
        return datetime.fromtimestamp(
            next_interval(self.timestamp(), interval), self.tzinfo
        )

    def previous_interval(self, interval: float) -> "datetime":
        return datetime.fromtimestamp(
            previous_interval(self.timestamp(), interval), self.tzinfo
        )

    def current_interval(self, interval: float) -> "datetime":
        return datetime.fromtimestamp(
            current_interval(self.timestamp(), interval), self.tzinfo
        )

    def closest_interval(self, interval: float) -> "datetime":
        return datetime.fromtimestamp(
            closest_interval(self.timestamp(), interval), self.tzinfo
        )


_set = False
_start = 0
_epoch = 0
_speed = 1
_limit = None
_limit_logged = False


def set_artificial_time(
    epoch: float,
    speed: float = 1,
    allow_reset: bool = False,
    limit: float | None = None,
) -> None:
    global _set
    global _start
    global _epoch
    global _speed
    global _limit
    global _limit_logged

    if environ.deployment == DeploymentType.PRODUCTION:
        raise Exception("Artificial time in production.")

    if speed < 0:
        raise ValueError("Artificial time speed must be zero or positive.")

    if not allow_reset:
        if _set:
            raise Exception("Artificial time set more than once.")

    _set = True
    _start = native_time.time()
    _epoch = epoch
    _speed = speed
    _limit = limit
    _limit_logged = False
    start_date = datetime.fromtimestamp(_start, UTC)
    epoch_date = datetime.fromtimestamp(_epoch, UTC)

    logging.debug(
        f"Artificial time mapped from {start_date} to {epoch_date} at {speed}x speed."
    )
    if limit is not None:
        logging.debug(f"Artificial time will stop at {limit}.")


def set_artificial_datetime(
    date: datetime,
    speed: float = 1,
    allow_reset: bool = False,
    limit: datetime | None = None,
) -> None:
    if limit is not None:
        limit = limit.float_timestamp()
    set_artificial_time(date.float_timestamp(), speed, allow_reset, limit)


def time() -> float:
    global _start
    global _epoch
    global _speed
    global _limit
    global _limit_logged

    now = native_time.time()
    elapsed = (now - _start) * _speed
    artificial_time = _epoch + elapsed

    if _limit is not None:
        # noinspection PyTypeChecker
        if artificial_time > _limit:
            artificial_time = _limit
            if not _limit_logged:
                _limit_logged = True
                logging.debug("Artificial time has reached the limit.")

    if artificial_time > now:
        _start = 0
        _epoch = 0
        _speed = 1
        artificial_time = now
        logging.debug("Artificial time has reached the present.")

    return artificial_time


def sleep(secs: float) -> None:
    if secs > 0:
        if _speed == 0:
            logging.debug(f"Sleeping for {secs} seconds although time is paused.")
            native_time.sleep(secs)
        else:
            native_time.sleep(secs / _speed)


def sleep_until(wake_time: float) -> None:
    delay = wake_time - time()
    if delay > 0:
        sleep(delay)


def sleep_until_datetime(wake_datetime: native_datetime) -> None:
    sleep_until(wake_datetime.float_timestamp())

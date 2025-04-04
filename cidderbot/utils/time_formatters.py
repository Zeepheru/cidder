from datetime import datetime, timedelta, timezone
from enum import Enum


class TimeUnit(Enum):
    """Standard units of time. Use `TimeUnit.value` to get the duration in seconds."""

    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000  # 30 days
    YEAR = 31536000  # 365 days


TIMEUNIT_MAPPING = {
    TimeUnit.YEAR: {
        TimeUnit.MONTH: 12,
        TimeUnit.WEEK: 52,
        TimeUnit.DAY: 365,
        TimeUnit.HOUR: 365 * 24,
        TimeUnit.MINUTE: 365 * 24 * 60,
        TimeUnit.SECOND: 365 * 24 * 60 * 60,
    },
    TimeUnit.MONTH: {
        TimeUnit.WEEK: 4,
        TimeUnit.DAY: 30,
        TimeUnit.HOUR: 30 * 24,
        TimeUnit.MINUTE: 30 * 24 * 60,
        TimeUnit.SECOND: 30 * 24 * 60 * 60,
    },
    TimeUnit.WEEK: {
        TimeUnit.DAY: 7,
        TimeUnit.HOUR: 7 * 24,
        TimeUnit.MINUTE: 7 * 24 * 60,
        TimeUnit.SECOND: 7 * 24 * 60 * 60,
    },
    TimeUnit.DAY: {
        TimeUnit.HOUR: 24,
        TimeUnit.MINUTE: 24 * 60,
        TimeUnit.SECOND: 24 * 60 * 60,
    },
    TimeUnit.HOUR: {
        TimeUnit.MINUTE: 60,
        TimeUnit.SECOND: 60 * 60,
    },
    TimeUnit.MINUTE: {
        TimeUnit.SECOND: 60,
    },
}


def get_time_unit_mapping(time_unit_a: TimeUnit, time_unit_b: TimeUnit) -> int:
    """Returns an integer n where n is an approximate number of time_b in time_unit_a.

    Args:
        time_unit_a (TimeUnit): Smaller time unit.
        time_unit_b (TimeUnit): Larger time unit.

    Returns:
        int: Approximated integer number of time_unit_b in time_unit_a.
            Returns 0 if time_unit_a is smaller than time_unit_b.
    """

    if time_unit_a.value < time_unit_b.value:
        return 0
    if time_unit_a == time_unit_b:
        return 1

    return TIMEUNIT_MAPPING[time_unit_a][time_unit_b]


def convert_datetime_to_utc_timestamp(dt: datetime) -> float:
    # return dt.replace(tzinfo=timezone.utc).timestamp() # idk this is bugged
    return dt.timestamp()


def convert_time_unit_string(dt: datetime, unit: TimeUnit) -> str:
    """Converts a `datetime.datetime` into a formatted string, based on a given unit.

    Args:
        dt (datetime.datetime): Datetime to be converted.
        unit (TimeUnit): Unit of measurement for the date.

    Returns:
        str: Formatted time as a string.
    """

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    if unit == TimeUnit.YEAR:
        return dt.strftime("%Y")  # 1970
    if unit == TimeUnit.MONTH:
        return dt.strftime("%B %Y")  # January 1970
    if unit == TimeUnit.WEEK:
        return dt.strftime("Week %W, %Y")  # Week 00, 1970
    if unit == TimeUnit.DAY:
        return dt.strftime("%d %B %Y")  # 1 January 1970
    if unit == TimeUnit.HOUR:
        return dt.strftime("%d %B %Y, %H:00")  # 1 January 1970, 12:00
    if unit == TimeUnit.MINUTE:
        return dt.strftime("%d %B %Y, %H:%M")  # 1 January 1970, 12:42
    return dt.strftime("%d %B %Y, %H:%M:%S")  # 1 January 1970, 12:42:00


def format_timedelta(td: timedelta, length_limit: int = 3) -> str:
    """Formats a `datetime.timedelta` duration into a readable string.

    Largest time unit output is weeks.

    Args:
        td (timedelta): Duration to be formatted.
        length_limit (int, optional): Limit for number of components in the time string.
            Must be a positive integer. Defaults to 3.

    Returns:
        str: Formatted string
    """

    # Originally prompted from Deepseek R1, significantly modified.
    part_length_limit = length_limit

    # Extract days, hours, minutes, seconds from the timedelta
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    weeks, days = divmod(days, 7)

    # Create a list of formatted strings for each unit
    parts = []

    # oh gosh the repetition in this segment hurts me.
    # But if I parameterized it into a loop, it'll be painful to read...
    while True:

        if weeks > 0:
            if days >= 4 and part_length_limit == 1:
                weeks += 1

            parts.append(f"{weeks} {'week' if weeks == 1 else 'weeks'}")
            part_length_limit -= 1

        if part_length_limit == 0:
            break

        if days > 0:
            if hours >= 12 and part_length_limit == 1:
                days += 1

            parts.append(f"{days} {'day' if days == 1 else 'days'}")
            part_length_limit -= 1

        if part_length_limit == 0:
            break

        if hours > 0:
            if minutes >= 30 and part_length_limit == 1:
                hours += 1

            parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
            part_length_limit -= 1

        if part_length_limit == 0:
            break

        if minutes > 0:
            if seconds >= 30 and part_length_limit == 1:
                minutes += 1

            parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
            part_length_limit -= 1

        if part_length_limit == 0:
            break

        if seconds > 0:
            # no need for any more rounding
            parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")
            part_length_limit -= 1

        break

    # Join the parts with commas and 'and' for the last part
    if len(parts) == 0:
        return "now"
    elif len(parts) == 1:
        return parts[0]
    else:
        return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def main():
    print(format_timedelta(timedelta(seconds=90), 2))
    print(format_timedelta(timedelta(seconds=90), 1))

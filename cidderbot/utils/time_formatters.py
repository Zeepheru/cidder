from datetime import datetime, timedelta
from enum import Enum


class TimeUnit(Enum):
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000  # 30 days
    YEAR = 31536000  # 365 days


def convert_time_unit_string(dt: datetime, unit: TimeUnit) -> str:
    """Returns time as a formatted string, based on the unit given.

    Args:
        dt (datetime.datetime): _description_
        unit (TimeUnit): _description_

    Returns:
        str: Formatted time as a string.
    """

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    if unit == TimeUnit.YEAR:
        return dt.strftime("%Y")  # 1970
    elif unit == TimeUnit.MONTH:
        return dt.strftime("%B %Y")  # January 1970
    elif unit == TimeUnit.WEEK:
        return dt.strftime("Week %W, %Y")  # Week 00, 1970
    elif unit == TimeUnit.DAY:
        return dt.strftime("%w %B %Y")  # 1 January 1970
    elif unit == TimeUnit.HOUR:
        return dt.strftime("%w %B %Y, %H:00")  # 1 January 1970, 12:00
    elif unit == TimeUnit.MINUTE:
        return dt.strftime("%w %B %Y, %H:%M")  # 1 January 1970, 12:42
    return dt.strftime("%w %B %Y, %H:%M:%S")  # 1 January 1970, 12:42:00


def format_timedelta(td: timedelta) -> str:
    # Deepseek R1 :)
    part_length_limit = 4

    # Extract days, seconds, and microseconds from the timedelta
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Create a list of formatted strings for each unit
    parts = []

    if days > 0 and days < 7:
        parts.append(f"{days} {'day' if days == 1 else 'days'}")

    if hours > 0:
        parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")

    if minutes > 0:
        parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")

    if seconds > 0:
        parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

    # Handle weeks if days >= 7
    if days >= 7:
        weeks, days = divmod(days, 7)
        parts.insert(0, f"{weeks} {'week' if weeks == 1 else 'weeks'}")
        if days > 0:
            parts.insert(1, f"{days} {'day' if days == 1 else 'days'}")

    # Join the parts with commas and 'and' for the last part
    if len(parts) == 0:
        return "now"
    elif len(parts) == 1:
        return parts[0]
    else:
        parts = parts[:part_length_limit]
        return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def main():
    print(format_timedelta(timedelta(seconds=1)))
    print(format_timedelta(timedelta(seconds=12)))
    print(format_timedelta(timedelta(seconds=121)))
    print(format_timedelta(timedelta(seconds=1234)))
    print(format_timedelta(timedelta(seconds=12351)))
    print(format_timedelta(timedelta(seconds=252351)))
    print(format_timedelta(timedelta(seconds=752351)))
    print(format_timedelta(timedelta(seconds=1252351)))
    print(format_timedelta(timedelta(seconds=86400 * 2)))
    print(format_timedelta(timedelta(seconds=86400 * 6)))
    print(format_timedelta(timedelta(seconds=86400 * 8)))
    print(format_timedelta(timedelta(seconds=86400 * 15)))

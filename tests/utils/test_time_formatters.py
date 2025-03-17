from datetime import timedelta

import pytest

from cidderbot.utils.time_formatters import format_timedelta


@pytest.mark.parametrize(
    "input_td,input_len,expected",
    [
        (timedelta(seconds=0), 1, "now"),
        (timedelta(seconds=1), 1, "1 second"),
        (timedelta(seconds=2), 1, "2 seconds"),
        (timedelta(seconds=1), 2, "1 second"),
        (timedelta(seconds=90), 2, "1 minute and 30 seconds"),
        (timedelta(seconds=90), 122341222, "1 minute and 30 seconds"),
        (timedelta(seconds=90), 1, "2 minutes"),
        (timedelta(seconds=3601), 2, "1 hour and 1 second"),
        (timedelta(days=1, hours=2, minutes=3), 3, "1 day, 2 hours and 3 minutes"),
        (
            timedelta(days=15, hours=12, minutes=17),
            4,
            "2 weeks, 1 day, 12 hours and 17 minutes",
        ),
        (timedelta(days=8, seconds=1234), 1, "1 week"),
        (timedelta(days=11, seconds=1234), 1, "2 weeks"),
    ],
)
def test_format_timedelta(input_td, input_len, expected):
    assert format_timedelta(input_td, input_len) == expected

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Union, List
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import pytz

from arthurai.common.exceptions import UserValueError
from arthurai.util import generate_timestamps, normal_random_ints_fixed_sum, format_timestamp, is_valid_datetime_string

MOCK_NOW_VALUE = datetime(2020, 11, 13, tzinfo=pytz.utc)

generate_timestamp_value_cases = [
    ({'total': 8},
     np.array([1, 1, 1, 1, 1, 1, 1, 1]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 6), datetime(2020, 11, 7), datetime(2020, 11, 8), datetime(2020, 11, 9),
       datetime(2020, 11, 10), datetime(2020, 11, 11), datetime(2020, 11, 12), datetime(2020, 11, 13))]),
    ({'total': 4, 'duration': "2d"},
     np.array([1, 2, 1]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 11), datetime(2020, 11, 12), datetime(2020, 11, 12), datetime(2020, 11, 13))]),
    ({'total': 10, 'duration': "3d"},
     np.array([3, 3, 2, 2]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 10), datetime(2020, 11, 10), datetime(2020, 11, 10), datetime(2020, 11, 11),
       datetime(2020, 11, 11), datetime(2020, 11, 11), datetime(2020, 11, 12), datetime(2020, 11, 12),
       datetime(2020, 11, 13), datetime(2020, 11, 13))]),
    ({'total': 1, 'duration': "3d"}, None, UserValueError),
    ({'total': 11, 'duration': "3h", 'freq': "H"},
     np.array([3, 4, 2, 2]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 12, hour=21), datetime(2020, 11, 12, hour=21), datetime(2020, 11, 12, hour=21),
      datetime(2020, 11, 12, hour=22), datetime(2020, 11, 12, hour=22), datetime(2020, 11, 12, hour=22),
      datetime(2020, 11, 12, hour=22), datetime(2020, 11, 12, hour=23), datetime(2020, 11, 12, hour=23),
      datetime(2020, 11, 13), datetime(2020, 11, 13))]),
    ({'total': 4, 'duration': "2d", 'end': datetime(2020, 12, 13, tzinfo=pytz.utc)},
     np.array([2, 1, 1]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 12, 11), datetime(2020, 12, 11), datetime(2020, 12, 12), datetime(2020, 12, 13))]),
]


@pytest.mark.parametrize("kwargs,repeats,expected", generate_timestamp_value_cases)
def test_generate_timestamps_values(kwargs: Dict[str, Any], repeats: np.ndarray, expected: Union[List[datetime], type]):
    """
    Test that generate_timestamps() outputs match expected values for a few cases
    """
    mock_now = MagicMock()
    mock_now.return_value = MOCK_NOW_VALUE
    mock_randints = MagicMock(normal_random_ints_fixed_sum)
    mock_randints.return_value = repeats
    with patch("arthurai.util._datetime_now", mock_now):
        with patch("arthurai.util.normal_random_ints_fixed_sum", mock_randints):
            if isinstance(expected, list):
                actual = generate_timestamps(**kwargs)
                assert actual == expected
            elif issubclass(expected, Exception):
                with pytest.raises(expected):
                    generate_timestamps(**kwargs)
            else:
                raise TypeError("did not understand 'expected' value")


random_ints_cases = [
    {'num_values': 47, 'total_sum': 58730},
    {'num_values': 47, 'total_sum': 47},
    {'num_values': 13, 'total_sum': 2302},
    {'num_values': 92, 'total_sum': 50238}
]


@pytest.mark.parametrize("kwargs", random_ints_cases)
def test_normal_random_ints_fixed_sum(kwargs: Dict[str, Any]):
    np.random.seed(91)
    actual = normal_random_ints_fixed_sum(**kwargs)
    assert len(actual) == kwargs['num_values']
    assert actual.sum() == kwargs['total_sum']


def test_format_timestamp_with_no_tz_parameter():
    """Checks to make sure the handling of datetime objects/string are handled correctly"""
    timestamps = [
        datetime(2020, 8, 13, 17, 44, 31, tzinfo=timezone.utc),
        datetime(2020, 8, 13, 17, 44, 31),
        "2020-08-13T17:44:31Z",
        "2020-08-13T17:44:31",
        20200806174431,
    ]
    correct_outputs = [
        "2020-08-13T17:44:31+00:00",
        ValueError,
        "2020-08-13T17:44:31Z",
        ValueError,
        TypeError
    ]

    for count, timestamp in enumerate(timestamps):
        if correct_outputs[count] == ValueError or correct_outputs[count] == TypeError:
            with pytest.raises(correct_outputs[count]):
                format_timestamp(timestamp)
        else:
            assert format_timestamp(timestamp) == correct_outputs[count]


def test_format_timestamps_with_tz_parameter():
    """Checks to make sure the handing of datetime objects/string with timezone info"""
    timestamps = [
        (datetime(2020, 8, 13, 17, 44, 31), 'US/Eastern'),
        (datetime(2020, 8, 13, 17, 44, 31), timezone(timedelta(hours=1)))
    ]

    correct_outputs = [
        '2020-08-13T21:44:31+00:00',
        '2020-08-13T16:44:31+00:00'
    ]

    for count, t in enumerate(timestamps):
        assert format_timestamp(t[0], t[1]) == correct_outputs[count]


def test_is_valid_datetime_string():
    """Checks a few edge cases for the is_valid_datetime_string"""
    input_dates = [
        '2020-08-13T21:44:31+00:00',
        "2020-08-13T17:44:31Z",
        2020081321443514,
        [1234, 51234, 12351],
        9.1,
    ]

    correct_outputs = [
        True,
        True,
        False,
        False,
        False
    ]

    for count, date in enumerate(input_dates):
        assert is_valid_datetime_string(date) == correct_outputs[count]
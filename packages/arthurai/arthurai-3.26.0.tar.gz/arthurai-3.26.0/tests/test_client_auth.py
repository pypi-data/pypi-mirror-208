from datetime import timedelta, datetime
from typing import NamedTuple
from unittest import mock

import pytest
import pytz

from arthurai.client import auth
from arthurai.common.constants import API_PREFIX
from tests.fixtures.mocks import USER_TOKEN_JAN_1_2023_MIDNIGHT_EXPIRY

URL = "http://url"
LOGIN = "username"
PASSWORD = "password"
VERIFY_SSL = True


class AuthRefreshTestCase(NamedTuple):
    cur_time: datetime
    expected_wait_time: timedelta


CASES = [  # 2 hours to expiry: refresh in 115 minutes
         AuthRefreshTestCase(cur_time=datetime(2022, 12, 31, 22, 00, tzinfo=pytz.UTC),
                             expected_wait_time=timedelta(minutes=115)),
         # 30 min to expiry: refresh in 25 min
         AuthRefreshTestCase(cur_time=datetime(2022, 12, 31, 23, 30, tzinfo=pytz.UTC),
                             expected_wait_time=timedelta(minutes=25)),
         # 60 sec to expiry: refresh now
         AuthRefreshTestCase(cur_time=datetime(2022, 12, 31, 23, 59, tzinfo=pytz.UTC),
                             expected_wait_time=timedelta())
]


@mock.patch('arthurai.client.auth.user_login')
@mock.patch('arthurai.client.auth.datetime', wraps=datetime)
@pytest.mark.parametrize("case", CASES)
def test_refresh(mock_datetime, mock_user_login, case):
    # mock current time
    mock_datetime.now.return_value = case.cur_time
    # mock usre login
    mock_user_login.return_value = (USER_TOKEN_JAN_1_2023_MIDNIGHT_EXPIRY, {})

    # get value
    refresher = auth.AuthRefresher(url=URL, login=LOGIN, password=PASSWORD, verify_ssl=VERIFY_SSL)
    actual_header, actual_wait_time = refresher.refresh()

    # assert user login called with expected
    mock_user_login.assert_called_once_with(api_http_host=URL, api_prefix=API_PREFIX, login=LOGIN,
                                            password=PASSWORD, verify_ssl=VERIFY_SSL)
    # compare wait time to expected
    assert actual_wait_time == case.expected_wait_time
    # compare headers to expected
    assert actual_header == {"Authorization": USER_TOKEN_JAN_1_2023_MIDNIGHT_EXPIRY}

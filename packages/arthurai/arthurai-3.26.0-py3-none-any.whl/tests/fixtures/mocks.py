import logging

import pytest

from arthurai import ArthurAI


BASE_URL = "https://mock"
ACCESS_KEY = "FAKE_ACCESS_KEY"
USER_TOKEN = "fake-token"
USER_TOKEN_JAN_1_2023_MIDNIGHT_EXPIRY = \
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzI1MzEyMDB9.BM498J3ulaG6v69S6qMEz6ETWgUeXZ7dpb-ZE4VOons'


@pytest.fixture(scope="class")
def client():
    logging.info("Creating mock ArthurAI Client")

    access_key = "FAKE_ACCESS_KEY"

    config = {
        'access_key': access_key,
        'url': BASE_URL,
        'offline': True
    }
    yield ArthurAI(config)

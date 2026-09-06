import pytest

from harness.reset_db import reset_database


@pytest.fixture(scope="session", autouse=True)
def clean_database():
    reset_database()
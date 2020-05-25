import pytest

from ksmutils import Network
from ksmutils import PyTestLogger


@pytest.fixture(scope="session", autouse=True)
def network():
    n = Network(logger=PyTestLogger)
    return n

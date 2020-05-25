import pytest

from ksmutils.logging import PyTestLogger
from ksmutils.network import Network


@pytest.fixture(scope="session", autouse=True)
def network():
    n = Network(logger=PyTestLogger)
    return n

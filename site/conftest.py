import pytest

from ksmutils import Network


@pytest.fixture(scope="session", autouse=True)
def network():
    n = Network()
    return n

import pytest

from ksmutils import Kusama


@pytest.fixture(scope="session", autouse=True)
def kusama():
    kusama_obj = Kusama(
        arbitrator_key="5c65b9f9f75f95d70b84577ab07e22f7400d394ca3c8bcb227fb6d42920d9b50"
    )
    kusama_obj.connect()
    return kusama_obj

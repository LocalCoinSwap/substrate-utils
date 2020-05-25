from ksmutils import Kusama
from ksmutils import PyTestLogger


class TestVersionEndpoint:
    def test_version_check(self, network):
        kusama = Kusama(logger=PyTestLogger)
        kusama.connect(network=network)


class TestTransactionEndpoint:
    def test_basic_transaction(self, network):
        kusama = Kusama(logger=PyTestLogger)
        kusama.connect(network=network)

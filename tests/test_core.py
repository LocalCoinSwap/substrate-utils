from ksmutils.core import Kusama
from ksmutils.logging import PyTestLogger


class TestVersionEndpoint:
    def test_version_check(self, network):
        kusama = Kusama(logger=PyTestLogger)
        kusama.connect(network=network)

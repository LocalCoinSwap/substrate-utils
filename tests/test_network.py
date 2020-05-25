import unittest

from ksmutils.network import Network


class Logger:
    def __init__(self):
        self.LAST_MESSAGE = None

    def info(self, message):
        self.LAST_MESSAGE = message

    def error(self, message):
        self.LAST_MESSAGE = message

    def debug(self, message):
        self.LAST_MESSAGE = message


class TestBasicConnection(unittest.TestCase):
    def test_basic_connection(self):
        network = Network(logger=Logger)
        assert (
            network.logger.LAST_MESSAGE
            == "Instantiating network connection to wss://kusama-rpc.polkadot.io/"
        )

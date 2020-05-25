from logging import Logger

_INSTANCE = None


class Network:
    """
    The Network class manages a connection to local/remote Kusama node
    """

    def __init__(
        self,
        *,
        logger: "Logger" = Logger,
        address: str = "wss://kusama-rpc.polkadot.io/",
        **kwargs,
    ):
        global _INSTANCE
        assert _INSTANCE is None, "Network is a singleton!"
        _INSTANCE = self

        self.logger = logger()
        self.logger.info(f"Instantiating network connection to {address}")

        self._connect(**kwargs)

    def _connect(self):
        pass

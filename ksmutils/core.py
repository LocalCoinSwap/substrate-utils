from .logging import Logger
from .network import Network

BLOCKCHAIN_VERSION = 1062


class Kusama:
    def __init__(
        self,
        *,
        address: str = "wss://kusama-rpc.polkadot.io/",
        logger: "Logger" = Logger
    ):
        self.address = address
        self.logger = logger

    def connect(
        self, *, logger: "Logger" = None, address: str = "", network: "Network" = None
    ):
        logger = self.logger if not logger else logger
        address = self.address if not address else address
        if not network:
            network = Network(logger=logger, address=address)

        self.network = network
        assert self.check_version() == BLOCKCHAIN_VERSION

    def check_version(self):
        """
        Make sure the versioning of the Kusama blockchain has not been
        updated since the last developer verification of the codebase
        """
        version = self.network.node_rpc_call(
            "state_getRuntimeVersion", [], loop_limit=1
        )
        return version[0]["result"]["specVersion"]

    def unsigned_transction(self):
        pass

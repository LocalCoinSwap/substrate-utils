from scalecodec import ScaleBytes
from scalecodec.base import RuntimeConfiguration
from scalecodec.metadata import MetadataDecoder
from scalecodec.type_registry import load_type_registry_preset

from .logging import Logger
from .network import Network

# Hardcode this because we WANT things to break if it changes
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

        # WARNING: Relying on side effects to run code is dangerous, refactor this if possible
        RuntimeConfiguration().update_type_registry(
            load_type_registry_preset("default")
        )
        RuntimeConfiguration().update_type_registry(load_type_registry_preset("kusama"))

        self.metadata = self._get_metadata()
        self.spec_version = self._get_spec_version()
        self.genesis_hash = self._get_genesis_hash()

    def check_version(self):
        """
        Make sure the versioning of the Kusama blockchain has not been
        updated since the last developer verification of the codebase
        """
        version = self.network.node_rpc_call(
            "state_getRuntimeVersion", [], loop_limit=1
        )
        return version[0]["result"]["specVersion"]

    def _get_metadata(self):
        raw_metadata = self.network.node_rpc_call(
            "state_getMetadata", [None], loop_limit=1
        )[0]["result"]
        metadata = MetadataDecoder(ScaleBytes(raw_metadata))
        return metadata.decode()

    def _get_spec_version(self):
        return BLOCKCHAIN_VERSION

    def _get_genesis_hash(self):
        return self.network.node_rpc_call("chain_getBlockHash", [0], loop_limit=1)[0][
            "result"
        ]

    def _get_nonce(self, address):
        """
        NOTES:
        response = substrate.get_runtime_state(
            "System", "Account", [seller_address]
        )
        assert response.get("result")
        nonce = response["result"].get("nonce", 0)
        """
        pass

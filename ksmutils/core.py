from hashlib import blake2b

import xxhash
from scalecodec import ScaleBytes
from scalecodec.base import RuntimeConfiguration
from scalecodec.base import ScaleDecoder
from scalecodec.metadata import MetadataDecoder
from scalecodec.type_registry import load_type_registry_preset
from scalecodec.utils.ss58 import ss58_decode

from .logging import Logger
from .network import Network

# Hardcode this because we WANT things to break if it changes
BLOCKCHAIN_VERSION = 1062


class Kusama:
    def __init__(
        self,
        *,
        address: str = "wss://kusama-rpc.polkadot.io/",
        logger: "Logger" = Logger,
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

        self.metadata = self.get_metadata()
        self.spec_version = self.get_spec_version()
        self.genesis_hash = self.get_genesis_hash()

    def check_version(self):
        """
        Make sure the versioning of the Kusama blockchain has not been
        updated since the last developer verification of the codebase
        """
        version = self.network.node_rpc_call(
            "state_getRuntimeVersion", [], loop_limit=1
        )
        return version[0]["result"]["specVersion"]

    def get_metadata(self):
        raw_metadata = self.network.node_rpc_call(
            "state_getMetadata", [None], loop_limit=1
        )[0]["result"]
        metadata = MetadataDecoder(ScaleBytes(raw_metadata))
        metadata.decode()
        return metadata

    def get_spec_version(self):
        return BLOCKCHAIN_VERSION

    def get_genesis_hash(self):
        return self.network.node_rpc_call("chain_getBlockHash", [0], loop_limit=1)[0][
            "result"
        ]

    def _get_address_info(self, address):
        account_id = ss58_decode(address, 2)

        a = bytearray(xxhash.xxh64("System", seed=0).digest())
        b = bytearray(xxhash.xxh64("System", seed=1).digest())
        c = bytearray(xxhash.xxh64("Account", seed=0).digest())
        d = bytearray(xxhash.xxh64("Account", seed=1).digest())
        a.reverse()
        b.reverse()
        c.reverse()
        d.reverse()

        storage_key = f"0x{a.hex()}{b.hex()}{c.hex()}{d.hex()}"
        hashed_address = f"{blake2b(bytes.fromhex(account_id), digest_size=16).digest().hex()}{account_id}"
        storage_hash = storage_key + hashed_address

        result = self.network.node_rpc_call(
            "state_getStorageAt", [storage_hash, None], loop_limit=1
        )[0]["result"]

        return_decoder = ScaleDecoder.get_decoder_class(
            "AccountInfo<Index, AccountData>",
            ScaleBytes(result),
            metadata=self.metadata,
        )
        return return_decoder.decode()

    def get_balance(self, address):
        result = self._get_address_info(address)
        return result["data"]["free"]

    def get_nonce(self, address):
        result = self._get_address_info(address)
        return result["nonce"]
